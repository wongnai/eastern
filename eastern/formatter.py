from abc import ABC, abstractmethod
from pathlib import Path, PurePath

from stevedore.driver import DriverManager


class BaseFormatter(ABC):

    def __init__(self, raw, path='', env=None):
        self.raw = raw

        if not isinstance(path, PurePath):
            self.path = PurePath(path)
        else:
            self.path = path

        self.env = env or {}

    @abstractmethod
    def format(self):
        pass


def format(filename, env=None):
    """
    Format a file

    :param filename: Path to file
    :type filename: str or :py:class:`pathlib.Path`
    :param dict[str,str] env: List of variables
    """
    ext = str(filename).split('.')[-1]
    driver = DriverManager('eastern.formatter', ext)
    driver.propagate_map_exceptions = True
    env = env or {}

    if isinstance(filename, Path):
        file_obj = filename
    else:
        file_obj = Path(filename)

    body = file_obj.read_text()
    return driver(lambda ext: ext.plugin(body, file_obj.parent, env).format())
