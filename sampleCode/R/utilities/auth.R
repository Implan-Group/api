# Authentication and the token cache.
#
# The caching pattern every IMPLAN sample follows, in any language:
#
#   1. If a cached token file exists, read it and verify it with one cheap call.
#   2. If that works, use it. A token is valid for 24 hours.
#   3. Only if there is no file, or the token in it has expired, post the
#      credentials and write the new token to the file.
#
# The caching is not an optimization, it is a requirement. Authenticating on
# every run is unnecessary, unsupported, and repeated requests in a short period
# can earn a temporary ban on the account.
#
# The token itself is never printed or logged. Treat it exactly as you would the
# password that produced it.
#
# Wiki: Authentication - https://github.com/Implan-Group/api/wiki/Authentication
# Support: How to Use the IMPLAN API with R: Obtaining Your API Token
# https://support.implan.com/hc/en-us/articles/48279952909467


# A small, fast, always-available endpoint used only to answer "is this token
# still good?". It returns a handful of strings, so verifying costs almost
# nothing.
VERIFY_PATH <- "/api/v1/region/RegionTypes"


# Raised when a token cannot be obtained or the credentials are refused.
authentication_error <- function(message) {
  structure(
    class = c("implan_authentication_error", "error", "condition"),
    list(message = message, call = NULL)
  )
}


# Returns the token saved by an earlier run, or NULL if there is not one.
read_cached_token <- function() {
  path <- token_cache_path()
  if (!file.exists(path)) {
    return(NULL)
  }

  token <- trimws(paste(readLines(path, warn = FALSE), collapse = ""))
  if (nzchar(token)) token else NULL
}


# Saves a token for the next run.
#
# The file is gitignored (`*.jwt`). It holds a live credential, so keep it out of
# source control, shared folders, and screenshots.
write_cached_token <- function(token) {
  writeLines(token, token_cache_path())
  invisible(token)
}


# Checks a cached token with one inexpensive authenticated request.
is_token_valid <- function(token) {
  status <- tryCatch(
    {
      resp <- request(paste0(implan_base_url(), VERIFY_PATH)) |>
        req_user_agent(USER_AGENT) |>
        req_timeout(REQUEST_TIMEOUT_SECONDS) |>
        req_auth_bearer_token(bare_token(token)) |>
        req_error(is_error = function(resp) FALSE) |>
        req_perform()
      resp_status(resp)
    },
    error = function(condition) {
      # Network trouble tells us nothing about the token. Treat it as invalid so
      # the caller takes the fresh-token path and gets a clearer error there.
      NA_integer_
    }
  )

  identical(as.integer(status), 200L)
}


# Authenticates with username and password and returns a fresh bearer token.
#
# POST /api/auth  (wiki: Authentication)
#
# The request body is a JSON object with lowercase `username` and `password`. The
# response body is the token, already carrying its `Bearer ` prefix, so it goes
# into the `Authorization` header exactly as received.
fetch_new_token <- function() {
  credentials <- require_credentials()

  resp <- tryCatch(
    request(paste0(implan_base_url(), "/api/auth")) |>
      req_user_agent(USER_AGENT) |>
      req_timeout(REQUEST_TIMEOUT_SECONDS) |>
      req_body_json(
        list(username = credentials$username, password = credentials$password),
        auto_unbox = TRUE
      ) |>
      req_error(is_error = function(resp) FALSE) |>
      req_perform(),
    httr2_failure = function(condition) {
      stop(implan_transport_error(implan_base_url(), condition))
    }
  )

  status <- resp_status(resp)

  if (status == 200L) {
    token <- trimws(resp_body_string(resp))
    if (!nzchar(token)) {
      stop(authentication_error("The auth endpoint returned an empty token."))
    }

    # The API already prefixes the token, but a proxy that trimmed it would
    # produce a confusing 401 later, so make sure of it here.
    if (!startsWith(token, "Bearer ")) {
      token <- paste("Bearer", token)
    }

    write_cached_token(token)
    log_debug(paste("Authenticated and cached a new token at", token_cache_path()))
    return(token)
  }

  problem <- problem_details(resp)

  if (status == 503L) {
    # Two different causes, and the fix differs. See the support article named at
    # the top of this file.
    stop(authentication_error(paste0(
      "The authentication service answered 503 Service Unavailable.\n",
      "That is either a brief outage, in which case waiting a minute and\n",
      "running again usually works, or API access has not been enabled on\n",
      "your account, in which case your Customer Success Manager has to turn\n",
      "it on. Repeat 503s point to the second.\n",
      describe(problem)
    )))
  }

  if (status %in% c(400L, 401L, 403L)) {
    stop(authentication_error(paste0(
      "IMPLAN refused those credentials.\n",
      "Check IMPLAN_USERNAME and IMPLAN_PASSWORD in your .env file; they are\n",
      "the same ones you use at app.implan.com, and your subscription must\n",
      "include API access.\n",
      describe(problem)
    )))
  }

  stop(authentication_error(paste0("Could not authenticate.\n", describe(problem))))
}


# Returns a usable bearer token, reusing the cached one while it still works.
get_bearer_token <- function() {
  cached <- read_cached_token()

  if (!is.null(cached)) {
    if (is_token_valid(cached)) {
      log_debug("Reusing the cached bearer token")
      return(cached)
    }
    log_debug("The cached token has expired; requesting a new one")
  }

  fetch_new_token()
}


# Builds the API client the workflows use.
#
# The client asks for the token lazily and can refresh it once if a request comes
# back 401 part way through a run, which matters for a bulk workflow that runs
# for longer than the token's lifetime. The token lives in an environment so that
# a refresh is seen by every later call rather than only by the one that
# triggered it.
create_client <- function() {
  holder <- new.env(parent = emptyenv())
  holder$token <- NULL

  provide_token <- function() {
    if (is.null(holder$token)) {
      holder$token <- get_bearer_token()
    }
    holder$token
  }

  refresh_token <- function() {
    holder$token <- fetch_new_token()
    holder$token
  }

  api_client(token_provider = provide_token, token_refresher = refresh_token)
}
