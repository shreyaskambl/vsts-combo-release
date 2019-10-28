from lib.project import Project
from lib.releasedefinition import ReleaseDefinition
import pprint, time, logging, sys, os, util
from lib.RuntimeConfiguration import RuntimeConfiguration

logging.basicConfig(level=logging.INFO, format='%(message)s')
config = RuntimeConfiguration("config.json")
personal_access_token=os.environ["VSTS_PAT_TOKEN"]

def validation (release, release_client, config):
    util.check_if_tagged_release_exists (release, release_client, config)

def main():
    project = Project(config.vsts_project_name)
    release = ReleaseDefinition()
    release_client = util.get_release_client(project, release, personal_access_token, config)

    validation(release, release_client, config)
    release_summary_status_list = util.loop_through_release_definitions_to_trigger_release(release, release_client, config)
    
    util.output_release_status(release_summary_status_list)

if __name__ == "__main__":
    main()