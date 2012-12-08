import re
import yaml

"""
A yaml loader that preserves top level element order.
"""

def load(filename):
    with open(filename, 'r') as file:
        yaml_data = []
        yaml_str = ""

        for line in file:
            # discard comments
            if line[0] == "#":
                continue

            # top level
            if re.search(r'\w', line[0]):
                this_yaml = yaml.load(yaml_str)
                if this_yaml is not None:
                    yaml_data.append(this_yaml)

                yaml_str = line
            else:
                yaml_str += line

        this_yaml = yaml.load(yaml_str)
        if this_yaml is not None:
            yaml_data.append(this_yaml)

    return yaml_data
