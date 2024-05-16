#!/bin/bash

device="AVOCADO"
DEVICE_ADDR="avocado.enerzai.com"
DB_UPLOADER_URL="avocado.enerzai.com"
PORT=22

cd uploader
pip install -e .

cd ../

ssh-keyscan -t rsa $DEVICE_ADDR >> /root/.ssh/known_hosts
python ci/run.py --device $device