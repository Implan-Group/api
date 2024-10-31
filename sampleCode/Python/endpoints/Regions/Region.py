# MIT License

# Copyright (c) 2023 IMPLAN

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class Region:
    def __init__(self, hashId, urid, userModelId, description, modelId, modelBuildStatus, employment, output, valueAdded, aggregationSchemeId, datasetId, datasetDescription, fipsCode, provinceCode, m49Code, regionType, hasAccessibleChildren, regionTypeDescription, geoId, isMrioAllowed):
        self.hash_id = hashId
        self.urid = urid
        self.user_model_id = userModelId
        self.description = description
        self.model_id = modelId
        self.model_build_status = modelBuildStatus
        self.employment = employment
        self.output = output
        self.value_added = valueAdded
        self.aggregation_scheme_id = aggregationSchemeId
        self.dataset_id = datasetId
        self.dataset_description = datasetDescription
        self.fips_code = fipsCode
        self.province_code = provinceCode
        self.m49_code = m49Code
        self.region_type = regionType
        self.has_accessible_children = hasAccessibleChildren
        self.region_type_description = regionTypeDescription
        self.geo_id = geoId
        self.is_mrio_allowed = isMrioAllowed
 
