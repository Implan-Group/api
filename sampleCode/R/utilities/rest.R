# The HTTP client every endpoint file uses.
#
# One place is responsible for everything that is the same on every call:
# attaching the bearer token, logging the exchange, turning an error response
# into an R condition you can read, backing off when the API asks you to, and
# refreshing an expired token once before giving up.
#
# Errors deserve a word. Every failure from this API comes back as a
# problem-details document (RFC 9457) with a `title`, a `detail`, and a
# `traceId`. Those three fields are the difference between "something went wrong"
# and knowing what to fix, so this client raises them as an `implan_api_error`
# condition rather than letting a failed call return NULL and break somewhere
# else with a confusing message.
#
# Most of the work is done by httr2's own policies rather than by hand:
#
#   req_auth_bearer_token()  attaches the token and redacts it when a request is
#                            printed
#   req_retry()              waits and tries again on 429 and the transient 5xx,
#                            honouring Retry-After when the API sends one
#   req_error()              puts the problem details into the R error message
#   req_throttle()           keeps the bulk workflows inside the published limits
#
# Wiki: Requests - https://github.com/Implan-Group/api/wiki/Requests
# Wiki: Responses - https://github.com/Implan-Group/api/wiki/Responses

library(httr2)
library(jsonlite)


# Statuses worth trying again. 429 means the rate limit was hit; the 5xx family
# here means the service was briefly unavailable rather than that the request was
# wrong.
RETRY_STATUSES <- c(429L, 502L, 503L, 504L)

MAX_ATTEMPTS <- 4L

# Sent on every request, so IMPLAN can tell sample traffic apart in their logs.
USER_AGENT <- "implan-impact-api-samples-r"


# The body the API returns with any error, per RFC 9457.
#
# `trace_id` is the one to quote when reporting a problem to IMPLAN support: it
# identifies the exact request in their logs.
problem_details <- function(resp) {
  status <- resp_status(resp)
  title <- resp_status_desc(resp)
  detail <- ""
  trace_id <- NULL

  body <- tryCatch(resp_body_string(resp), error = function(condition) "")

  parsed <- if (nzchar(trimws(body))) {
    tryCatch(fromJSON(body, simplifyVector = FALSE), error = function(condition) NULL)
  } else {
    NULL
  }

  if (is.list(parsed)) {
    if (!is.null(parsed$title)) title <- parsed$title
    if (!is.null(parsed$detail)) detail <- parsed$detail
    if (!is.null(parsed$traceId)) trace_id <- parsed$traceId
  } else {
    # Not JSON at all: a gateway error page, or an empty body. Use whatever text
    # came back so the reader is not left with nothing.
    detail <- substr(trimws(body), 1, 1000)
  }

  structure(
    list(status = status, title = title, detail = detail, trace_id = trace_id),
    class = "implan_problem"
  )
}


# One readable block, for a console message or a support ticket.
describe.implan_problem <- function(x, ...) {
  lines <- sprintf("%d %s", x$status, x$title)
  if (nzchar(x$detail)) {
    lines <- c(lines, paste0("  ", x$detail))
  }
  if (!is.null(x$trace_id)) {
    lines <- c(lines, paste0("  traceId: ", x$trace_id))
  }
  paste(lines, collapse = "\n")
}


# Raised when the API answers with an error.
#
# Catch it with tryCatch(..., implan_api_error = function(cnd) ...) to handle an
# expected failure, for example a 409 when a title is already taken.
# `cnd$status` is the status code and `cnd$problem$detail` is the API's
# explanation.
implan_api_error <- function(method, url, problem) {
  structure(
    class = c("implan_api_error", "error", "condition"),
    list(
      message = paste0(method, " ", url, "\n", describe(problem)),
      call = NULL,
      problem = problem,
      status = problem$status,
      url = url
    )
  )
}


# Raised when the request never reached the API at all.
implan_transport_error <- function(base_url, condition) {
  structure(
    class = c("implan_transport_error", "error", "condition"),
    list(
      message = paste0(
        "Could not reach ", base_url, ".\n", conditionMessage(condition), "\n",
        "Check your network connection and IMPLAN_API_URL."
      ),
      call = NULL
    )
  )
}


# Builds the client the workflows pass around.
#
# An environment rather than a list, because the token and the rate limit are
# mutable: a token refreshed part way through a run has to be visible to every
# call that follows, wherever the client was passed to.
api_client <- function(token_provider,
                       token_refresher = NULL,
                       base_url = implan_base_url(),
                       requests_per_minute = NULL) {
  client <- new.env(parent = emptyenv())
  client$base_url <- sub("/+$", "", base_url)
  client$token_provider <- token_provider
  client$token_refresher <- token_refresher
  client$requests_per_minute <- requests_per_minute
  class(client) <- "implan_client"
  client
}


# Switches on client-side throttling for a bulk workflow.
set_rate_limit <- function(client, requests_per_minute) {
  client$requests_per_minute <- requests_per_minute
  invisible(client)
}


# Strips the `Bearer ` prefix, because req_auth_bearer_token() adds its own.
bare_token <- function(token) sub("^Bearer\\s+", "", token)


