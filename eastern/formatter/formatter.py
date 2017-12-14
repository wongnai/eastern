import re
import os
from pathlib import PurePath, Path

from ..plugin import manager, command_registry
from . import utils


class Formatter:
    def __init__(self, raw, path='', env={}):
        self.raw = raw

        if not isinstance(path, PurePath):
            self.path = PurePath(path)
        else:
            self.path = path

        self.env = env

    def format(self):
        self.body = self.raw
        self.body = manager.chain('format_pre_hook', self.body, formatter=self)
        self.body = self.interpolate_env(self.body)
        self.body = self.parse_lines(self.body)
        self.body = manager.chain(
            'format_post_hook', self.body, formatter=self)

        return self.body

    def interpolate_env(self, text):
        for key, value in self.env.items():
            text = text.replace("${" + key + "}", value)

        return text

    def parse_lines(self, body):
        body_lines = body.split(os.linesep)
        return os.linesep.join(
            utils.flatten([self.parse_line(line) for line in body_lines]))

    def parse_line(self, line):
        if '#' not in line:
            return line

        line = manager.chain('line_pre_hook', line, formatter=self)
        before, after = line.split('#', 1)

        # line must only have precending spaces
        if not re.match(r'^\s*$', before):
            return line

        splitted = after.strip().split(' ', 1)
        command = splitted[0]
        args = []

        if len(splitted) > 1:
            args = splitted[1]

        if command not in command_registry:
            return line

        output = command_registry[command](args, line=line, formatter=self)

        if not isinstance(output, list):
            output = [output]

        output = os.linesep.join([before + item for item in output])

        output = manager.chain('line_post_hook', output, formatter=self)
        return output


def format(filename, env={}):
    if isinstance(filename, Path):
        file_obj = filename
    else:
        file_obj = Path(filename)
    body = file_obj.read_text()
    return Formatter(body, file_obj.parent, env).format()
