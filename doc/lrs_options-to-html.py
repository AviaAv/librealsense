with open('../CMake/lrs_options.cmake', 'r') as file:
    lines = file.readlines()

table_rows = []
in_cond = False
in_else = False
current_condition = None
current_comment = ""

for line in lines:
    if line.strip().startswith('option('):
        line = ' '.join(line.split())  # remove consecutive spaces
        parts = line.strip().split(' ')
        option = parts[0].strip('option(')
        description = ' '.join(parts[1:-1]).strip('"')
        if current_comment:
            description += " <span style='font-style: italic; color: #666;'>" + current_comment + "</span>"
            current_comment = ""
        value = parts[-1].strip(")")  # TODO should it be swapped to true/false ?
        if in_cond:
            value = f'ON if <b><code>{current_condition}</code></b><br/> OFF otherwise'
            if in_else:
                continue
        value = value.replace('ON', '<span style="color: #4CAF50;">ON</span>').replace('OFF', '<span style="color: #E74C3C;">OFF</span>')
        if in_cond:
            value = f'<span class="tooltip">Conditioned<span class="tooltip-text">{value}</span></span>'
        table_rows.append(f'\n      <tr>'
                          f'\n\t<td>\n\t  <b><code>{option}</code></b>'f'\n\t</td>'
                          f'\n\t<td>\n\t  {description}\n\t</td>'
                          f'\n\t<td>\n\t  {value}\n\t</td>'
                          f'\n      </tr>')

    elif line.startswith('if'):
        parts = line.strip().split('(', 1)
        condition = parts[1][:-1]  # remove last ) - part of the 'if' syntax
        current_condition = condition
        in_cond = True
    elif line.startswith('else'):
        in_else = True
    elif line.startswith('endif'):
        current_condition = None
        in_cond = False
        in_else = False
    elif line.startswith('##'):
        continue  # ignore internal comments
    elif line.startswith('#'):
        current_comment += line.strip('# \n')

html = f'''<!DOCTYPE html>
<html>
<head>
  <title>Build Customization Flags</title>
  <link rel="icon" href="icon.ico" type="image/icon type">
  <link rel="stylesheet" href="build-flags.css">
</head>
<body>
  <div class="container">
    <h1>Intel RealSense™ SDK Build Customization Flags</h1>
    <table>
      <tr>
        <th style="width: 30%">Option</th>
        <th style="width: 55%">Description</th>
        <th style="width: 15%">Default</th>
      </tr>{''.join(table_rows)}
    </table>
  </div>
</body>
</html>
'''

with open('build-flags.html', 'w') as file:
    file.write(html)
