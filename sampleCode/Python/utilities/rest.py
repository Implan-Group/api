"""The HTTP client every endpoint module uses.

One class, `ApiClient`, is responsible for everything that is the same on every
call: attaching the bearer token, logging the exchange, turning an error response
into a Python exception you can read, backing off when the API asks you to, and
refreshing an expired token once before giving up.

Errors deserve a word. Every failure from this API comes back as a problem-details
document (RFC 9457) with a `title`, a `detail`, and a `traceId`. Those three fields
are the difference between "something went wrong" and knowing what to fix, so this
client raises them as an `ImplanApiError` rather than letting a failed call return
`None` and break somewhere else with a confusing message.

Wiki: Requests - https://github.com/Implan-Group/api/wiki/Requests
Wiki: Responses - https://github.com/Implan-Group/api/wiki/Responses
"""

import dataclasses
import datetime
import json
import random
import time
from collections import deque
from typing import Any, Callable, Mapping, Sequence

import requests

from utilities import config, logging_setup

# Statuses worth trying again. 429 means the rate limit was hit; the 5xx family
# here means the service was briefly unavailable rather than that the request was
# wrong. A 503 from the auth endpoint in particular is usually transient.
_RETRY_STATUSES = frozenset({429, 502, 503, 504})

_MAX_ATTEMPTS = 4


@dataclasses.dataclass(frozen=True)
class ProblemDetails:
    """The body the API returns with any error, per RFC 9457.

    `trace_id` is the one to quote when reporting a problem to IMPLAN support: it
    identifies the exact request in their logs.
    """

    status: int
    title: str
    detail: str
    trace_id: str | None = None
    type: str | None = None
    instance: str | None = None

    @classmethod
    def from_response(cls, response: requests.Response) -> "ProblemDetails":
        """Read problem details out of a response, whatever shape it arrived in."""
        title = response.reason or "Request failed"
        detail = ""
        trace_id = None
        problem_type = None
        instance = None

        try:
            body = response.json()
        except ValueError:
            # Not JSON at all: a gateway error page, or an empty body. Use whatever
            # text came back so the reader is not left with nothing.
            detail = (response.text or "").strip()[:1000]
        else:
            if isinstance(body, dict):
                title = body.get("title") or title
                detail = body.get("detail") or ""
                trace_id = body.get("traceId") or body.get("trace_id")
                problem_type = body.get("type")
                instance = body.get("instance")
            else:
                detail = str(body)[:1000]

        return cls(
            status=response.status_code,
            title=title,
            detail=detail,
            trace_id=trace_id,
            type=problem_type,
            instance=instance,
        )

    def describe(self) -> str:
        """One readable block, suitable for a console message or a support ticket."""
        lines = [f"{self.status} {self.title}"]
        if self.detail:
            lines.append(f"  {self.detail}")
        if self.trace_id:
            lines.append(f"  traceId: {self.trace_id}")
        return "\n".join(lines)


class ImplanApiError(RuntimeError):
    """Raised when the API answers with an error.

    Catch this to handle an expected failure, for example a 409 when a title is
    already taken. `error.problem.status` is the status code and
    `error.problem.detail` is the API's explanation.
    """

    def __init__(self, method: str, url: str, problem: ProblemDetails) -> None:
        super().__init__(f"{method} {url}\n{problem.describe()}")
        self.method = method
        self.url = url
        self.problem = problem

    @property
    def status_code(self) -> int:
        return self.problem.status


class RateLimiter:
    """Keeps a category of requests under a published per-minute limit.

    The API publishes limits per group of endpoints, and exceeding one earns a
    `429 Too Many Requests` and, if you keep going, a temporary ban. The bulk
    workflows switch this on so that a loop over thousands of regions stays
    polite; the short workflows do not need it.

    Limits are on the wiki home page:
    https://github.com/Implan-Group/api/wiki
    """

    def __init__(self, requests_per_minute: int) -> None:
        self.requests_per_minute = requests_per_minute
        self._timestamps: deque[float] = deque()

    def wait(self) -> None:
        """Block until another request would be within the limit."""
        now = time.monotonic()
        # Forget anything that happened more than a minute ago.
        while self._timestamps and now - self._timestamps[0] >= 60.0:
            self._timestamps.popleft()

        if len(self._timestamps) >= self.requests_per_minute:
            sleep_for = 60.0 - (now - self._timestamps[0]) + 0.1
            if sleep_for > 0:
                logging_setup.get_logger().debug(
                    "Rate limit: waiting %.1fs to stay under %d requests per minute",
                    sleep_for,
                    self.requests_per_minute,
                )
                time.sleep(sleep_for)

        self._timestamps.append(time.monotonic())


