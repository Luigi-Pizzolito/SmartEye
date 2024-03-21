import os
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape

# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# load environment variables from .env file
print("generate_template.py: parsing configuration .env file")
with open('../config.env') as f:
    for line in f:
        # skip empty lines and comments
        if not line.strip() or line[0] == '#':
            continue

        # remove mid-line comments
        line = line.split('#')[0]

        # split line by '='
        envvars = line.strip().split('=')

        # process key-value pairs
        for i in range(0, len(envvars), 2):
            key = envvars[i].strip()
            value = envvars[1].strip() if i+1 < len(envvars) else ''
            print("generate_template.py: found var: "+key+"="+value)
            os.environ[key] = value
    # print(os.environ)

# create Jinja environment
env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['yml'])
)

# load the Jinja template
template = env.get_template('docker-compose.yml.jinja')

# render the template with environment variables
rendered_template = template.render(env=os.environ)

# save template to file
with open('../docker-compose.yml', 'w') as f:
    f.write(rendered_template)
print("generate_template.py: rendered docker-compose.yml template.")