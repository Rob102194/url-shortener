up:
	docker-compose up --build

test:
	docker-compose run --rm api pytest
