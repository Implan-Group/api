# Spending patterns: how a dollar moves through a supply chain.
#
# A spending pattern is a list of commodities with the share of a dollar that
# goes to each. IMPLAN supplies a default pattern for every industry and
# institution, and you can read it, change individual coefficients, and send it
# back as part of an event.
#
# Wiki: Spending Patterns
# https://github.com/Implan-Group/api/wiki/Spending-Patterns


# Which family of spending pattern to read.
#
# "Institution" patterns additionally require a region, because government and
# household spending varies by where it happens.
SPENDING_PATTERN_TYPES <- c(
  INDUSTRY = "Industry",
  INSTITUTION = "Institution",
  CUSTOM = "Custom",
  HOUSEHOLD = "Household"
)


# One commodity within a spending pattern, and the share spent on it.
#
# `coefficient` is that share, from 0 to 1, and the coefficients across a pattern
# sum to 1. Change one and set `is_user_coefficient` so IMPLAN knows the value is
# yours rather than its own.
#
# `local_purchase_percentage` is how much of this commodity is bought inside the
# region. Leave it at 1 to assume everything is local, or set `is_sam_value` to
# have IMPLAN substitute the region's own trade data, which is usually the more
# defensible choice.
spending_pattern_commodity_from_api <- function(payload) {
  from_api(
    payload,
    defaults = list(
      commodity_code = NA_integer_,
      commodity_description = "",
      coefficient = NULL,
      is_sam_value = FALSE,
      is_user_coefficient = FALSE,
      local_purchase_percentage = 1.0
    ),
    class_name = "implan_spending_pattern_commodity"
  )
}


# One line naming the commodity and its share, for the console.
describe.implan_spending_pattern_commodity <- function(x, ...) {
  share <- if (is.null(x$coefficient)) "" else sprintf("%.6f", x$coefficient)
  sprintf("%5s  %10s  %s", x$commodity_code, share, x$commodity_description)
}


# Reads a spending pattern's commodity list.
#
# The shape varies a little by pattern type: some of these endpoints answer with
# the commodity array directly, and others wrap it in an object. Both are handled
# so a caller does not have to care which it got.
spending_pattern_commodities_from_api <- function(payload) {
  if (is.null(payload)) {
    return(list())
  }

  # A bare array: the items have no names of their own at the top level.
  if (is.null(names(payload))) {
    return(list_from_api(payload, spending_pattern_commodity_from_api))
  }

  commodities <- payload$commodities
  if (is.null(commodities)) {
    commodities <- payload$spendingPatternCommodities
  }
  list_from_api(commodities, spending_pattern_commodity_from_api)
}
