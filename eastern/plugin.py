import functools
from abc import ABC

from stevedore import extension
from stevedore.exception import NoMatches


class EasternPlugin(ABC):
    def env_hook(self, ext, formatter, **kwargs):
        return {}

    def line_pre_hook(self, ext, line, formatter, **kwargs):
        return line

    def line_post_hook(self, ext, line, formatter, **kwargs):
        return line

    def format_pre_hook(self, ext, body, formatter, **kwargs):
        return body

    def format_post_hook(self, ext, body, formatter, **kwargs):
        return body

    def deploy_pre_hook(self, manifest, ctx, **kwargs):
        return manifest

    def deploy_post_hook(self, manifest, ctx, **kwargs):
        pass


class ChainMixin:
    def chain(self, func, value, *args, **kwargs):
        for extension in self:
            value = getattr(extension.obj, func)(extension, value, *args,
                                                 **kwargs)

        return value


class MapIgnoreEmptyMixin:
    def map(self, *args, **kwargs):
        try:
            return super().map(*args, **kwargs)
        except NoMatches:
            return []


class ExtensionChainManager(ChainMixin, MapIgnoreEmptyMixin,
                            extension.ExtensionManager):
    pass


class ExtensionMayEmptyManager(MapIgnoreEmptyMixin,
                               extension.ExtensionManager):
    pass


@functools.lru_cache(None)
def get_plugin_manager():
    return ExtensionChainManager(
        namespace='eastern.plugin', invoke_on_load=True)


@functools.lru_cache(None)
def get_cli_manager():
    return ExtensionMayEmptyManager(namespace='eastern.cli')
