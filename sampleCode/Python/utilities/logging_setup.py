"""Console and file logging for the samples.

Two audiences are served here. The console gets a readable narration of what a
workflow is doing, at INFO. The log file gets the full request and response detail
at DEBUG, which is what you send to support@implan.com when something is wrong.

The `Authorization` header is redacted in both. A bearer token is a credential: it
is as good as your password for the next 24 hours, so it never reaches a console,
a log file, or a screenshot.
"""

import datetime
import json
import logging
import sys
from pathlib import Path

from requests import PreparedRequest, Response

from utilities import config

_LOGGER_NAME = "implan"

# Header names that must never be written out, compared case-insensitively.
_REDACTED_HEADERS = {"authorization", "x-api-key", "cookie", "set-cookie"}

# A response body longer than this is truncated in the log. Region and industry
# lists run to megabytes, and a log nobody can open helps nobody.
_MAX_LOGGED_BODY_CHARS = 20_000


def configure() -> logging.Logger:
    """Set up console and file logging, and return the logger the samples use.

    Calling this more than once is harmless; the handlers are only attached the
    first time.
    """
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console: the narration. Keep it short so the workflow's own story is legible.
    console = logging.StreamHandler(stream=sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(console)

    # File: everything, including full request and response bodies.
    config.LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)
    log_path = config.LOG_DIRECTORY / f"Log_{datetime.date.today():%Y%m%d}.txt"
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")
    )
    logger.addHandler(file_handler)

    logger.debug("Logging started. Full request and response detail goes to %s", log_path)
    return logger


def get_logger() -> logging.Logger:
    """Return the samples' logger, configuring it on first use."""
    return configure()


def log_path() -> Path:
    """Return today's log file path, for printing to the reader."""
    return config.LOG_DIRECTORY / f"Log_{datetime.date.today():%Y%m%d}.txt"


def heading(text: str) -> None:
    """Print a step heading to the console.

    Workflows are written as numbered steps, and these are the headings. Keeping
    them in one place means the console output of every sample looks the same.
    """
    logger = get_logger()
    logger.info("")
    logger.info(text)
    logger.info("-" * len(text))


def _redact(headers) -> dict[str, str]:
    """Copy headers, replacing the value of anything sensitive."""
    return {
        name: ("<redacted>" if name.lower() in _REDACTED_HEADERS else value)
        for name, value in (headers or {}).items()
    }


def _pretty(body: object) -> str:
    """Render a request or response body for the log, prettified when it is JSON."""
    if body is None:
        return ""
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8")
        except UnicodeDecodeError:
            return f"<{len(body)} bytes of binary content>"
    text = str(body)
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            return json.dumps(json.loads(text), indent=2)
        except ValueError:
            # Not valid JSON after all; fall through and log it as it came.
            pass
    return text


def log_exchange(
    request: PreparedRequest,
    response: Response,
    elapsed: datetime.timedelta,
) -> None:
    """Write one request and response pair to the log file.

    This is the record to attach to a support ticket. It includes the method, the
    full URL, the headers with credentials removed, both bodies, the status, and
    how long the call took.
    """
    logger = get_logger()

    lines: list[str] = [
        "--------",
        f"{request.method} {request.url}",
    ]

    for name, value in _redact(request.headers).items():
        lines.append(f"  {name}: {value}")

    if request.body:
        lines.append("  request body:")
        lines.append(_pretty(request.body))

    seconds = elapsed.total_seconds()
    lines.append(f"  -> {response.status_code} {response.reason} in {seconds:.2f}s")

    content_type = response.headers.get("Content-Type", "")
    lines.append(f"  response content-type: {content_type or '(none)'}")

    body = _pretty(response.content)
    if len(body) > _MAX_LOGGED_BODY_CHARS:
        body = (
            body[:_MAX_LOGGED_BODY_CHARS]
            + f"\n... truncated, {len(body) - _MAX_LOGGED_BODY_CHARS} more characters"
        )
    if body:
        lines.append("  response body:")
        lines.append(body)

    logger.debug("\n".join(lines))
