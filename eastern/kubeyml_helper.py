import yaml
import struct
from pathlib2 import Path

class RollingResources(struct.Struct):
    def __init__(self, yml):
        self.yml = yml

    @property
    def name(self):
        return "{}/{}".format(self.yml['kind'], self.yml['metadata']['name'])

    @property
    def namespace(self):
        if 'namespace' in self.yml['metadata']:
            return self.yml['metadata']['namespace']
        return None

def __is_rolling_resource(doc):
    if 'kind' not in doc:
        return False

    return doc['kind'] in ['Deployment', 'ReplicationController', 'ReplicaSet']

def get_supported_rolling_resources(yaml_path):
    text = Path(yaml_path).read_text()
    # print text
    yml = yaml.load_all(text)
    results = []
    for doc in yml:
        if __is_rolling_resource(doc):
            results.append(RollingResources(doc))
    return results
