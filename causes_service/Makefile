PONY: help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

up:
	docker-compose up -d
	./manage.py runserver 0.0.0.0:8000

styles-watch:
	npx --yes tailwindcss -o static/css/ts-styles.css --watch --minify

styles-build:
	npx --yes tailwindcss -o static/css/ts-styles.css --minify

test: ## Run component tests
	pytest

migrate:
	./manage.py migrate

migrations:
	./manage.py makemigrations

format:
	ruff --fix .

generateschema:
	./manage.py generateschema --file openapi-schema.yml

createsuperuser:
	DJANGO_SUPERUSER_PASSWORD=admin ./manage.py createsuperuser --noinput --email admin@email.com

populate_search_indexes:
	./manage.py createMeilisearchIndex
	./manage.py populateMeilisearchIndex
