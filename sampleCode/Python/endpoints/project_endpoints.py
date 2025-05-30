import requests

class Project:
    def __init__(self, id_, title, aggregation_scheme_id, household_set_id, is_mrio=False, folder_id=None, last_impact_run_id=None):
        self.id = id_
        self.title = title
        self.aggregation_scheme_id = aggregation_scheme_id
        self.household_set_id = household_set_id
        self.is_mrio = is_mrio
        self.folder_id = folder_id
        self.last_impact_run_id = last_impact_run_id

    @classmethod
    def from_dict(cls, data):
        return cls(
            id_=data.get("id"),
            title=data.get("title"),
            aggregation_scheme_id=data.get("aggregationSchemeId"),
            household_set_id=data.get("householdSetId"),
            is_mrio=data.get("isMrio", False),
            folder_id=data.get("folderId"),
            last_impact_run_id=data.get("lastImpactRunId"),
        )

    def to_dict(self):
        data = {
            "Title": self.title,
            "AggregationSchemeId": self.aggregation_scheme_id,
            "HouseholdSetId": self.household_set_id,
            "IsMrio": self.is_mrio,
        }
        if self.folder_id is not None:
            data["FolderId"] = self.folder_id
        if self.last_impact_run_id is not None:
            data["LastImpactRunId"] = self.last_impact_run_id
        return data

class ProjectEndpoints:
    @staticmethod
    def create(project, bearer_token):
        url = "https://api.implan.com/api/v1/impact/project"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.post(url, json=project.to_dict(), headers=headers)
        if response.status_code == 200:
            project_data = response.json()
            print(f"Created Project: {project_data}")  # Debugging line
            return Project.from_dict(project_data)
        else:
            print(f"Failed to create project: {response.status_code} - {response.text}")
            response.raise_for_status()


    @staticmethod
    def get_project(project_id, bearer_token):
        url = f"https://api.implan.com/api/v1/impact/project/{project_id}"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            project_data = response.json()
            print(f"Project Data: {project_data}")  # Debugging line to check the response format
            if isinstance(project_data, list):
                if project_data:
                    return Project.from_dict(project_data[0])
                else:
                    raise ValueError("No project found with the specified ID.")
            else:
                return Project.from_dict(project_data)
        else:
            print(f"Failed to get project: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def get_projects(bearer_token):
        url = "https://api.implan.com/api/v1/impact/project"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            projects_data = response.json()
            print(f"Projects Data: {projects_data}")  # Debugging line
            return [Project.from_dict(project) for project in projects_data]
        else:
            print(f"Failed to get projects: {response.status_code} - {response.text}")
            response.raise_for_status()

    @staticmethod
    def get_shared_projects(bearer_token):
        url = "https://api.implan.com/api/v1/impact/project/shared"
        headers = {"Authorization": f"Bearer {bearer_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            shared_projects_data = response.json()
            print(f"Shared Projects Data: {shared_projects_data}")  # Debugging line
            return [Project.from_dict(project) for project in shared_projects_data]
        else:
            print(f"Failed to get shared projects: {response.status_code} - {response.text}")
            response.raise_for_status()