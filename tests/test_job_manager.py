import pytest

from eastern.job_manager import JobManager
from eastern.kubectl import JobStatus
from eastern.timeout import ProcessTimeout
from eastern import Kubectl
from unittest.mock import MagicMock, patch

JOB_NAME = "test-job"
MULTI_POD_NAMES = "test-job-9vmlg test-job-2abcd"
SINGLE_POD_NAMES = "test-job-9vmlg"


@pytest.fixture
def kubectl():
    return MagicMock(Kubectl)

def test_get_pod_names(kubectl):
    kubectl.get_job_pod_name.return_value = MULTI_POD_NAMES
    job_manager = JobManager(kubectl, JOB_NAME)
    assert job_manager.get_pod_names() == ["test-job-2abcd", "test-job-9vmlg"]


def test_get_pod_names_with_single_pod(kubectl):
    kubectl.get_job_pod_name.return_value = SINGLE_POD_NAMES
    job_manager = JobManager(kubectl, JOB_NAME)
    assert job_manager.get_pod_names() == ["test-job-9vmlg"]


def test_get_pod_name(kubectl):
    kubectl.get_job_pod_name.return_value = MULTI_POD_NAMES
    job_manager = JobManager(kubectl, JOB_NAME)
    assert job_manager.get_pod_name() == "test-job-2abcd"


def test_wait_completion_success(kubectl):
    kubectl.get_job_pod_name.return_value = JOB_NAME
    kubectl.get_pod_phase.return_value = 'RUNNING'
    job_manager = JobManager(kubectl, JOB_NAME)
    kubectl.get_job_status.return_value = JobStatus({"active" : 0, "succeeded" : 1})
    job_manager.wait_completion()


@patch.object(ProcessTimeout, 'run_sync', MagicMock(return_value=None))
def test_wait_completion(kubectl): 
    kubectl.get_job_pod_name.return_value = JOB_NAME
    kubectl.get_pod_phase.return_value = 'RUNNING'

    job_manager = JobManager(kubectl, JOB_NAME)
    kubectl.get_job_status.side_effect = [ JobStatus({"active" : 1}), JobStatus({"active" : 1}), JobStatus({"active" : 0, "succeeded": 1}) ]
    
    job_manager.wait_completion()


