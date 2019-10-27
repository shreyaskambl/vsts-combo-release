from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import pprint

class Project:
    
    def __init__(self, projectName):
        self.name = projectName

    def set_connection(self, personal_access_token, organization_url):
        credentials = BasicAuthentication('', personal_access_token)
        connection = Connection(base_url=organization_url, creds=credentials)
        return(connection)
        
    def get_core_client(self, connection):
        # Get a client (the "core" client provides access to projects, teams, etc)
        core_client = connection.clients.get_core_client()
        return (core_client)
    
    def getProjects(self, core_client):
        get_projects_response = core_client.get_projects()
        index = 0
        while get_projects_response is not None:
            for project in get_projects_response.value:
                pprint.pprint("[" + str(index) + "] " + project.name)
                index += 1
            if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
                # Get the next page of projects
                get_projects_response = core_client.get_projects(continuation_token=get_projects_response.continuation_token)
            else:
                # All projects have been retrieved
                get_projects_response = None