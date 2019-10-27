from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v5_1.release.models import ReleaseStartMetadata,ArtifactMetadata,BuildVersion,ReleaseEnvironmentUpdateMetadata,ReleaseApproval
import pprint,time

class ReleaseDefinition:
    def __init__(self):
        pass
    
    def getReleaseClient(self, connection):
        release_client = connection.clients_v5_1.get_release_client()   # Get a client (the "release" client provides access to release etc)
        return (release_client)

    def getReleaseDefinitions(self, projectName, release_client, continuation_token=None):
        get_release_definitions_response = release_client.get_release_definitions(projectName, search_text=projectName, continuation_token=continuation_token)
        return (get_release_definitions_response)

    def waitForReleaseCompletion(self, release_client, release, config):
        releaseEnvironmentBreakonStatus = ['succeeded', 'partiallySucceeded', 'queued', 'rejected', 'scheduled', 'canceled']
        timeout = time.time() + 60*5     # set timeout to 5 mins
        release_id = release.id
        release_completion_status = release_client.get_release(config.vsts_project_name, release_id=release_id)
        for environment in release_completion_status.environments:
            if (environment.name == config.environment_name):
                environment_id = environment.id
        
        get_release_environment = release_client.get_release_environment(config.vsts_project_name, release_id, environment_id)
        while get_release_environment.status not in releaseEnvironmentBreakonStatus:
            get_release_environment = release_client.get_release_environment(config.vsts_project_name, release_id, environment_id)
            time.sleep(10)                        # sleep for 10 sec
            if (time.time() > timeout):           #timeout if release is not completed in 5 minutes
                break
        
        return (get_release_environment.status)

    def getLatestReleaseWithTag(self, config, release_client, releasedefinition_id, continuation_token=None):
        get_releases_response = release_client.get_releases(config.vsts_project_name, definition_id=releasedefinition_id, expand="tags,artifacts", tag_filter=[config.vsts_tag_name], top=1, continuation_token=continuation_token)
        return (get_releases_response)

    def createRelease(self, release_client, release_definition, artifacts, config):
        release_definition_id = release_definition.id
        artifactmetadata_list = []
        for artifact in artifacts:
            buildversion = BuildVersion(id=artifact.definition_reference['version'].id, name=artifact.definition_reference['definition'].name)
            artifactmetadata = ArtifactMetadata(alias=artifact.alias, instance_reference=buildversion)
            artifactmetadata_list.append(artifactmetadata)
        releasestartmetadata = ReleaseStartMetadata(artifacts=artifactmetadata_list, definition_id=release_definition_id, description="Creating Sample Release", manual_environments=list((config.manual_environments).split(",")))
        release = release_client.create_release(releasestartmetadata, config.vsts_project_name)
        return (release)

    def updateReleaseEnvironment(self, release_client, release, config):
        for environment in release.environments:
            if (environment.name == config.environment_name):
                environment_id = environment.id
                release_id = release.id
                environment_update_data = ReleaseEnvironmentUpdateMetadata(comment="Trigger Release for " + config.environment_name, status="inProgress")
                release_environment = release_client.update_release_environment(environment_update_data, config.vsts_project_name, release_id, environment_id)
                time.sleep(20)
                return (release_environment)

    def getApprovals(self, release_client, release, config):
        release_id = release.id
        approval_response = release_client.get_approvals(config.vsts_project_name, release_ids_filter=[release_id], top=1)
        return (approval_response)

    def updateReleaseApprovals(self, release_client, release, approvals, config):
        release_approval = ReleaseApproval(status="approved", comments="Automated Approved by Ops")
        for approval in approvals.value:
            approval_id = approval.id
            update_approval_response = release_client.update_release_approval(release_approval, config.vsts_project_name, approval_id)
        return (update_approval_response)