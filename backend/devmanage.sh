#!/bin/sh

dotenv -f .env.dev run python manage.py $@
