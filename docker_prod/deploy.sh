#!/bin/bash
git pull
docker-compose up -d
docker exec django python manage.py collectstatic --noinput
curl -H "X-Rollbar-Access-Token: "$(cat .env | grep ROLLBAR_TOKEN | cut -d "=" -f 2)"" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "product", "revision":"'"$(git rev-parse HEAD)"'", "status": "succeeded"}'
echo 'Deploy completed!'
