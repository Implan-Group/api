"""Tests for the Python samples.

Run them from the folder holding `main.py`:

    python -m unittest

They need no network and no credentials. Every request goes to a scripted
transport adapter (see `tests/support.py`), so the real `ApiClient` runs its
retries, token refresh, logging, and error handling against answers that never
leave the machine.

These are not tests of the API. They cover the places where Python, `requests`,
or the samples' own plumbing could quietly do something other than what this API
needs, where a mistake produces a request that is accepted and wrong, or a failure
reported as the wrong kind of failure.
"""

import logging

# The samples' logger sets up its console and `logs/` handlers only when it has
# none. Giving it one here keeps a test run from writing to `logs/` or cluttering
# the console; the tests that need the log read it with `assertLogs`.
logging.getLogger("implan").addHandler(logging.NullHandler())
