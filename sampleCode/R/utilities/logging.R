# Console and file logging for the samples.
#
# Two audiences are served here. The console gets a readable narration of what a
# workflow is doing. The log file gets the full request and response detail,
# which is what you send to support@implan.com when something is wrong.
#
# The `Authorization` header is redacted in both. A bearer token is a credential:
# it is as good as your password for the next 24 hours, so it never reaches a
# console, a log file, or a screenshot. httr2 marks the header as secret when
# `req_auth_bearer_token()` sets it, and `req_get_headers(redacted = "redact")`
# is what honours that mark. The name list below is a second guard, in case a
# header is ever added without one.


# Header names never written out, compared case-insensitively.
REDACTED_HEADERS <- c("authorization", "x-api-key", "cookie", "set-cookie")

# A response body longer than this is truncated in the log. Region and industry
# lists run to megabytes, and a log nobody can open helps nobody.
MAX_LOGGED_BODY_CHARS <- 20000


# Today's log file. The folder is created on first use.
log_file_path <- function() {
  directory <- log_directory()
  if (!dir.exists(directory)) {
    dir.create(directory, recursive = TRUE)
  }
  file.path(directory, sprintf("Log_%s.txt", format(Sys.Date(), "%Y%m%d")))
}


# Writes one line of narration to the console.
#
# `...` is passed to sprintf when there is one, so this reads the same way as the
# C# and Python samples: log_info("  %d regions", n).
#
# Narration goes to stdout rather than through message(), so that redirecting the
# output of a run to a file captures the story of it.
log_info <- function(format_string = "", ...) {
  text <- if (...length() > 0) sprintf(format_string, ...) else format_string
  cat(text, "\n", sep = "")
  invisible(NULL)
}


# Prints a step heading.
#
# Workflows are written as numbered steps, and these are the headings. Keeping
# them in one place means every sample's console output looks the same.
log_heading <- function(text) {
  cat("\n", text, "\n", strrep("-", nchar(text)), "\n", sep = "")
  invisible(NULL)
}


# Appends a line to the log file only, not the console.
log_debug <- function(text) {
  cat(
    format(Sys.time(), "%Y-%m-%d %H:%M:%S"), " ", text, "\n",
    file = log_file_path(), sep = "", append = TRUE
  )
  invisible(NULL)
}


# Renders a body for the log, prettified when it is JSON.
prettify_body <- function(body) {
  if (is.null(body) || !nzchar(body)) {
    return("")
  }

  trimmed <- trimws(body)
  if (!startsWith(trimmed, "{") && !startsWith(trimmed, "[")) {
    return(body)
  }

  # Not valid JSON after all; log it as it came.
  as.character(tryCatch(jsonlite::prettify(body), error = function(condition) body))
}


# The method of a request. httr2 leaves it unset for a plain GET.
request_method <- function(req) {
  method <- tryCatch(httr2::req_get_method(req), error = function(condition) NULL)
  if (!is.null(method)) {
    return(method)
  }
  if (is.null(req$method)) "GET" else req$method
}


# The full URL of a request, including the query string.
request_url <- function(req) {
  tryCatch(httr2::req_get_url(req), error = function(condition) req$url)
}


# The request body, rendered for the log, with the token-bearing parts left out.
request_body_text <- function(req) {
  type <- tryCatch(httr2::req_get_body_type(req), error = function(condition) "empty")

  if (identical(type, "empty")) {
    return(NULL)
  }
  if (identical(type, "multipart") || identical(type, "file")) {
    # A file upload. Naming it is useful; printing its bytes into a text log is
    # not.
    return(sprintf("<%s body, not logged>", type))
  }

  body <- tryCatch(
    httr2::req_get_body(req, obfuscated = "redact"),
    error = function(condition) NULL
  )
  if (is.null(body)) {
    return(NULL)
  }

  if (is.character(body)) {
    return(prettify_body(paste(body, collapse = "\n")))
  }

  rendered <- tryCatch(
    as.character(jsonlite::toJSON(body, auto_unbox = TRUE, null = "null")),
    error = function(condition) NULL
  )
  if (is.null(rendered)) NULL else prettify_body(rendered)
}


# The response's content type, or a placeholder when it did not send one.
response_content_type <- function(resp) {
  type <- tryCatch(httr2::resp_content_type(resp), error = function(condition) NULL)
  if (is.null(type) || is.na(type)) "(none)" else type
}


# Writes one request and response pair to the log file.
#
# This is the record to attach to a support ticket. It has the method, the full
# URL, the headers with credentials removed, both bodies, the status, and how
# long the call took.
log_exchange <- function(req, resp, elapsed_seconds) {
  lines <- c("--------", paste(request_method(req), request_url(req)))

  headers <- tryCatch(
    httr2::req_get_headers(req, redacted = "redact"),
    error = function(condition) list()
  )
  for (name in names(headers)) {
    value <- if (tolower(name) %in% REDACTED_HEADERS) {
      "<redacted>"
    } else {
      paste(as.character(headers[[name]]), collapse = ", ")
    }
    lines <- c(lines, sprintf("  %s: %s", name, value))
  }

  body <- request_body_text(req)
  if (!is.null(body) && nzchar(body)) {
    lines <- c(lines, "  request body:", body)
  }

  if (is.null(resp)) {
    # No response at all, which means the request never completed.
    log_debug(paste(c(lines, "  -> no response"), collapse = "\n"))
    return(invisible(NULL))
  }

  lines <- c(
    lines,
    sprintf(
      "  -> %d %s in %.2fs",
      httr2::resp_status(resp), httr2::resp_status_desc(resp), elapsed_seconds
    ),
    sprintf("  response content-type: %s", response_content_type(resp))
  )

  response_body <- prettify_body(
    tryCatch(httr2::resp_body_string(resp), error = function(condition) "")
  )
  if (nchar(response_body) > MAX_LOGGED_BODY_CHARS) {
    response_body <- paste0(
      substr(response_body, 1, MAX_LOGGED_BODY_CHARS),
      sprintf(
        "\n... truncated, %d more characters",
        nchar(response_body) - MAX_LOGGED_BODY_CHARS
      )
    )
  }
  if (nzchar(response_body)) {
    lines <- c(lines, "  response body:", response_body)
  }

  log_debug(paste(lines, collapse = "\n"))
}
