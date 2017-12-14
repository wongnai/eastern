import os

from ..plugin import register_command, EasternPlugin
from . import utils, formatter as fmt


def _load(args, formatter, required=False, **kwargs):
    file_list = args.split(',')
    override_file = utils.resolve_file(file_list, formatter.path)

    if not override_file:
        error = 'Cannot load ' + ', '.join(file_list)
        if required == True:
            raise OSError(error)
        else:
            return '# ' + error

    return fmt.format(override_file, env=formatter.env).split(os.linesep)


def load_strict(args, **kwargs):
    return _load(args, required=True, **kwargs)


class OverridePlugin(EasternPlugin):
    def __init__(self):
        register_command('load?', _load)
        register_command('load!', load_strict)
