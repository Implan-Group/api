"""Configuration shared by every workflow.

This module holds the handful of settings the samples need and nothing else: where
the API lives, where credentials come from, where files are written, and the two
conventions (a title prefix and a dollar year) that the workflows apply to
everything they create.

Credentials are read from a `.env` file that sits next to `main.py`. That file is
listed in `.gitignore` and must never be committed. Copy `.env.example` to `.env`
and fill in the two values.

Wiki: Getting Started - https://github.com/Implan-Group/api/wiki/Getting-Started
"""

import datetime
import os
from pathlib import Path

from dotenv import load_dotenv

# The root of this sample, which is the folder holding `main.py`. Every other path
# is derived from it so the samples behave the same no matter which directory you
# start them from.
SAMPLE_ROOT: Path = Path(__file__).resolve().parents[1]

# Load `.env` into the process environment. `load_dotenv` leaves any variable that
# is already set alone, so an environment variable exported in your shell or set by
# a CI system wins over the file.
load_dotenv(SAMPLE_ROOT / ".env")

# Every endpoint in these samples is served from this host. Authentication lives at
# `/api/auth`; everything else is under `/api/v1/`.
BASE_URL: str = os.getenv("IMPLAN_API_URL", "https://api.implan.com").rstrip("/")

# Your IMPLAN sign-in. These are the same credentials you use at app.implan.com,
# and your subscription must include API access. Contact support@implan.com if a
# login that works in the browser is refused here.
USERNAME: str | None = os.getenv("IMPLAN_USERNAME")
PASSWORD: str | None = os.getenv("IMPLAN_PASSWORD")

# Where the bearer token is cached between runs. A token is good for 24 hours, and
# asking for a new one on every run risks a temporary ban, so the samples always
# reuse this file when the token in it still works.
TOKEN_CACHE_PATH: Path = SAMPLE_ROOT / "implan_auth.jwt"

# Request and response logs are appended here, one file per day.
LOG_DIRECTORY: Path = SAMPLE_ROOT / "logs"

# Exported CSV reports and other downloads land here.
REPORTS_DIRECTORY: Path = SAMPLE_ROOT / "reports"

# Input files that ship with the samples (the bulk-import CSVs, for example).
DATA_DIRECTORY: Path = SAMPLE_ROOT / "data"

# Everything these samples create in your IMPLAN account is named with this prefix
# so you can find it later and delete it. Projects, events, groups, and combined
# regions all use it.
TITLE_PREFIX: str = "ImpactApi Sample"

# How long a workflow waits for a long-running operation before giving up. An
# impact usually finishes in a couple of minutes and a combined-region build in
# under one, so these are generous.
IMPACT_TIMEOUT_SECONDS: int = 15 * 60
IMPACT_POLL_SECONDS: int = 15
REGION_BUILD_TIMEOUT_SECONDS: int = 10 * 60
REGION_BUILD_POLL_SECONDS: int = 15

# How long to wait for a single HTTP request before treating it as failed. The
# gateway itself times out at 30 seconds, so anything longer than this is a network
# problem rather than a slow endpoint.
REQUEST_TIMEOUT_SECONDS: float = 60.0


def current_dollar_year() -> int:
    """Return the dollar year the samples use, which is the current calendar year.

    Dollar Year is the year the results are expressed in; Data Year is the year of
    the underlying IMPLAN dataset. They are different things and often differ. The
    samples use the current year so they never go stale, and every Group they
    create carries it explicitly, because the API has no default: a Group saved
    without a dollar year produces an impact run that never attaches.

    Support: Which Year Is It Anyway? Data Year, Model Year, and Dollar Year
    https://support.implan.com/hc/en-us/articles/360039290593
    """
    return datetime.date.today().year


def unique_title(label: str) -> str:
    """Build a title that is unique per run and easy to find in IMPLAN Cloud.

    Titles must be unique for your user, and the API rejects an ampersand and the
    characters `| ; % * ? ! = ' " ^ #`, so keep `label` to plain words.
    """
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{TITLE_PREFIX} - {label} - {stamp}"


def require_credentials() -> tuple[str, str]:
    """Return the username and password, or explain exactly what is missing.

    Every workflow calls this before its first request so a missing `.env` fails
    immediately with a useful message rather than as a confusing 401 later.
    """
    if not USERNAME or not PASSWORD:
        raise RuntimeError(
            "IMPLAN credentials are not set.\n"
            f"Copy {SAMPLE_ROOT / '.env.example'} to {SAMPLE_ROOT / '.env'} and fill in\n"
            "IMPLAN_USERNAME and IMPLAN_PASSWORD, or set them as environment variables."
        )
    return USERNAME, PASSWORD
