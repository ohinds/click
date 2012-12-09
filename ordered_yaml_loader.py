import re
import yaml

"""
A yaml loader for clicks.
"""

def _calculate_depth(entry, parent_depth):
    try:
        max_depth = 0
        for val in entry.itervalues():
            depth = _calculate_depth(val, parent_depth + 1)
            if depth > max_depth:
                max_depth = depth
        return max_depth + parent_depth
    except:
        pass
    return 0

def _expand_repeats(yaml_str, yaml_data):
    entry = yaml.load(yaml_str)
    depth = _calculate_depth(entry, 0)
    if (depth < 2):
        if entry is not None:
            yaml_data.append(entry)
        return

    entry_val = entry.values()[0]

    name = entry.keys()[0]
    repeats = entry_val["repeats"]

    part_str = ""
    parts = []
    for line in yaml_str.split("\n"):        
        if len(line) < 1 or re.search(r"\w", line[0]) or re.search(r"repeats:", line):
            continue
        if re.search(r"  \w", line[0:3]):
            part = yaml.load(part_str)
            if part is not None:
                parts.append(part)
            part_str = ""
        else:
            part_str += (line + "\n")

    part = yaml.load(part_str)
    if part is not None:
        parts.append(part)

    for i in xrange(repeats):
        for j, part in enumerate(parts):
            yaml_data.append({"%s_%d_%d" % (name, i, j): part})

    return 

def load(filename):
    with open(filename, 'r') as file:
        yaml_data = []
        yaml_str = ""

        for line in file:
            # discard comments
            if line[0] == "#":
                continue

            # top level
            if re.search(r"\w", line[0]):
                _expand_repeats(yaml_str, yaml_data)
                yaml_str = line
            else:
                yaml_str += line

        _expand_repeats(yaml_str, yaml_data)

    return yaml_data
