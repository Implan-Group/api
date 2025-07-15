from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper

class ApiEndpoint:
    def __init__(self,
                 rest_helper: RestHelper,
                 logging_helper: LoggingHelper,
                 base_url: str | None = None):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.base_url: str = base_url or "https://api.implan.com"
        self.endpoints: EndpointsHelper = EndpointsHelper(rest_helper, logging_helper, base_url)


class EndpointsHelper:
    def __init__(self,
                 rest_helper: RestHelper,
                 logging_helper: LoggingHelper,
                 base_url: str | None = None):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.base_url = base_url or "https://api.implan.com"

        # We must import in this order to prevent circular references

        from endpoints.data_endpoints import DataEndpoints
        self.data_endpoints = DataEndpoints(self)

        from endpoints.event_endpoints import EventEndpoints
        self.event_endpoints = EventEndpoints(self)

        from endpoints.industry_endpoints import IndustryEndpoints
        self.industry_endpoints = IndustryEndpoints(self)

        from endpoints.project_endpoints import ProjectEndpoints
        self.project_endpoints = ProjectEndpoints(self)

        from endpoints.group_endpoints import GroupEndpoints
        self.group_endpoints = GroupEndpoints(self)

        from endpoints.regional_endpoints import RegionalEndpoints
        self.regional_endpoints = RegionalEndpoints(self)

        from endpoints.impact_endpoints import ImpactEndpoints
        self.impact_endpoints = ImpactEndpoints(self)

        from endpoints.report_endpoints import ReportEndpoints
        self.report_endpoints = ReportEndpoints(self)