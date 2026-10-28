# Loads the samples, and gives the tests a client and scripted responses.
#
# testthat runs from tests/testthat, so the sample root is two folders up.
# Sourcing main.R loads every file; it runs the command line only when Rscript is
# handed main.R itself, so sourcing it here is safe.
source(file.path(testthat::test_path("..", ".."), "main.R"))


# A token-shaped value that must never show up in the log.
FAKE_TOKEN <- "Bearer not.a.real.token"


# A client like the one the workflows use, pointed at a host that does not exist.
# With httr2's mocking on, no request reaches it.
test_client <- function(token_refresher = NULL) {
  api_client(
    token_provider = function() FAKE_TOKEN,
    token_refresher = token_refresher,
    base_url = "https://example.invalid"
  )
}


# One scripted response, in the form httr2's mocking takes.
mock_response <- function(status, body = "", content_type = "application/json", headers = list()) {
  httr2::response(
    status_code = status,
    headers = c(list(`Content-Type` = content_type), headers),
    body = charToRaw(body)
  )
}


# What R renders a request or model as on the wire.
as_json <- function(x) {
  as.character(jsonlite::toJSON(x, auto_unbox = TRUE, null = "null"))
}
