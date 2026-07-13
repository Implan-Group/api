from endpoints.endpoints_helper import EndpointsHelper


class WorkflowExample:
    """
    The base class for any Workflow Example(s)
    All implementations gain access to the EndpointsHelper
    """

    def __init__(self, endpoints_helper: EndpointsHelper):
        self.endpoints = endpoints_helper
