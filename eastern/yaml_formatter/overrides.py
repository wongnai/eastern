import os

from . import utils
from .. import formatter as fmt


def load(args, formatter, required=False, **kwargs):
    file_list = args.split(",")
    override_file = utils.resolve_file(file_list, formatter.path)

    if not override_file:
        error = "Cannot load " + ", ".join(file_list)
        if required == True:
            raise OSError(error)
        else:
            return "# " + error

    return fmt.format(override_file, env=formatter.env).rstrip("\r\n")


def load_strict(args, **kwargs):
    return load(args, required=True, **kwargs)
