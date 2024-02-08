#!/usr/bin/fish


virtualenv -p /usr/bin/python3 venv
. venv/bin/activate.fish

pip install hjson

sudo python3 run.py
