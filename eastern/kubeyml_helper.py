import yaml


class RollingResources:

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


def is_rolling_resource(doc):
    if not doc or 'kind' not in doc:
        return False

    return doc['kind'] in ['Deployment', 'ReplicaSet', 'DaemonSet']


def get_supported_rolling_resources(text):
    yml = yaml.load_all(text)
    results = []
    for doc in yml:
        if is_rolling_resource(doc):
            results.append(RollingResources(doc))
    return results
