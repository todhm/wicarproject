#!/bin/sh
# this script is used to boot a webapp in supervisor mode
pip install -r /home/hmmon/apps/wicarproject/requirements.txt

python /home/hmmon/apps/wicarproject/manage.py db upgrade

sudo supervisorctl restart wicarapp
sudo supervisorctl restart wicarcelery
sudo supervisorctl restart wicarbeat
