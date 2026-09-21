"""Authentication and the token cache.

This is the reference implementation of the caching pattern every IMPLAN sample
follows, in any language:

1. If a cached token file exists, read it and verify it with one cheap call.
2. If that works, use it. A token is valid for 24 hours.
3. Only if there is no file, or the token in it has expired, post the credentials
   and write the new token to the file.

The caching is not an optimization, it is a requirement. Authenticating on every
run is unnecessary, unsupported, and repeated requests in a short period can earn
a temporary ban on the account.

The token itself is never printed or logged. Treat it exactly as you would the
password that produced it.

Wiki: Authentication - https://github.com/Implan-Group/api/wiki/Authentication
Support: How to Use the IMPLAN API with R: Obtaining Your API Token
https://support.implan.com/hc/en-us/articles/48279952909467
"""

import requests

from utilities import config, logging_setup
from utilities.rest import ApiClient, ProblemDetails

# A small, fast, always-available endpoint used only to answer "is this token still
# good?". It returns a handful of strings, so verifying costs almost nothing.
_VERIFY_PATH = "/api/v1/region/RegionTypes"


class AuthenticationError(RuntimeError):
    """Raised when a token cannot be obtained or the credentials are refused."""


def _read_cached_token() -> str | None:
    """Return the token saved by an earlier run, or `None` if there is not one."""
    if not config.TOKEN_CACHE_PATH.exists():
        return None
    token = config.TOKEN_CACHE_PATH.read_text(encoding="utf-8").strip()
    return token or None


def _write_cached_token(token: str) -> None:
    """Save a token for the next run.

    The file is listed in `.gitignore` (`*.jwt`). It holds a live credential, so
    keep it out of source control, shared folders, and screenshots.
    """
    config.TOKEN_CACHE_PATH.write_text(token, encoding="utf-8")


def _is_token_valid(token: str) -> bool:
    """Check a cached token with one inexpensive authenticated request."""
    try:
        response = requests.get(
            f"{config.BASE_URL}{_VERIFY_PATH}",
            headers={"Authorization": token},
            timeout=config.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        # Network trouble tells us nothing about the token. Treat it as invalid so
        # the caller takes the fresh-token path and gets a clearer error there.
        return False
    return response.status_code == 200


def fetch_new_token() -> str:
    """Authenticate with username and password and return a fresh bearer token.

    POST /api/auth  (wiki: Authentication)

    The request body is a JSON object with lowercase `username` and `password`. The
    response body is the token, already carrying its `Bearer ` prefix, so it goes
    into the `Authorization` header exactly as received.
    """
    username, password = config.require_credentials()
    logger = logging_setup.get_logger()

    url = f"{config.BASE_URL}/api/auth"
    response = requests.post(
        url,
        json={"username": username, "password": password},
        timeout=config.REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code == 200:
        response.encoding = "utf-8"
        token = response.text.strip()
        if not token:
            raise AuthenticationError("The auth endpoint returned an empty token.")
        # The API already prefixes the token, but a proxy that trims it would
        # produce a confusing 401 later, so make sure of it here.
        if not token.startswith("Bearer "):
            token = f"Bearer {token}"
        _write_cached_token(token)
        logger.debug("Authenticated and cached a new token at %s", config.TOKEN_CACHE_PATH)
        return token

    problem = ProblemDetails.from_response(response)

    if response.status_code == 503:
        # Two different causes, and the fix differs. See the support article named
        # in this module's docstring.
        raise AuthenticationError(
            "The authentication service answered 503 Service Unavailable.\n"
            "That is either a brief outage, in which case waiting a minute and\n"
            "running again usually works, or API access has not been enabled on\n"
            "your account, in which case your Customer Success Manager has to turn\n"
            f"it on. Repeat 503s point to the second.\n{problem.describe()}"
        )

    if response.status_code in (400, 401, 403):
        raise AuthenticationError(
            "IMPLAN refused those credentials.\n"
            "Check IMPLAN_USERNAME and IMPLAN_PASSWORD in your .env file; they are\n"
            "the same ones you use at app.implan.com, and your subscription must\n"
            f"include API access.\n{problem.describe()}"
        )

    raise AuthenticationError(f"Could not authenticate.\n{problem.describe()}")


def get_bearer_token() -> str:
    """Return a usable bearer token, reusing the cached one whenever it still works."""
    logger = logging_setup.get_logger()

    cached = _read_cached_token()
    if cached is not None:
        if _is_token_valid(cached):
            logger.debug("Reusing the cached bearer token")
            return cached
        logger.debug("The cached token has expired; requesting a new one")

    return fetch_new_token()


def create_client() -> ApiClient:
    """Build the API client the workflows use.

    The client asks for the token lazily and can refresh it once if a request comes
    back 401 mid-run, which matters for a bulk workflow that runs for longer than
    the token's lifetime.
    """
    token_holder: dict[str, str] = {}

    def provide_token() -> str:
        if "token" not in token_holder:
            token_holder["token"] = get_bearer_token()
        return token_holder["token"]

    def refresh_token() -> str:
        token_holder["token"] = fetch_new_token()
        return token_holder["token"]

    return ApiClient(token_provider=provide_token, token_refresher=refresh_token)
