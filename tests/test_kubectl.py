import pytest

from eastern import Kubectl
from unittest.mock import MagicMock, patch

JOB_RESPONSE = """
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

NO_STATUS_JOB_RESPONSE = '{}'


@patch('subprocess.check_output')
def test_get_job_status(check_output):
    check_output.return_value = JOB_RESPONSE
    kubectl = Kubectl()
    status = kubectl.get_job_status("test-job")

    check_output.assert_called_with(
        ['kubectl', 'get', 'job', 'test-job', '-o', 'json'])

    assert status.succeeded == 1
    assert status.active == 0
    assert status.failed == 0


@patch('subprocess.check_output')
def test_get_job_status_failed(check_output):
    check_output.return_value = NO_STATUS_JOB_RESPONSE
    kubectl = Kubectl()

    with pytest.raises(KeyError):
        kubectl.get_job_status("test-job")
