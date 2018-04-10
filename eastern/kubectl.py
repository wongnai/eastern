import json
import subprocess

from .timeout import ProcessTimeout

class Kubectl:
    """
    Kubernetes CLI wrapper

    :param str path: Path to kubectl (or command name if in path)
    """
    #: Current namespace (default to omit parameter)
    namespace = None
    #: Current context (default to omit parameter)
    context = None

    def __init__(self, path='kubectl'):
        self.path = path

    def get_launch_args(self):
        """
        Get kubectl command line

        eg. ``['kubectl', '--namespace', 'production', '--context', 'production']``
        
        :rtype: list[str]
        """
        out = [self.path]

        if self.namespace:
            out.extend(['--namespace', self.namespace])

        if self.context:
            out.extend(['--context', self.context])

        return out

    def apply(self, file='-', data=None):
        """
        Run :command:`kubectl apply`

        :param str file: Filename to apply, or ``-`` to apply from data
        :param str data: Manifest body to apply, only when ``file`` is ``-``
        :return: Return value of the command (0 for success)
        """
        process = subprocess.Popen(
            self.get_launch_args() + [
                'apply',
                '-f',
                file,
            ],
            stdin=subprocess.PIPE)

        process.communicate(data)

        return process.returncode

    def rollout_wait(self, name, timeout=None):
        """
        Run :command:`kubectl rollout status` and wait for exit

        :param str name: Deployment name to wait
        :return: Return value of the command (0 for success)
        """
        args = self.get_launch_args() + [
            'rollout',
            'status',
            name,
        ]

        if timeout:
            return ProcessTimeout(timeout, *args).run_sync()
        else:
            return subprocess.call(args)

    def get_job_pod_name(self, name):
        """
        Get the actual pod name of a job

        :param str name: Job name
        :return: Job name
        :raises JobNotFound: If no pod for that job is found
        """
        out = subprocess.check_output(self.get_launch_args() + [
            'get', 'pod', '-a', '--selector=job-name={}'.format(name), '-o',
            'jsonpath={.items..metadata.name}'
        ])

        if not out.strip():
            raise JobNotFound

        return out.decode('utf8')

    def get_pod_phase(self, name):
        """
        Get the phase of the pod

        :param str name: Pod name
        :return: `Pod phase <https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/>`_
        """
        return subprocess.check_output(self.get_launch_args(
        ) + ['get', 'pod', name, '-o', 'jsonpath={.status.phase}']).decode(
            'utf8')

    def get_pod_log(self, name):
        """
        Get pod's log

        :param str name: Pod name
        :rtype: str
        """
        return subprocess.check_output(self.get_launch_args() + ['logs', name])

    def get_pod(self, name):
        """
        Get pod's metadata

        :param str name: Pod name
        :rtype: dict
        """
        return json.loads(
            subprocess.check_output(
                self.get_launch_args() + ['get', 'pod', name, '-o', 'json']))

    def delete_job(self, name):
        """
        Delete a job

        :param str name: Job name
        :return: Return value (0 for success)
        """
        return subprocess.call(self.get_launch_args() + [
            'delete',
            'job',
            name,
        ])


class KubernetesException(Exception):
    pass


class JobNotFound(KubernetesException):
    """
    Cannot find the given job
    
    Raised by :py:func:`Kubectl.get_job_pod_name`
    """
    pass
