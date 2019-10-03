import functools
from abc import ABC

from stevedore import extension
from stevedore.exception import NoMatches


class EasternPlugin(ABC):
    """
    Base class for all plugins
    """

    def env_hook(self, formatter, **kwargs):
        """
        Return a dict of additional environment values (equivalent to ``-s`` on command line)

        :param formatter: A formatter instance
        :type formatter: :py:class:`eastern.formatter.formatter.Formatter`
        :rtype: dict
        """
        return {}

    def line_pre_hook(self, line, formatter, **kwargs):
        """
        Preprocess a formatter line. The line will be given as-is.

        Must always return the resulting line.

        :param str line: A line of template
        :param formatter: A formatter instance
        :type formatter: :py:class:`eastern.formatter.formatter.Formatter`
        :rtype: str
        """
        return line

    def line_post_hook(self, line, formatter, **kwargs):
        """
        Postprocess a formatter line. The line will be given after all plugins has processed the line.

        Must always return the resulting line.

        :param str line: A line of template
        :param formatter: A formatter instance
        :type formatter: :py:class:`eastern.formatter.formatter.Formatter`
        :rtype: str
        """
        return line

    def format_pre_hook(self, body, formatter, **kwargs):
        """
        Preprocess a template. The template will be given as-is.

        Must always return the resulting template.

        :param str body: The whole template
        :param formatter: A formatter instance
        :type formatter: :py:class:`eastern.formatter.formatter.Formatter`
        :rtype: str
        """
        return body

    def format_post_hook(self, body, formatter, **kwargs):
        """
        Postprocess a template. The template will be given after all plugins has processed it.

        Must always return the resulting template.

        :param str body: The whole template
        :param formatter: A formatter instance
        :type formatter: :py:class:`eastern.formatter.formatter.Formatter`
        :rtype: str
        """
        return body

    def deploy_pre_hook(self, manifest, ctx, **kwargs):
        """
        Preprocess the manifest before deploying. Can also be used to run actions.

        Must always return the manifest.

        Available context objects:

        * ``ctx.obj['kubectl']``: An instance of :py:class:`eastern.kubectl.Kubectl`

        :param str manifest: Kubernetes manifest
        :param ctx: Click context
        :type ctx: `click.Context <http://click.pocoo.org/5/api/#context>`_
        :rtype: str
        """
        return manifest

    def deploy_post_hook(self, manifest, ctx, **kwargs):
        """
        Run actions after deployment succeeded

        Available context objects:

        * ``ctx.obj['kubectl']``: An instance of :py:class:`eastern.kubectl.Kubectl`

        :param str manifest: Kubernetes manifest
        :param ctx: Click context
        :type ctx: `click.Context <http://click.pocoo.org/5/api/#context>`_
        """
        pass


class ChainMixin:
    def chain(self, func, value, *args, **kwargs):
        for extension in self:
            value = getattr(extension.obj, func)(value, *args, **kwargs)

        return value


class MapIgnoreEmptyMixin:
    def map(self, *args, **kwargs):
        try:
            return super().map(*args, **kwargs)
        except NoMatches:
            return []


class ExtensionChainManager(
    ChainMixin, MapIgnoreEmptyMixin, extension.ExtensionManager
):
    pass


class ExtensionMayEmptyManager(MapIgnoreEmptyMixin, extension.ExtensionManager):
    pass


@functools.lru_cache(None)
def get_plugin_manager():
    return ExtensionChainManager(namespace="eastern.plugin", invoke_on_load=True)


@functools.lru_cache(None)
def get_cli_manager():
    return ExtensionMayEmptyManager(namespace="eastern.cli")
