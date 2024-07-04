# Variables
HEROKU_APP_NAME := food-recipes-test-1

# Default target
.PHONY: all
all: push release

# Login to Heroku container registry
.PHONY: login
login:
	@echo "Logging in to Heroku Container Registry..."
	heroku login
	heroku container:login

# Build Docker image and push it to Heroku registry
.PHONY: push
push:
	@echo "Pushing Docker image to Heroku..."
	heroku container:push web --app $(HEROKU_APP_NAME)

# Release the Docker image on Heroku
.PHONY: release
release:
	@echo "Releasing Docker image on Heroku..."
	heroku container:release web --app $(HEROKU_APP_NAME)

# Open the Heroku app in the browser
.PHONY: open
open:
	@echo "Opening the Heroku app in the browser..."
	heroku open --app $(HEROKU_APP_NAME)

# Create Heroku app and Postgres DB
.PHONY: create-app
create-app:
	@echo "Creating Heroku app..."
	heroku apps:create $(HEROKU_APP_NAME)

	@echo "Creating Postgres DB..."
	heroku addons:create heroku-postgresql:essential-0 -a $(HEROKU_APP_NAME)

	@echo "IMPORTANT: Make sure that the DB creating process is completed."
	@echo "Execute the full 'heroku addons:info ...' command from the previous output until you see 'State: created'."

# Create DB tables and admin accounts
.PHONY: create-db-tables
create-db-tables:
	@echo "Creating DB tables and admin accounts..."
	heroku run python manage.py create_db --app $(HEROKU_APP_NAME)
	heroku run python manage.py create_admins --app $(HEROKU_APP_NAME)
	heroku run python manage.py create_categories --app $(HEROKU_APP_NAME)

# Show logs
.PHONY: logs
logs:
	heroku logs --tail
