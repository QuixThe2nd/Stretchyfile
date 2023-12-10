import sys
import re


if len(sys.argv) < 2:
    stretchyfile_path = 'Stretchyfile'
else:
    stretchyfile_path = sys.argv[1]

with open(stretchyfile_path, 'r') as file:
    stretchyfile = file.read()


variables = {}
caddyfile = ""

for line in stretchyfile.splitlines():
    if line.startswith("$"):  # Stretchy
        line = line[1:]  # Remove $
        if '=' in line:  # Variable Assignment
            name, value = line.split('=')
            if '{' in value:
                # Variable Usage in Variable Assignment
                for name, new_value in variables.items():
                    if '{' + name + '}' in value:
                        # Count occurrences of {name} in value 1 - This is done for many-to-many relationships
                        count = value.count('{' + name + '}')
                        for i in range(count):
                            if ',' in new_value:
                                new_values = new_value.split(',')
                                # Get all chars to the left of {name} until a space or comma is found
                                pattern = r'([^ ,]+)\{' + re.escape(name) + r'\}'
                                join = ','
                                match = re.search(pattern, value)
                                if match:
                                    join += match.group(1)
                                    value = re.sub(pattern, match.group(1) + join.join(new_values), value, 1)
                                else:
                                    value = value.replace('{' + name + '}', join.join(new_values), 1)
                            else:
                                value = value.replace('{' + name + '}', new_value, 1)
            variables[name.strip()] = value.strip()
            continue
        else:  # Variable Usage
            for name, value in variables.items():
                if '{' + name + '}' in line:  # Replace Variable
                    # Count occurrences of {name} in line - This is done for many-to-many relationships between domains and ports
                    count = line.count('{' + name + '}')
                    for i in range(count):
                        if ',' in value:
                            values = value.split(',')
                            previous_char = line[line.find('{' + name + '}') - 1]
                            next_char = line[line.find('{' + name + '}') + len(name) + 2]
                            join = ', '
                            if previous_char == ':':
                                # print all chars before {name} until a space is found
                                # This specifies the domain if any, for a single domain to multiple port relationship
                                join += line[:line.find('{' + name + '}')].split(' ')[-1]
                            if next_char == ':':
                                # print all chars after {name} until a space or comma is found
                                # This specifies the port if any, for a single port to multiple domain relationship
                                pattern = r'\{' + re.escape(name) + r'\}([^ ,]+)'
                                match = re.search(pattern, line)
                                if match:
                                    join = match.group(1) + join
                            line = line.replace('{' + name + '}', join.join(values), 1)

                        else:
                            line = line.replace('{' + name + '}', value)

    if line.startswith('#') or line == '':
        continue
    caddyfile += line + '\n'

caddyfile_path = stretchyfile_path.split('/')
caddyfile_path.pop()
caddyfile_path.append('Caddyfile')
caddyfile_path = '/'.join(caddyfile_path)

with open(caddyfile_path, 'w') as file:
    file.write(caddyfile)
