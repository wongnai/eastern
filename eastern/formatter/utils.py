import collections
from pathlib import Path


def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, str):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def resolve_file(files, base):
    '''Resolve a list of files to the first one that exists
    
    Returns a path object or None if no file exists'''
    if not isinstance(base, Path):
        base = Path(base)

    for file in files:
        file_obj = base / file.strip()
        if file_obj.exists():
            return file_obj
