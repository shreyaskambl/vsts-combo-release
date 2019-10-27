import json

class RuntimeConfiguration:

    def __init__(self, path):
        with open( path, 'r') as f:
            dynamic_config = json.load(f)
        self._config = {
            **dynamic_config,
         }
         
    @property
    def vsts_project_name(self):
        return self._config['vsts_project_name']

    @property
    def organization_url(self):
        return self._config['organization_url']

    @property
    def environment_name(self):
        return self._config['environment_name']

    @property
    def manual_environments(self):
        return self._config['manual_environments']

    @property
    def pdi_services_list(self):
        return self._config['pdi_services_list']

    @property
    def vsts_tag_name(self):
        return self._config['vsts_tag_name']