### Frontend part

FROM refinedev/node:18 AS frontendbuilder

COPY admin-dashboard/package.json admin-dashboard/package-lock.json* admin-dashboard/.npmrc* ./

RUN npm ci

ENV NODE_ENV production

COPY admin-dashboard/ ./

RUN npm run build


### Backend part

FROM python:3.11.3-slim-buster as backendrunner

WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
ENV FLASK_DEBUG 0

RUN apt-get update && apt-get install -y netcat

RUN pip install --upgrade pip
COPY backend/requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY backend/ /usr/src/app/

COPY --from=frontendbuilder /app/refine/dist/ /usr/src/app/static/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
CMD gunicorn -w 2 -b 0.0.0.0:$PORT food_recipe:app
