import functools
from abc import ABC

from stevedore import extension


class EasternPlugin(ABC):
    def line_pre_hook(self, ext, line, formatter, **kwargs):
        return line

    def line_post_hook(self, ext, line, formatter, **kwargs):
        return line

    def command_hook(self, ext, command, arg, formatter, **kwargs):
        pass

    def format_pre_hook(self, ext, body, formatter, **kwargs):
        return body

    def format_post_hook(self, ext, body, formatter, **kwargs):
        return body

    def cli_hook(self, ext, cli, **kwargs):
        pass

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


class ExtensionChainManager(ChainMixin, extension.ExtensionManager):
    pass


command_registry = {}


def register_command(name, func):
    command_registry[name] = func


@functools.lru_cache(None)
def get_plugin_manager():
    return ExtensionChainManager(
        namespace='eastern.plugin', invoke_on_load=True)


@functools.lru_cache(None)
def get_cli_manager():
    return extension.ExtensionManager(namespace='eastern.cli')
