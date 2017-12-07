import json
import subprocess


class Kubectl:
    namespace = None
    context = None

    def __init__(self, path='kubectl'):
        self.path = path

    def get_launch_args(self):
        out = [self.path]

        if self.namespace:
            out.extend(['--namespace', self.namespace])

        if self.context:
            out.extend(['--context', self.context])

        return out

    def apply(self, file='-', data=None):
        process = subprocess.Popen(
            self.get_launch_args() + [
                'apply',
                '-f',
                file,
            ],
            stdin=subprocess.PIPE)

        process.communicate(data)

        return process.returncode

    def rollout_wait(self, name):
        return subprocess.call(self.get_launch_args() + [
            'rollout',
            'status',
            name,
        ])

    def get_job_pod_name(self, name):
        out = subprocess.check_output(self.get_launch_args() + [
            'get', 'pod', '-a', '--selector=job-name={}'.format(name), '-o',
            'jsonpath={.items..metadata.name}'
        ])

        if not out.strip():
            raise JobNotFound

        return out.decode('utf8')

    def get_pod_phase(self, name):
        return subprocess.check_output(self.get_launch_args(
        ) + ['get', 'pod', name, '-o', 'jsonpath={.status.phase}']).decode(
            'utf8')

    def get_pod_log(self, name):
        return subprocess.check_output(self.get_launch_args() + ['logs', name])

    def get_pod(self, name):
        return json.loads(
            subprocess.check_output(
                self.get_launch_args() + ['get', 'pod', name, '-o', 'json']))

    def delete_job(self, name):
        return subprocess.call(self.get_launch_args() + [
            'delete',
            'job',
            name,
        ])


class KubernetesException(Exception):
    pass


class JobNotFound(KubernetesException):
    pass
