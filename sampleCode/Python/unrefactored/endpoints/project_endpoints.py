import requests



class ProjectEndpointsOld:
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