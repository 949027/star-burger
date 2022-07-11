# syntax=docker/dockerfile:1

FROM node:14 AS parcel

WORKDIR star-burger

COPY bundles-src bundles-src
COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm ci --dev

CMD [ "./node_modules/.bin/parcel", "build", "bundles-src/index.js", "--dist-dir", "bundles", "--public-url", "./"]

FROM python:3.8-slim-buster AS django

WORKDIR star-burger

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

FROM nginx:1.23.0-alpine AS nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY production/nginx.conf /etc/nginx/conf.d/
