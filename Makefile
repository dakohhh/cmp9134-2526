run:
	uvicorn app:app --reload

migrations:
	alembic revision --autogenerate -m $(message)

migrate:
	alembic upgrade head

compose:
	docker-compose -f docker-compose-dev.yaml up -d

compose-down:
	docker-compose -f docker-compose-dev.yaml down