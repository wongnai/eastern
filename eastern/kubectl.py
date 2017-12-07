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

        return process

    def rollout_wait(self, name):
        return subprocess.call(self.get_launch_args() + [
            'rollout',
            'status',
            name,
        ])
