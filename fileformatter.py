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

def resolve_load_file(path, override_file_path):
    default_override_file = False
    if "," in override_file_path:
        argv = override_file_path.split(",")
        override_file_path = argv[0].strip()
        default_override_file = argv[1].strip()

    # do nothing when no override file found
    override_file = Path(path + os.sep + override_file_path)
    if not override_file.exists():
        if not default_override_file:
            return False
        override_file = Path(path + os.sep + default_override_file)
        if not override_file.exists():
            return False

    return override_file

def map_override(line, path, env):
    require_sep = "# load!"
    optional_sep = "# load?"

    if line.find(require_sep) > -1:
        required = True
        sectionSeperator = require_sep + " "
    elif line.find(optional_sep) > -1:
        required = False
        sectionSeperator = optional_sep + " "
    else:
        return line

    # read file name
    splited_line = line.split(sectionSeperator)
    override_file_path = splited_line[1]

    override_file = resolve_load_file(path, override_file_path)

    if not override_file:
        if required == True:
            raise Exception("Override file not found: " + override_file_path)
        else:
            return line

    # get indent
    indent = splited_line[0]
    # read file
    override_text = format(str(override_file), env)
    # prepend indent
    override_file_lines = [indent + l for l in override_text.split(os.linesep)]
    # insert into file array
    return override_file_lines

prod_mark_file_name = os.path.join(os.path.dirname(__file__), 'projects', 'production.yaml')
prod_ns = ('prod', 'staging')
def map_prod_mark(line, path, env):
    is_prod = False
    for ns in prod_ns:
        if ns in env['NAMESPACE']:
            is_prod = True
            break

    if not is_prod:
        return line.replace('# mark_prod', '# mark_prod ignored as this is not production')

    pos = line.find('# mark_prod')
    if pos == -1:
        return line

    indent = ' ' * pos
    override_text = format(prod_mark_file_name, env)

    override_file_lines = [indent + l for l in override_text.split(os.linesep)]
    return override_file_lines

def line_map(line, path, env):
    out = map_override(line, path, env)
    out = map_prod_mark(line, path, env)

    return out

def replace_with_env(file_text, env):
    for key in env:
        file_text = file_text.replace("${" + key + "}", env[key])
    return file_text

def format(filename, env = {}):
    file_text = replace_with_env(Path(filename).read_text(), env)
    dir_path = os.path.dirname(os.path.realpath(filename))
    file_text_array = file_text.split(os.linesep)
    new_file_text_array = flatten(map(lambda line : line_map(line, dir_path, env), file_text_array))

    return os.linesep.join(new_file_text_array)