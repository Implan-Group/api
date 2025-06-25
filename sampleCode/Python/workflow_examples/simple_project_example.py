from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class SimpleProjectExample:
    """
    This is an example workflow use as inspiration


    """

    def __init__(self, rest_helper: RestHelper, logging_helper: LoggingHelper):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper

    def complete_workflow(self):

        # An Aggregation Scheme Id is required for filtering
        # If one is not already known, you can query for a full list