# Builds one request, with every policy this API needs attached.
#
# `query` is a named list. A value holding several elements becomes a repeated
# parameter (`regions=Oregon&regions=Wisconsin`), which is the shape this API
# expects for its filters, hence `.multi = "explode"`. A list would flatten to
# the last value alone, silently, which is why the endpoint files build plain
# character vectors here.
#
# `body` is sent as JSON. It is allowed on a GET, which sounds wrong but is what
# a few of this API's report endpoints require; see
# `get_estimated_growth_percentage()` in endpoints/impact_results.R. httr2
# switches the method to POST as soon as a body is attached, so the method is set
# again afterwards.
build_request <- function(client, path, method = "GET", query = NULL, body = NULL) {
  req <- request(paste0(client$base_url, path)) |>
    req_user_agent(USER_AGENT) |>
    req_timeout(REQUEST_TIMEOUT_SECONDS) |>
    req_auth_bearer_token(bare_token(client$token_provider())) |>
    req_retry(
      max_tries = MAX_ATTEMPTS,
      retry_on_failure = TRUE,
      is_transient = function(resp) resp_status(resp) %in% RETRY_STATUSES
    ) |>
    req_error(body = function(resp) describe(problem_details(resp)))

  query <- Filter(Negate(is.null), as.list(query))
  if (length(query) > 0) {
    req <- req_url_query(req, !!!query, .multi = "explode")
  }

  if (!is.null(body)) {
    req <- req_body_json(req, body, auto_unbox = TRUE, null = "null")
  }

  if (!is.null(client$requests_per_minute)) {
    # The published limits are per minute, so one bucket that fills over 60
    # seconds is exactly the right shape.
    req <- req_throttle(req, capacity = client$requests_per_minute, fill_time_s = 60)
  }

  req_method(req, method)
}


# Performs one request, refreshing the token once if it has expired.
#
# httr2's retry policy has already dealt with 429 and the transient 5xx by the
# time anything reaches here, so this only has to handle the 401 case and turn
# whatever is left into an `implan_api_error`.
perform_request <- function(client, req) {
  for (attempt in seq_len(2L)) {
    started <- Sys.time()

    outcome <- tryCatch(
      list(ok = TRUE, resp = req_perform(req)),
      httr2_http = function(condition) {
        failed <- condition$resp
        if (is.null(failed)) {
          failed <- last_response()
        }
        list(ok = FALSE, resp = failed)
      },
      httr2_failure = function(condition) {
        stop(implan_transport_error(client$base_url, condition))
      }
    )

    log_exchange(req, outcome$resp, as.numeric(difftime(Sys.time(), started, units = "secs")))

    if (isTRUE(outcome$ok)) {
      return(outcome$resp)
    }

    # An expired token looks like a 401. Refresh once and try again; if the
    # second attempt also fails, the credentials or the subscription are the
    # problem, not the token.
    can_refresh <- attempt == 1L &&
      resp_status(outcome$resp) == 401L &&
      !is.null(client$token_refresher)

    if (can_refresh) {
      log_debug("401 received; refreshing the bearer token and retrying")
      client$token_refresher()
      req <- req_auth_bearer_token(req, bare_token(client$token_provider()))
      next
    }

    stop(implan_api_error(request_method(req), request_url(req), problem_details(outcome$resp)))
  }

  stop("The request loop finished without a response, which should not happen.", call. = FALSE)
}


# GETs a JSON document and parses it.
#
# `simplifyVector = FALSE` keeps every response as nested lists. It costs a
# little convenience and buys predictability: jsonlite would otherwise turn an
# array of objects into a data frame whenever those objects happen to share
# their fields, and leave it as a list when they do not, so the same endpoint
# would hand back different shapes on different days.
get_json <- function(client, path, query = NULL, body = NULL) {
  parse_json_response(perform_request(client, build_request(client, path, "GET", query, body)))
}


# GETs a text document, which for this API means a CSV report.
#
# Write the result to a file with a `.csv` extension and it opens in Excel or
# Sheets.
get_text <- function(client, path, query = NULL, body = NULL) {
  resp <- perform_request(client, build_request(client, path, "GET", query, body))
  resp_body_string(resp)
}


# POSTs a JSON body and reads whatever comes back.
#
# A few endpoints answer with a bare number or a sentence rather than an object:
# RunImpact returns a run id, and CancelImpact returns a confirmation. Both still
# need reading, so an unparseable response comes back as trimmed text.
post_json <- function(client, path, body = NULL) {
  parse_json_response(perform_request(client, build_request(client, path, "POST", body = body)))
}


# POSTs a file as multipart form data, for the Event Template upload.
post_file <- function(client, path, field_name, file_path) {
  req <- request(paste0(client$base_url, path)) |>
    req_user_agent(USER_AGENT) |>
    req_timeout(REQUEST_TIMEOUT_SECONDS) |>
    req_auth_bearer_token(bare_token(client$token_provider())) |>
    req_error(body = function(resp) describe(problem_details(resp)))

  # The field name matters: the API reads the upload from `excelFile`.
  parts <- list(curl::form_file(file_path))
  names(parts) <- field_name
  req <- do.call(req_body_multipart, c(list(req), parts))

  parse_json_response(perform_request(client, req))
}


# PUTs a JSON body and reads whatever comes back.
put_json <- function(client, path, body = NULL) {
  parse_json_response(perform_request(client, build_request(client, path, "PUT", body = body)))
}


# DELETEs a resource. The API returns no body worth reading.
delete_resource <- function(client, path) {
  perform_request(client, build_request(client, path, "DELETE"))
  invisible(NULL)
}


# Returns the response as parsed JSON when it is JSON, and as trimmed text
# otherwise.
parse_json_response <- function(resp) {
  body <- tryCatch(resp_body_string(resp), error = function(condition) "")
  if (!nzchar(trimws(body))) {
    return(NULL)
  }

  parsed <- tryCatch(fromJSON(body, simplifyVector = FALSE), error = function(condition) NULL)
  if (is.null(parsed)) {
    return(gsub('^"|"$', "", trimws(body)))
  }
  parsed
}
