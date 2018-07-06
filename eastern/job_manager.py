import time
import logging

from .timeout import ProcessTimeout

logger = logging.getLogger(__name__)


class JobManager(object):
    def __init__(self, kubectl, job_name):
        self.kubectl = kubectl
        self.job_name = job_name

    def is_pod_scheduled(self):
        """
        Check is job pod was scheduled by looking at number of job active, succeeded and failed

        :rtype: bool
        """
        status = self.kubectl.get_job_status(self.job_name)
        return status.active + status.failed + status.succeeded > 0

    def wait_pod_scheduled(self, timeout_second=10):
        """
        Check every 1 second to see if pod was scheduled, you can specify maximum timeout in second

        :param timeout_second int: time to wait in seconds, default is to wait for 10 seconds
        :raises: JobTimedOutException in case that pod was not scheduled and over time limit
        """
        if not timeout_second:
            timeout_second = 10

        try:
            retry(lambda: self.is_pod_scheduled(), count=timeout_second)
        except RetryLimitReached:
            raise JobTimedOutException("pod not scheduled in time")

    def is_completed(self):
        """
        Check if job was completed and was not care whether a job was succeeded or failed.

        :rtype: bool
        """
        status = self.kubectl.get_job_status(self.job_name)
        return (status.failed + status.succeeded > 0) and status.active == 0

    def wait_completion(self, idle_timeout=None):
        """
        Wait until job was completed.

        :param idle_timeout int: time to wait in seconds
        """
        if not self.is_pod_scheduled():
            raise JobOperationException(
                "Wait for completion must run after pod was scheduled")

        pod_names = self.get_pod_names()
        for pod_name in pod_names:
            if self.is_completed():
                return

            # wait for pod phrase to be ready before tail log
            retry(lambda: is_pod_phrase_can_get_log(
                self.kubectl.get_pod_phase(pod_name)))

            args = self.kubectl.get_launch_args() + ['logs', '-f', pod_name]
            ProcessTimeout(idle_timeout, *args).run_sync()

    def get_pod_name(self):
        """
        Get pod name, if there are multiple pods, return the first one (lexicological sort)

        :rtype: str
        :raises JobNotFound: If no pod for that job is found
        """
        return self.get_pod_names()[0]

    def get_pod_names(self):
        """
        Get pod names, ordered by lexicological

        :rtype: list
        :raises JobNotFound: If no pod for that job is found
        """
        names_str = self.kubectl.get_job_pod_name(self.job_name)
        names = names_str.split()
        names.sort()
        return names

    def remove(self):
        """
        Delete job

        :raises JobOperationException: if delete job exit code was not 0 (succeeded)
        """
        exit_code = self.kubectl.delete_job(self.job_name)
        if exit_code != 0:
            raise JobOperationException(
                "remove job {name} failed, exit code {exit_code}".format(name=self.job_name, exit_code=exit_code))


def retry(bool_fn, count=10, interval=1):
    while count > 0:
        result = bool_fn()
        if result:
            return
        count = count - 1
        time.sleep(interval)  # second to sleep
    raise RetryLimitReached()


def is_pod_phrase_can_get_log(phrase):
    logger.debug('Pod phrase: %s', phrase)
    return phrase and phrase.lower() in ["running", "succeeded", "failed"]


class JobOperationException(Exception):
    pass


class JobTimedOutException(Exception):
    pass


class RetryLimitReached(Exception):
    pass
