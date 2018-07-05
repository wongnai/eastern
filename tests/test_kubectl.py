import pytest

from eastern import Kubectl
from unittest.mock import MagicMock, patch

@pytest.fixture
def job_response():
    return """
    {
        "status": {
            "completionTime": "2018-07-04T10:31:35Z",
            "conditions": [
                {
                    "lastProbeTime": "2018-07-04T10:31:35Z",
                    "lastTransitionTime": "2018-07-04T10:31:35Z",
                    "status": "True",
                    "type": "Complete"
                }
            ],
            "startTime": "2018-07-04T10:31:23Z",
            "succeeded": 1
        }
    }
    """

@pytest.fixture
def no_status_job_response():
    return '{}'

@patch('subprocess.check_output')
def test_get_job_status(check_output, job_response):
    check_output.return_value = job_response
    kubectl = Kubectl()
    status = kubectl.get_job_status("test-job")

    check_output.assert_called_with(['kubectl', 'get', 'job', 'test-job', '-o', 'json'])

    assert status.succeeded == 1
    assert status.active == 0
    assert status.failed == 0

@patch('subprocess.check_output')
def test_get_job_status_failed(check_output, no_status_job_response):
    check_output.return_value = no_status_job_response
    kubectl = Kubectl()

    with pytest.raises(KeyError):
        kubectl.get_job_status("test-job")
