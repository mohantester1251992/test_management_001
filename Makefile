.PHONY: install fmt lint test runserver celery worker beat migrate

install:
	pip install -r requirements.txt

fmt:
	black .
	isort .

lint:
	flake8
	mypy backend

test:
	pytest

runserver:
	python manage.py runserver 0.0.0.0:8000

celery:
celery -A backend worker -l info -Q orchestrator,runner

worker:
celery -A backend worker -l info -Q runner

beat:
	celery -A backend beat -l info

migrate:
	python manage.py migrate
