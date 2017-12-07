from pathlib import Path

from . import kubeyml_helper


def test_get_supported_rolling_resources():
    yaml_file = Path(__file__).parents[1] / "fixture/1.yaml"
    resources = kubeyml_helper.get_supported_rolling_resources(
        yaml_file.open().read())

    assert len(resources) == 1

    resource = resources[0]
    assert resource.name == "Deployment/wongnai-react"
    assert resource.namespace == "production"
