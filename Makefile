dev:
	docker-compose up --build

import:
	python app/db/importer/import_from_csv.py

test:
	pytest

fmt:
	black app tests

lint:
	ruff app tests