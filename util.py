import sys, inspect, logging
from lib.releasedefinition import ReleaseDefinition
from lib.release_model import ReleaseStatusSummary
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')

def set_connection (project, personal_access_token, organization_url):
    connection = project.set_connection(personal_access_token, organization_url)
    return (connection)

def get_release_client (project, release, personal_access_token, config):
    connection = set_connection(project, personal_access_token, config.organization_url)
    release_client = release.getReleaseClient(connection)
    return (release_client)

def get_release_definitions (release, release_client, config, continuation_token=None):
    release_definitions=[]
    with open(config.pdi_services_list) as f:
        vstsBuildDefPrefix = f.read().splitlines()
        f.close()

    get_release_definitions_response = release.getReleaseDefinitions(config.vsts_project_name, release_client, continuation_token)   #get list of release definitions
    while get_release_definitions_response is not None:
        for releasedefinition in get_release_definitions_response.value:
            if any(str(releasedefinition.name) == prefix for prefix in vstsBuildDefPrefix):
                release_definitions.append(releasedefinition)
        if get_release_definitions_response.continuation_token is not None and get_release_definitions_response.continuation_token != "":
            # Get the next page of release definitions
            get_release_definitions_response = release.get_release_definitions(release, release_client, config, continuation_token=get_release_definitions_response.continuation_token)
        else:
            # All release definitions have been retrieved
            get_release_definitions_response = None
    return (release_definitions)

def get_tagged_release (release_definition, release, release_client, config, continuation_token=None):
    release_definition_id = release_definition.id
    get_release_response = release.getLatestReleaseWithTag(config, release_client, release_definition_id, continuation_token)   #get list of release definitions
    while get_release_response is None:
        if get_release_response.continuation_token is not None and get_release_response.continuation_token != "":
            # Get the next page of releases 
            get_release_response = release.getLatestReleaseWithTag(config, release_client, release_definition_id, continuation_token=get_release_response.continuation_token)
        #### need to implement ty-catch here####
        #else:
            # All release definitions have been retrieved
        #    get_release_response = None    
    return (get_release_response)

def get_tagged_release_artifact (release_definition, release, release_client, config, continuation_token=None):
    get_release_response = get_tagged_release(release_definition, release, release_client, config)   #get list of release definitions
    artifacts = get_release_response.value[0].artifacts   #reading first index value as we expect only single element in the release response list
    return(artifacts)

def create_release (release_definition, release, release_client, artifacts, config, continuation_token=None):
    release = release.createRelease(release_client, release_definition, artifacts, config)   #create a release using artifact from tagged release
    return (release)

def update_release_environment (release_client, release, triggered_release, config, continuation_token=None):
    release_environment = release.updateReleaseEnvironment(release_client, triggered_release, config)   #deploy an environment
    return (release_environment)

def get_approvals (release_client, release, triggered_release, config, continuation_token=None):
    release_environment = release.getApprovals(release_client, triggered_release, config)   #get list of approvals for the release
    return (release_environment)

def update_release_approvals (release_client, release, triggered_release, approvals, config, continuation_token=None):
    release_environment = release.updateReleaseApprovals(release_client, triggered_release, approvals, config)   #approve the release
    return (release_environment)

def wait_for_release_completion (release_client, release, triggered_release, config, continuation_token=None):
    release_completion_status = release.waitForReleaseCompletion(release_client, triggered_release, config)   #approve the release
    return (release_completion_status)

def loop_through_release_definitions_to_trigger_release (release, release_client, config):
    release_summary_status_list = []
    release_definitions = get_release_definitions(release, release_client, config)  #get list of release definitions
    for release_definition in release_definitions:
        logging.info ("Triggering Release for " + str(release_definition.name))
        artifacts = get_tagged_release_artifact(release_definition, release, release_client, config)

        triggered_release = create_release(release_definition, release, release_client, artifacts, config)

        triggered_release_environment = update_release_environment(release_client, release, triggered_release, config)

        approvals = get_approvals(release_client, release, triggered_release, config)
        if ( len(approvals.value) > 0):                     #if approval count is greater that 0, approve the release
            update_approval_response = update_release_approvals(release_client, release, triggered_release, approvals, config)
            approval_status = update_approval_response.status
        else:
            approval_status = "NA"
        release_completion_status = wait_for_release_completion(release_client, release, triggered_release, config)

        release_summary_status = ReleaseStatusSummary(release_definition.name, triggered_release.name, approval_status, release_completion_status)
        release_summary_status_list.append(release_summary_status)
        return(release_summary_status_list)

def output_release_status(release_summary_status_list):
    for release_status in release_summary_status_list:
        print("% -25s % 25s % 25s % 25s" %(release_status.definition_name, release_status.release_name, release_status.approval_status, release_status.status))          

def check_if_tagged_release_exists (release, release_client, config):
    tagged_release_list = {}
    tagged_release_list = defaultdict(lambda:0,tagged_release_list)
    release_definitions = get_release_definitions(release, release_client, config)  #get list of release definitions
    for release_definition in release_definitions:
        get_release_response = get_tagged_release (release_definition, release, release_client, config)
        try:
            tagged_release_list[release_definition.name] = get_release_response.value[0].name
        except Exception as e:
            print("Validation Failed. Could not find tagged release of " + release_definition.name + " for VSTS Release tag " + config.vsts_tag_name)
            print("Exception: " + str(e))
            print("Occurred Method: " + inspect.currentframe().f_code.co_name)
            exit(1)