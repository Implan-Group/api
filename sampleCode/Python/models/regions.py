from typing import Any

class Region:
    """
    This Model holds data about a particular IMPLAN Region
    """

    def __init__(self,
                 hash_id: str,
                 urid: int,
                 user_model_id: int | None,
                 description: str,
                 model_id: int | None,
                 model_build_status: str,
                 employment: float,
                 output: float,
                 value_added: float,
                 dataset_id: int,
                 dataset_description: str,
                 region_type: str,
                 has_accessible_children: bool,
                 region_type_description: str,
                 geo_id: int | None,
                 is_mrio_allowed: bool,
                 # All the below properties are optional
                 aggregation_scheme_id: int | None = None,
                 fips_code: int | None = None,
                 province_code: int | None = None,
                 m49_code: int | None = None,
                 is_customized: bool = False,
                 is_combined: bool = False,
                 parent_region_ids: list[Any] | None = None,
                 is_customizable: bool = False,
                 is_combinable: bool = False,
                 has_access: bool = False,
                 region_type_sort: int = 0,
                 congressional_session: int | None = None,
                 ):
        self.hash_id = hash_id
        self.urid = urid
        self.user_model_id = user_model_id
        self.description = description
        self.model_id = model_id
        self.model_build_status = model_build_status
        self.employment = employment
        self.output = output
        self.value_added = value_added
        self.dataset_id = dataset_id
        self.dateset_description = dataset_description
        self.region_type = region_type
        self.has_accessible_children = has_accessible_children
        self.region_type_description = region_type_description
        self.geo_id = geo_id
        self.is_mrio_allowed = is_mrio_allowed

        self.aggregation_scheme_id = aggregation_scheme_id
        self.fips_code = fips_code
        self.province_code = province_code
        self.m49_code = m49_code
        self.is_customized = is_customized
        self.is_combined = is_combined
        self.parent_region_ids = parent_region_ids
        self.is_customizable = is_customizable
        self.is_combinable = is_combinable
        self.has_access = has_access
        self.region_type_sort = region_type_sort
        self.congressional_session = congressional_session