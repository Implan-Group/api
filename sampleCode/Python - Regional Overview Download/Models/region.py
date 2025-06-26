from typing import Any

# The names of the properties are non-standard so that they correctly map to the returned JSON
# noinspection PyPep8Naming

class Region:
    """
    This class holds data about a particular IMPLAN Region
    """

    # Constructor for Region maps to expected json
    def __init__(self,
                 hashId: str,
                 urid: int,
                 userModelId: int | None,
                 description: str,
                 modelId: int | None,
                 modelBuildStatus: str,
                 employment: float,
                 output: float,
                 valueAdded: float,
                 datasetId: int,
                 datasetDescription: str,
                 regionType: str,
                 hasAccessibleChildren: bool,
                 regionTypeDescription: str,
                 geoId: int | None,
                 isMrioAllowed: bool,
                 # All the below properties are optional
                 aggregationSchemeId: int | None = None,
                 fipsCode: int | None = None,
                 provinceCode: int | None = None,
                 m49Code: int | None = None,
                 isCustomized: bool = False,
                 isCombined: bool = False,
                 parentRegionIds: list[Any] | None = None,
                 isCustomizable: bool = False,
                 isCombinable: bool = False,
                 hasAccess: bool = False,
                 regionTypeSort: int = 0,
                 congressionalSession: int | None = None,
                 ):
        self.hashId = hashId
        self.urid = urid
        self.userModelId = userModelId
        self.description = description
        self.modelId = modelId
        self.modelBuildStatus = modelBuildStatus
        self.employment = employment
        self.output = output
        self.valueAdded = valueAdded
        self.datasetId = datasetId
        self.datasetDescription = datasetDescription
        self.regionType = regionType
        self.hasAccessibleChildren = hasAccessibleChildren
        self.regionTypeDescription = regionTypeDescription
        self.geoId = geoId
        self.isMrioAllowed = isMrioAllowed

        self.aggregationSchemeId = aggregationSchemeId
        self.fipsCode = fipsCode
        self.provinceCode = provinceCode
        self.m49Code = m49Code
        self.isCustomized = isCustomized
        self.isCombined = isCombined
        self.parentRegionIds = parentRegionIds
        self.isCustomizable = isCustomizable
        self.isCombinable = isCombinable
        self.hasAccess = hasAccess
        self.regionTypeSort = regionTypeSort
        self.congressionalSession = congressionalSession