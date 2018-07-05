import pytest

from eastern.job_manager import JobManager
from eastern import Kubectl
from unittest.mock import MagicMock

JOB_NAME = "test-job"
MULTI_POD_NAMES = "test-job-9vmlg test-job-2abcd"
SINGLE_POD_NAMES = "test-job-9vmlg"

@pytest.fixture
def kubectl():
    return MagicMock(Kubectl)

def test_get_pod_names(kubectl):
    kubectl = MagicMock(Kubectl)
    kubectl.get_job_pod_name.return_value = MULTI_POD_NAMES
    job_manager = JobManager(kubectl, JOB_NAME)
    assert job_manager.get_pod_names() == ["test-job-2abcd", "test-job-9vmlg"]

def test_get_pod_names_with_single_pod(kubectl):
    kubectl = MagicMock(Kubectl)
    kubectl.get_job_pod_name.return_value = SINGLE_POD_NAMES
    job_manager = JobManager(kubectl, JOB_NAME)
    assert job_manager.get_pod_names() == ["test-job-9vmlg"]

def test_get_pod_name(kubectl):
    kubectl = MagicMock(Kubectl)
    kubectl.get_job_pod_name.return_value = MULTI_POD_NAMES
    job_manager = JobManager(kubectl, JOB_NAME)
    assert job_manager.get_pod_name() == "test-job-2abcd"
