#!/bin/bash
git pull
docker-compose up -d
docker exec django python manage.py collectstatic --noinput
curl -H "X-Rollbar-Access-Token: "$(cat .env.prod | grep ROLLBAR_TOKEN | cut -d "=" -f 2)"" -H "Content-Type: application/json" -X POST 'https://api.rollbar.>
echo 'Deploy completed!'
