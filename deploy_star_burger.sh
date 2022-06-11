#!/bin/bash
set -e
source venv/bin/activate
git pull
pip install -r requirements.txt
npm ci --dev
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl restart star-burger.service
curl -H "X-Rollbar-Access-Token: "$(cat .env | grep ROLLBAR_TOKEN | cut -d "=" -f 2)"" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "product1", "revision":"'"$(git rev-parse HEAD)"'", "rollbar_name": "949027", "local_username": "user", "status": "succeeded"}'
echo 'Deploy completed!'
