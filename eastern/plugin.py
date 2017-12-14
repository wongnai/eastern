from abc import ABC

from stevedore import extension


class EasternPlugin(ABC):
    def line_pre_hook(self, ext, line, formatter):
        return line

    def line_post_hook(self, ext, line, formatter):
        return line

    def command_hook(self, ext, command, arg, formatter):
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


manager = ExtensionChainManager(
    namespace='eastern.plugin', invoke_on_load=True)
