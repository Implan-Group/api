"""Running an impact, and waiting for it.

Running is asynchronous. The POST returns a run id straight away, the analysis
takes a few minutes, and the status endpoint says when results are ready.

Wiki: Impacts - https://github.com/Implan-Group/api/wiki/Impacts
"""

import time

from models.results import ImpactStatus
from utilities import config, logging_setup
from utilities.rest import ApiClient, ImplanApiError


def run_impact(client: ApiClient, project_id: str) -> int:
    """Start an impact analysis and return its run id.

    POST /api/v1/impact/{projectId}  (wiki: Run Impact Analysis)

    The Project needs at least one Group holding at least one Event. The response
    body is the run id as a bare number, not an object.

    The run id coming back does not mean the analysis started successfully; that is
    what the status endpoint is for.
    """
    payload = client.post_json(f"/api/v1/impact/{project_id}")
    return int(payload)


def get_impact_status(client: ApiClient, run_id: int) -> ImpactStatus:
    """Read where an impact run has got to.

    GET /api/v1/impact/status/{runId}  (wiki: Get Impact Status)

    The body is a bare word such as `Complete`, sent as plain text rather than as
    JSON, so it is read as text. Anything other than `Complete` means not ready;
    `Error` and `UserCancelled` mean it stopped and will not produce results.

    A 404 means the run has no analyses. For a few seconds after a run starts
    that is normal, because the analyses are still being created; see
    `wait_for_impact`, which allows for it. A 404 that persists means the run
    never attached to a project.
    """
    text = client.get_text(f"/api/v1/impact/status/{run_id}").strip().strip('"')
    try:
        return ImpactStatus(text)
    except ValueError:
        # A status this sample has not seen. Report it rather than guessing.
        logging_setup.get_logger().debug("Unrecognized impact status %r", text)
        return ImpactStatus.UNKNOWN


def cancel_impact(client: ApiClient, run_id: int) -> str:
    """Cancel a running impact analysis.

    PUT /api/v1/impact/cancel/{runId}  (wiki: Cancel Impact)

    Useful when a run is taking far longer than expected, or when you spotted a
    mistake in the Project. Answers with a short sentence confirming the
    cancellation.
    """
    return str(client.put_json(f"/api/v1/impact/cancel/{run_id}"))


def wait_for_impact(
    client: ApiClient,
    run_id: int,
    timeout_seconds: int = config.IMPACT_TIMEOUT_SECONDS,
    poll_seconds: int = config.IMPACT_POLL_SECONDS,
) -> ImpactStatus:
    """Poll until an impact run finishes, and return its final status.

    Raises on a terminal failure, on a 404 that outlasts the start-up window, and
    on a run that has not finished inside `timeout_seconds`.

    Poll this endpoint and not the results endpoints. The status call is cheap; the
    results endpoints are not, and reading one before the run is complete produces
    an error that looks like a different problem.

    Expect a 404 on the first poll. For a few seconds after a run starts its
    analyses do not exist yet, and status answers 404 "No analyses exist" until
    they do; on INT the window was under 20 seconds. So a 404 is treated as "not
    registered yet" for the first `config.IMPACT_START_GRACE_SECONDS`, and only a
    404 that persists past that is reported as a run that never attached.
    """
    logger = logging_setup.get_logger()
    started = time.monotonic()
    deadline = started + timeout_seconds
    last_status: ImpactStatus | None = None
    said_not_registered = False

    while True:
        try:
            status = get_impact_status(client, run_id)
        except ImplanApiError as error:
            if error.status_code != 404:
                raise

            if time.monotonic() - started < config.IMPACT_START_GRACE_SECONDS:
                if not said_not_registered:
                    logger.info("  run %s: starting, not registered yet", run_id)
                    said_not_registered = True
                time.sleep(poll_seconds)
                continue

            raise RuntimeError(
                f"Impact run {run_id} still has no analyses after "
                f"{config.IMPACT_START_GRACE_SECONDS} seconds, which means it never "
                f"attached to the project. A common cause is a Group saved without a "
                f"dollar year. This is terminal: fix the Group and run the Project "
                f"again.\n{error.problem.describe()}"
            ) from error

        if status != last_status:
            last_status = status
            logger.info("  run %s: %s", run_id, status.value)

        if status is ImpactStatus.COMPLETE:
            return status

        if status.is_terminal_failure:
            raise RuntimeError(
                f"Impact run {run_id} ended with status '{status.value}'. Check the "
                f"Project's Events and Groups in IMPLAN Cloud, then run it again."
            )

        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Impact run {run_id} was still '{status.value}' after "
                f"{timeout_seconds} seconds. It may still finish; check the "
                f"Project in IMPLAN Cloud."
            )

        time.sleep(poll_seconds)