class ApiClient:
    """Sends authenticated requests to the Impact API.

    Build one of these with `utilities.auth.create_client()` rather than directly,
    so the token cache is wired up for you.
    """

    def __init__(
        self,
        token_provider: Callable[[], str],
        token_refresher: Callable[[], str] | None = None,
        base_url: str = config.BASE_URL,
    ) -> None:
        self._token_provider = token_provider
        self._token_refresher = token_refresher
        self.base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._logger = logging_setup.get_logger()
        # Set by the bulk workflows; `None` means no client-side throttling.
        self.rate_limiter: RateLimiter | None = None

    # -- the request that every other method goes through --------------------

    def _send(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any | None = None,
        files: Mapping[str, Any] | None = None,
        expected_statuses: Sequence[int] = (200, 201, 202, 204),
    ) -> requests.Response:
        """Send one request, retrying transient failures, and raise on an error.

        `json_body` is serialized and sent as the request body. It is allowed on a
        GET, which sounds wrong but is what a few of this API's report endpoints
        require; see `endpoints.impact_results.get_estimated_growth_percentage`.
        """
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        body = json.dumps(json_body) if json_body is not None else None

        last_problem: ProblemDetails | None = None

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            if self.rate_limiter is not None:
                self.rate_limiter.wait()

            headers = {"Authorization": self._token_provider()}
            if body is not None:
                headers["Content-Type"] = "application/json"

            request = requests.Request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=body,
                files=files,
            )
            prepared = self._session.prepare_request(request)

            started = datetime.datetime.now()
            response = self._session.send(
                prepared, timeout=config.REQUEST_TIMEOUT_SECONDS
            )
            elapsed = datetime.datetime.now() - started

            logging_setup.log_exchange(prepared, response, elapsed)

            if response.status_code in expected_statuses:
                return response

            problem = ProblemDetails.from_response(response)
            last_problem = problem

            # An expired token looks like a 401. Refresh once and try again; if the
            # second attempt also fails, the credentials or the subscription are
            # the problem, not the token.
            if (
                response.status_code == 401
                and self._token_refresher is not None
                and attempt == 1
            ):
                self._logger.debug("401 received; refreshing the bearer token and retrying")
                self._token_refresher()
                continue

            if response.status_code in _RETRY_STATUSES and attempt < _MAX_ATTEMPTS:
                delay = self._retry_delay(response, attempt)
                self._logger.info(
                    "  %s from the API; waiting %.0fs and trying again (attempt %d of %d)",
                    response.status_code,
                    delay,
                    attempt + 1,
                    _MAX_ATTEMPTS,
                )
                time.sleep(delay)
                continue

            raise ImplanApiError(method, url, problem)

        # Every attempt was a retryable failure.
        raise ImplanApiError(method, url, last_problem)  # type: ignore[arg-type]

    @staticmethod
    def _retry_delay(response: requests.Response, attempt: int) -> float:
        """How long to wait before trying again.

        The API's `Retry-After` header wins when it is present. Otherwise back off
        exponentially with a little randomness, so that a batch of parallel scripts
        does not retry in lockstep.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        return min(60.0, (2.0**attempt) + random.uniform(0, 1))

    # -- typed helpers the endpoint modules call -----------------------------

    def get_json(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any | None = None,
    ) -> Any:
        """GET a JSON document."""
        return self._send("GET", path, params=params, json_body=json_body).json()

    def get_text(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_body: Any | None = None,
    ) -> str:
        """GET a text document, which for this API means a CSV report.

        The response is decoded as UTF-8 text. Write it to a file with a `.csv`
        extension and it opens in Excel or Sheets.
        """
        response = self._send("GET", path, params=params, json_body=json_body)
        # `requests` guesses an encoding from the headers and guesses badly for
        # `text/csv`; the API sends UTF-8, so say so before reading `.text`.
        response.encoding = response.encoding or "utf-8"
        return response.text

    def get_bytes(
        self, path: str, *, params: Mapping[str, Any] | None = None
    ) -> bytes:
        """GET a binary document, such as a zipped export."""
        return self._send("GET", path, params=params).content

    def post_json(
        self,
        path: str,
        *,
        json_body: Any | None = None,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """POST a JSON body and read a JSON response.

        A few endpoints answer with a bare number or an empty body rather than an
        object, so an unparseable response comes back as raw text instead of
        raising.
        """
        response = self._send("POST", path, params=params, json_body=json_body)
        return _json_or_text(response)

    def post_file(self, path: str, *, field_name: str, file_path) -> Any:
        """POST a file as multipart form data, for the Event Template upload."""
        with open(file_path, "rb") as handle:
            files = {field_name: (file_path.name, handle)}
            response = self._send("POST", path, files=files)
        return _json_or_text(response)

    def put_json(self, path: str, *, json_body: Any | None = None) -> Any:
        """PUT a JSON body and read whatever comes back."""
        return _json_or_text(self._send("PUT", path, json_body=json_body))

    def patch_json(self, path: str, *, json_body: Any | None = None) -> Any:
        """PATCH a JSON body and read whatever comes back."""
        return _json_or_text(self._send("PATCH", path, json_body=json_body))

    def delete(self, path: str) -> None:
        """DELETE a resource. The API returns no body worth reading."""
        self._send("DELETE", path)


def _json_or_text(response: requests.Response) -> Any:
    """Return the response as JSON when it is JSON, and as trimmed text otherwise.

    `POST /api/v1/impact/{projectId}` answers with a bare run id, and
    `PUT /api/v1/impact/cancel/{runId}` answers with a sentence, so neither is a
    JSON object. Both still need reading.
    """
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text.strip().strip('"')
