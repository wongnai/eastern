from pathlib import Path

from eastern import kubeyml_helper

TEST_ROOT = (Path(__file__).parents[1]) / 'test_data' / 'kubeyml_helper'


def test_get_supported_rolling_resources():
    yaml_file = TEST_ROOT / 'sentry.yaml'
    resources = kubeyml_helper.get_supported_rolling_resources(
        yaml_file.open().read())

    assert len(resources) == 1

    resource = resources[0]
    assert resource.name == "Deployment/sentry"
    assert resource.namespace == "production"
