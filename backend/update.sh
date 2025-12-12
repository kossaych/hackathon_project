#!/bin/bash
cd ~/your-repo/backend
git reset --hard
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
touch yourapp_wsgi.py
