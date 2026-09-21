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

    The body is a bare string. Anything other than `Complete` means not ready;
    `Error` and `UserCancelled` mean it stopped and will not produce results.

    A 404 is also terminal and means something specific: the run never attached to
    a project. The usual cause is a Group saved without a dollar year. Retrying
    does not help; fix the Group and run again.
    """
    raw = client.get_json(f"/api/v1/impact/status/{run_id}")
    text = str(raw).strip().strip('"')
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

    Raises on a terminal failure, on a 404 meaning the run never attached, and on a
    run that has not finished inside `timeout_seconds`.

    Poll this endpoint and not the results endpoints. The status call is cheap; the
    results endpoints are not, and reading one before the run is complete produces
    an error that looks like a different problem.
    """
    logger = logging_setup.get_logger()
    deadline = time.monotonic() + timeout_seconds
    last_status: ImpactStatus | None = None

    while True:
        try:
            status = get_impact_status(client, run_id)
        except ImplanApiError as error:
            if error.status_code == 404:
                raise RuntimeError(
                    f"Impact run {run_id} has no analyses, which means it never "
                    f"attached to the project. The usual cause is a Group saved "
                    f"without a dollar year. This is terminal: fix the Group and "
                    f"run the Project again.\n{error.problem.describe()}"
                ) from error
            raise

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
