from pathlib2 import Path
import os
import collections

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def map_override(line, path):
    if not line.find("# load!") > -1:
        return line

    # read file name
    splited_line = line.split("# load! ")
    override_file = splited_line[1]
    # get indent
    indent = splited_line[0]
    # read file
    override_text = Path(path + os.sep + override_file).read_text()
    # prepend indent
    override_file_lines = [indent + l for l in override_text.split(os.linesep)]
    # insert into file array
    return override_file_lines

def replace_with_env(file_text, env):
    for key in env:
        file_text = file_text.replace("${" + key + "}", env[key])
    return file_text

def format(filename, env = {}):
    file_text = replace_with_env(Path(filename).read_text(), env)
    dir_path = os.path.dirname(os.path.realpath(filename))
    file_text_array = file_text.split(os.linesep)
    new_file_text_array = flatten(map(lambda line : map_override(line, dir_path), file_text_array))

    return os.linesep.join(new_file_text_array)