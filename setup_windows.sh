#!/bin/sh

# *******************************************************************
# * Author: 2024 Luigi Pizzolito (@https://github.com/Luigi-Pizzolito)
# *******************************************************************

# navigate to this scripts directory
cd "$(dirname "$0")" || exit
cd docker-template

# remove old docker-compose.yml if it exists
if [ -f "../docker-compose.yml" ]; then
    rm ../docker-compose.yml
fi

# create and activate VENV
echo "setup.sh: Entering Python VENV"
if [ ! -d "venv" ]; then
    python -m venv venv
fi
source venv/Scripts/activate

# install Jinja
echo "setup.sh: Satisfying requirements"
# export SOCKS_PROXY=socks5://10.197.88.68:10808
pip install Jinja2

# run Jinja template
echo "setup.sh: Creating docker-compose.yml template"
python generate_template.py

# suggest run
echo "setup.sh: Execute the following command to launch:"
echo "docker compose up --build"