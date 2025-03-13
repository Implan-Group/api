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
    def __init__(self, hash_id, urid, user_model_id, description, model_id, model_build_status, employment, output, value_added, aggregation_scheme_id, dataset_id, dataset_description, fips_code, province_code, m49_code, region_type, has_accessible_children, region_type_description, geo_id, is_mrio_allowed):
        self.hash_id = hash_id
        self.urid = urid
        self.user_model_id = user_model_id
        self.description = description
        self.model_id = model_id
        self.model_build_status = model_build_status
        self.employment = employment
        self.output = output
        self.value_added = value_added
        self.aggregation_scheme_id = aggregation_scheme_id
        self.dataset_id = dataset_id
        self.dataset_description = dataset_description
        self.fips_code = fips_code
        self.province_code = province_code
        self.m49_code = m49_code
        self.region_type = region_type
        self.has_accessible_children = has_accessible_children
        self.region_type_description = region_type_description
        self.geo_id = geo_id
        self.is_mrio_allowed = is_mrio_allowed
 
