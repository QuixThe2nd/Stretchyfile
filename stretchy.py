import sys
import re
import os


if len(sys.argv) < 2 or sys.argv[1].startswith('-'):
    stretchyfile_path = 'Stretchyfile'
else:
    stretchyfile_path = sys.argv[1]

if '-V' in sys.argv:
    verbose = True
    print('Verbose mode enabled')
    # Check next arg to see if comment mode is enabled
    if len(sys.argv) > sys.argv.index('-V') + 1 and sys.argv[sys.argv.index('-V') + 1] == 'comment':
        verbose_comment = True
        print('Comment mode enabled')
    else:
        verbose_comment = False
        print('Print mode disabled')
else:
    verbose = False
    verbose_comment = False

# Check if Stretchyfile exists
if not os.path.isfile(stretchyfile_path):
    print('Stretchyfile not found')
    exit()

with open(stretchyfile_path, 'r') as file:
    stretchyfile = file.read()


variables = {}
caddyfile = ""

def log(*args):
    global verbose, verbose_comment, caddyfile
    if verbose:
        for arg in args:
            if arg is not None:
                if verbose_comment:
                    caddyfile += '# VERBOSE: ' + ' '.join(str(arg).splitlines()) + '\n'
                else:
                    print(arg, end=' ')
        if not verbose_comment:
            print()


line_number = 0
conditions = 0
open_condition = False
condition = None
for line in stretchyfile.splitlines():
    line_number += 1
    if line.strip().startswith('if'):
        condition = line[line.find('(') + 1:line.rfind(')')]
        line = '@condition' + str(conditions) + ' {\n ' + condition.replace('&&', '\n') + '\n}\nhandle @condition' + str(conditions) + ' {\n'
        conditions += 1
        open_condition = True
    # Close condition
    elif open_condition and '}' in line:
        open_condition = False
        if line.count('}') == line.count('{') and 'else' in line:
            line = line.replace('else', '\n@condition' + str(conditions) + ' {\n not {\n' + condition.replace('&&', '\n') + '\n}\n}\nhandle @condition' + str(conditions) + ' ')
    if line.startswith("$"):  # Stretchy
        if not verbose_comment:
            log('--------------------------------\n\n\n\n--------------------------------\nLine:', line_number)
        line = line[1:]  # Remove $
        # If first char is a space, add a space to fix indentation issues caused by the removal of $
        if line.startswith(' '):
            line = ' ' + line
        if '=' in line:  # Variable Assignment
            name, value = line.split('=')
            name = name.strip()
            value = value.strip()
            log('\nVariable Assigned:', name, value)
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
                    log('\n----\nVariable Used:', name, value)
                    # Count occurrences of {name} in line - This is done for many-to-many relationships between domains and ports
                    count = line.count('{' + name + '}')
                    log('Variable Count:', count)
                    log('Variable Type:', 'Array ' if ',' in value else 'Single ')
                    for i in range(count):
                        if ',' in value:
                            values = value.split(',')
                            # Trim spaces from values
                            for i in range(len(values)):
                                values[i] = values[i].strip()
                            previous_char = line[line.find('{' + name + '}') - 1]
                            next_char = line[line.find('{' + name + '}') + len(name) + 2]
                            join = ', '
                            if previous_char == '.':
                                # print all chars before {name} until a space is found
                                # This specifies the subdomain(s) if any
                                join += line[:line.find('{' + name + '}')].split(' ')[-1]
                            elif previous_char == ':':
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
                            log('\nReplacing: ' + '{' + name + '}\nWith: ' + join.join(values) + '\nBefore: ' + line + '\nAfter: ' + line.replace('{' + name + '}', join.join(values), 1))
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

caddy_exec_path = os.popen('which caddy').read().strip()
os.exec(caddy_exec_path + ' fmt --overwrite ' + caddyfile_path)