
setClass("Region",
         slots = list(
           HashId = "character",
           Urid = "integer",
           UserModelId = "integer",
           Description = "character",
           ModelId = "integer",
           ModelBuildStatus = "character",
           Employment = "numeric",
           Output = "numeric",
           ValueAdded = "numeric",
           AggregationSchemeId = "integer",
           DatasetId = "integer",
           DatasetDescription = "character",
           FipsCode = "character",
           ProvinceCode = "character",
           M49Code = "character",
           RegionType = "character",
           HasAccessibleChildren = "logical",
           RegionTypeDescription = "character",
           GeoId = "character",
           IsMrioAllowed = "logical"
         ))
