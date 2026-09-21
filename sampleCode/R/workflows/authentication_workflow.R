# Workflow 1: Authentication.
#
# Goal: get a bearer token, cache it, and prove it works.
#
# Every other workflow depends on this one. Run it first, and run it again
# whenever you want to check that your credentials and subscription are in order
# without creating anything in your account.
#
# The point of the workflow is the caching. A token lasts 24 hours, and asking
# for a new one on every run is unnecessary, unsupported, and can get an account
# temporarily banned. So: read the cached token, verify it cheaply, and only
# authenticate when there is nothing usable on disk.
#
# Wiki: Authentication - https://github.com/Implan-Group/api/wiki/Authentication


authentication_workflow <- function() {
  # Step 1. Check that credentials are available before touching the network, so
  # a missing `.env` fails with an explanation rather than a 401.
  log_heading("Step 1: read credentials")
  credentials <- require_credentials()
  log_info("  signing in as %s", credentials$username)
  log_info("  credentials came from %s", file.path(implan_root(), ".env"))

  # Step 2. Get a token. This reuses the cached one when it still works and only
  # calls POST /api/auth when it does not, which is the pattern to copy.
  log_heading("Step 2: get a bearer token")
  had_cache <- file.exists(token_cache_path())
  get_bearer_token()

  if (had_cache) {
    log_info("  a cached token was already on disk and was checked before reuse")
  } else {
    log_info("  no cached token, so one was requested and saved")
  }
  log_info("  token cache: %s", token_cache_path())
  log_info("  the token itself is never printed or logged")

  # Step 3. Make one real authenticated call. Region Types is the cheapest
  # endpoint in the API, which is why it is the one used to test a token.
  log_heading("Step 3: confirm the token is accepted")
  client <- create_client()

  # GET /api/v1/region/RegionTypes  (wiki: Get Region Types)
  region_types <- get_region_types(client)
  log_info("  the API answered with %d region types:", length(region_types))
  log_info("    %s", paste(region_types, collapse = ", "))

  log_heading("Done")
  log_info("Authentication works. Every other workflow can now run.")
  log_info("Run this workflow again and step 2 will reuse the cached token.")
  log_info("Full request and response detail: %s", log_file_path())

  invisible(NULL)
}
