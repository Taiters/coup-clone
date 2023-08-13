BLACK=black -l 120 server
format:
	python -m isort server
	${BLACK}

lint:
	${BLACK} --check
	flake8 --config server/setup.cfg server

mypy:
	mypy --config-file server/setup.cfg server/app.py

test: lint mypy
	pytest server/tests

install:
	python -m pip install --upgrade pip
	pip install -r server/requirements.txt
