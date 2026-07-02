from endpoints.endpoints_helper import EndpointsHelper


class ApiEndpoint:
    """
    The base class for an Endpoints collection.
    This provides access to the EndpointsHelper, RestHelper, LoggingHelper, and base Impact API Url
    """

    def __init__(self,
                 endpoints_helper: EndpointsHelper):
        self.endpoints = endpoints_helper
        self.rest_helper = endpoints_helper.rest_helper
        self.logging_helper = endpoints_helper.logging_helper
        self.base_url = endpoints_helper.base_url