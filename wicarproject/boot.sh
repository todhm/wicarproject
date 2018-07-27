#!/bin/sh
# this script is used to boot a Docker container
pip install -r /home/hmmon/apps/wicarproject/requirements.txt

python /home/hmmon/apps/wicarproject/manage.py db upgrade

sudo supervisorctl restart wicarapp
sudo supervisorctl restart wicarcelery
sudo supervisorctl restart wicarbeat
