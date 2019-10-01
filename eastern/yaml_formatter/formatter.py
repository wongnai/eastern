import logging
import os
import re

from stevedore.driver import DriverManager
from stevedore.exception import NoMatches

from . import utils
from ..plugin import get_plugin_manager
from ..formatter import BaseFormatter

DRIVER_NS = 'eastern.command'


class Formatter(BaseFormatter):
    """
    :param str raw: Template string
    :param str path: Path to template
    :param dict[str,str] env: List of variables
    """
    logger = logging.getLogger(__name__)

    def __init__(self, raw, path='', env=None):
        super().__init__(raw, path, env)
        self.plugin = get_plugin_manager()

        envs = self.plugin.map_method('env_hook', formatter=self)

        for item in envs:
            self.env.update(**item)

    def format(self):
        """
        :return: Formatted template
        """
        self.body = self.raw
        self.body = self.plugin.chain('format_pre_hook',
                                      self.body,
                                      formatter=self)
        self.body = self.interpolate_env(self.body)
        self.body = self.parse_lines(self.body)
        self.body = self.plugin.chain('format_post_hook',
                                      self.body,
                                      formatter=self)

        return self.body

    def interpolate_env(self, text):
        return re.sub(r'\${([^}]+)}', self.replace_env, text)

    def replace_env(self, match):
        key = match.group(1)
        if key in self.env:
            return self.env[key]
        else:
            self.logger.warning('Interpolated variable not found: %s', key)
            return match.group()

    def parse_lines(self, body):
        body_lines = body.split(os.linesep)
        return os.linesep.join(
            utils.flatten([self.parse_line(line) for line in body_lines]))

    def parse_line(self, line):
        if '#' not in line:
            return line

        line = self.plugin.chain('line_pre_hook', line, formatter=self)
        before, after = line.split('#', 1)

        # line must only have precending spaces
        if not re.match(r'^\s*$', before):
            return line

        splitted = after.strip().split(' ', 1)
        command = splitted[0]
        args = []

        if len(splitted) > 1:
            args = splitted[1]

        try:
            func = DriverManager(DRIVER_NS, command)
            func.propagate_map_exceptions = True
        except NoMatches:
            self.logger.debug('Command not found %s', command, exc_info=True)
            return line

        output = func(lambda ext: ext.plugin(args, line=line, formatter=self))

        if output is None:
            output = []
        elif isinstance(output, str):
            output = output.split(os.linesep)

        output = os.linesep.join([before + item for item in output])

        output = self.plugin.chain('line_post_hook', output, formatter=self)
        return output
