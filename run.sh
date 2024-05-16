#!/bin/bash

device="AVOCADO"
url="avocado.enerzai.com"
port=22

cd uploader
pip install -e .

cd ../
python ci/run.py --device AVOCADO