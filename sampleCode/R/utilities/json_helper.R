# Translation between the API's JSON and the sample's R lists.
#
# The Impact API speaks camelCase; R here is written in snake_case. These
# functions do the conversion, and `from_api()` is deliberately tolerant so the
# samples keep working when the API starts returning a field they have never
# heard of.
#
# That tolerance is the important part. The API gains fields over time, and code
# that rejects an unexpected key turns a routine addition into a broken sample,
# so unknown keys are kept rather than dropped. Print a model to see everything a
# response really contained.


# Converts an R field name to the API's spelling: hash_id -> hashId.
camel_case <- function(names) {
  vapply(
    names,
    function(name) {
      parts <- strsplit(name, "_", fixed = TRUE)[[1]]
      if (length(parts) < 2) {
        return(name)
      }
      rest <- parts[-1]
      paste0(parts[1], paste0(toupper(substring(rest, 1, 1)), substring(rest, 2), collapse = ""))
    },
    character(1),
    USE.NAMES = FALSE
  )
}


# Converts an API field name to R's spelling: hashId -> hash_id.
snake_case <- function(names) {
  tolower(gsub("([a-z0-9])([A-Z])", "\\1_\\2", names))
}


# Builds a model from one JSON object, renaming its fields and keeping the ones
# this sample does not know about.
#
# `defaults` is a named list giving the fields the model declares and the value
# each takes when the API leaves it out. Anything else the response carried is
# kept under its original name, so nothing is silently discarded.
from_api <- function(payload, defaults = list(), class_name = NULL) {
  model <- defaults

  if (!is.null(payload) && length(payload) > 0) {
    for (api_name in names(payload)) {
      value <- payload[[api_name]]
      r_name <- snake_case(api_name)
      if (r_name %in% names(defaults)) {
        # A field the model declares. JSON null arrives as NULL, which would
        # delete the entry, so keep the default in that case.
        if (!is.null(value)) {
          model[[r_name]] <- value
        }
      } else if (!is.null(value)) {
        # A field the API has added, or one this sample has no use for. Keep it
        # rather than failing.
        model[[api_name]] <- value
      }
    }
  }

  if (!is.null(class_name)) {
    class(model) <- c(class_name, "implan_model", "list")
  }
  model
}


# Builds a list of models from a JSON array.
#
# Endpoints with nothing to return sometimes answer null rather than an empty
# array, so that case becomes an empty list.
list_from_api <- function(payload, builder) {
  if (is.null(payload) || length(payload) == 0) {
    return(list())
  }
  lapply(payload, builder)
}


# Fields that must always serialize as a JSON array.
#
# The request bodies are written with `auto_unbox = TRUE`, which turns a
# length-one vector into a JSON scalar. That is what you want almost everywhere
# and wrong for these: one tag has to go out as ["capital"] and not "capital",
# and the growth report rejects a filter that is not an array. Listing them here
# rather than at each call site means a new caller cannot forget.
ARRAY_FIELDS <- c(
  "tags", "hash_ids", "urids",
  "regions", "impacts", "group_names", "event_names", "event_tags"
)


# Renders a model as the JSON object the API expects.
#
# Fields set to NULL are left out rather than sent as null. The API reads an
# absent optional field as "not supplied", which is what NULL means in these
# models: a Group carries exactly one region identifier, and the other three stay
# absent.
to_api <- function(model, array_fields = ARRAY_FIELDS) {
  payload <- list()

  for (name in names(model)) {
    value <- model[[name]]
    if (is.null(value)) {
      next
    }

    api_name <- camel_case(name)

    if (name %in% array_fields) {
      # Force an array. An unnamed list is what jsonlite renders as one, and an
      # empty one renders as [].
      payload[[api_name]] <- unname(as.list(value))
    } else if (is.list(value) && !is.null(names(value))) {
      # A nested model.
      payload[[api_name]] <- to_api(value, array_fields)
    } else if (is.list(value)) {
      # A list of nested models, such as a group's events.
      payload[[api_name]] <- unname(lapply(value, to_api, array_fields = array_fields))
    } else {
      payload[[api_name]] <- value
    }
  }

  payload
}


# One-line descriptions for the console.
#
# `describe()` is a generic so each model can say what matters about itself,
# which keeps the workflows readable: they log describe(region) rather than
# assembling the same three fields every time.
describe <- function(x, ...) UseMethod("describe")

describe.default <- function(x, ...) {
  paste(names(x), unlist(lapply(x, function(v) paste(v, collapse = "/"))),
        sep = "=", collapse = "  ")
}


# Reads a field that may be missing, which is how an optional number in a
# response is handled everywhere in these samples.
field_or <- function(model, name, default = NULL) {
  value <- model[[name]]
  if (is.null(value)) default else value
}
