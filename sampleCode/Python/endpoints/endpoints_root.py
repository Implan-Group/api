from services.logging_helper import LoggingHelper
from services.rest_helper import RestHelper


class EndpointsHelper:
    def __init__(self,
                 rest_helper: RestHelper,
                 logging_helper: LoggingHelper,
                 base_url: str | None = None):
        self.rest_helper: RestHelper = rest_helper
        self.logging_helper: LoggingHelper = logging_helper
        self.base_url = base_url or "https://api.implan.com"

        from endpoints.aggregation_endpoints import AggregationSchemeEndpoints
        from endpoints.dataset_endpoints import DatasetEndpoints
        from endpoints.event_endpoints import EventEndpoints
        from endpoints.industry_endpoints import IndustryEndpoints
        from endpoints.project_endpoints import ProjectEndpoints
        from endpoints.group_endpoints import GroupEndpoints
        from endpoints.regional_endpoints import RegionalEndpoints
        from endpoints.impact_endpoints import ImpactEndpoints
        from endpoints.report_endpoints import ReportEndpoints

        self.aggregation_endpoints: AggregationSchemeEndpoints = AggregationSchemeEndpoints(self)
        self.dataset_endpoints: DatasetEndpoints = DatasetEndpoints(self)
        self.project_endpoints: ProjectEndpoints = ProjectEndpoints(self)
        self.industry_endpoints: IndustryEndpoints = IndustryEndpoints(self)
        self.event_endpoints: EventEndpoints = EventEndpoints(self)
        self.regional_endpoints: RegionalEndpoints = RegionalEndpoints(self)
        self.group_endpoints: GroupEndpoints = GroupEndpoints(self)
        self.impact_endpoints: ImpactEndpoints = ImpactEndpoints(self)
        self.report_endpoints: ReportEndpoints = ReportEndpoints(self)
