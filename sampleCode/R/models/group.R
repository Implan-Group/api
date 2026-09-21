# Groups: where and when an event happens.
#
# An Event says what changed. A Group pairs one region and one dollar year with
# the events that apply there. Running the same events in three states means
# three groups, which is the MultiEventToMultiGroup workflow.
#
# Wiki: Groups - https://github.com/Implan-Group/api/wiki/Groups


# The link between a Group and one of the Project's Events.
#
# `scaling_factor` multiplies the event's values inside this group. It is a
# multiplier and not a percentage: 1 leaves the event alone, 0.55 more than
# halves it, and 5000 analyzes it five thousand times over. Two decimal places
# are kept.
#
# Group and event scaling compound, so an event scaled 3000 inside a group scaled
# 5 is analyzed at 15000. Scale at one level or the other, not both. To leave an
# event out of a group, remove it rather than scaling it to zero.
group_event <- function(event_id, scaling_factor = 1.0) {
  list(event_id = event_id, scaling_factor = scaling_factor)
}


# One region and dollar year, with the events that apply to it.
#
# Supply exactly one region identifier: `hash_id`, `urid`, `user_model_id`, or
# `model_id`. HashId is the one to use.
#
# `dollar_year` has no server-side default, and a group saved without one
# produces an impact run that never attaches, so always set it. The samples use
# the current calendar year.
new_group <- function(title,
                      hash_id = NULL,
                      urid = NULL,
                      user_model_id = NULL,
                      model_id = NULL,
                      dollar_year = NULL,
                      dataset_id = NULL,
                      scaling_factor = 1.0,
                      group_events = list()) {
  structure(
    list(
      title = title,
      hash_id = hash_id,
      urid = urid,
      user_model_id = user_model_id,
      model_id = model_id,
      dollar_year = dollar_year,
      dataset_id = dataset_id,
      scaling_factor = scaling_factor,
      group_events = group_events
    ),
    class = c("implan_group", "implan_model", "list")
  )
}


# Reads a group, including its nested event links.
group_from_api <- function(payload) {
  group <- from_api(
    payload,
    defaults = list(
      title = "",
      id = NULL,
      project_id = NULL,
      hash_id = NULL,
      urid = NULL,
      user_model_id = NULL,
      model_id = NULL,
      dollar_year = NULL,
      dataset_id = NULL,
      scaling_factor = 1.0,
      group_events = list()
    ),
    class_name = "implan_group"
  )

  group$group_events <- list_from_api(
    group$group_events,
    function(item) {
      from_api(
        item,
        defaults = list(event_id = NULL, scaling_factor = 1.0),
        class_name = "implan_group_event"
      )
    }
  )
  group
}


# One line naming the group, for the console.
describe.implan_group <- function(x, ...) {
  sprintf(
    "%s  id=%s  hashId=%s  events=%d",
    x$title,
    field_or(x, "id", "(none)"),
    field_or(x, "hash_id", "(none)"),
    length(x$group_events)
  )
}
