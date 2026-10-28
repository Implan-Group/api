"""A stand-in for the network, and a client that uses it.

`requests` lets any `Session` hand its requests to a transport adapter instead of
the network. `ScriptedAdapter` is one: it answers each request with the next
outcome in its script, and an exception in the script is raised the way
`requests` raises when nothing answers.
"""

import io
from http import HTTPStatus

import requests
from requests.adapters import BaseAdapter

from utilities.rest import ApiClient

# A token-shaped value that must never show up in the log.
FAKE_TOKEN = "Bearer not.a.real.token"


def reply(
    status: int,
    body: str = "",
    content_type: str = "application/json",
    headers: dict[str, str] | None = None,
) -> tuple[int, str, dict[str, str]]:
    """One scripted answer: a status, a body, and its headers."""
    return status, body, {"Content-Type": content_type, **(headers or {})}


class ScriptedAdapter(BaseAdapter):
    """Answers each request with the next outcome in the script."""

    def __init__(self, *outcomes: tuple[int, str, dict[str, str]] | Exception) -> None:
        super().__init__()
        self._outcomes = list(outcomes)
        self.sent: list[requests.PreparedRequest] = []

    def send(self, request: requests.PreparedRequest, **kwargs) -> requests.Response:
        self.sent.append(request)
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome

        status, body, headers = outcome
        response = requests.Response()
        response.status_code = status
        response.reason = HTTPStatus(status).phrase
        response.headers.update(headers)
        response.raw = io.BytesIO(body.encode("utf-8"))
        response.encoding = "utf-8"
        response.url = request.url
        response.request = request
        return response

    def close(self) -> None:
        pass


def client_answering(
    *outcomes: tuple[int, str, dict[str, str]] | Exception,
    token_refresher=None,
) -> tuple[ApiClient, ScriptedAdapter]:
    """An `ApiClient` whose requests get these outcomes, in order."""
    adapter = ScriptedAdapter(*outcomes)
    session = requests.Session()
    session.mount("https://", adapter)
    client = ApiClient(
        token_provider=lambda: FAKE_TOKEN,
        token_refresher=token_refresher,
        base_url="https://example.invalid",
        session=session,
    )
    return client, adapter
