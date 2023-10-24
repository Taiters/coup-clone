BLACK=black -l 120 server
format:
	python -m isort server
	${BLACK}

lint:
	${BLACK} --check
	flake8 --config server/setup.cfg server

mypy:
	mypy --config-file server/setup.cfg server/app.py

install:
	python -m pip install --upgrade pip
	pip install -r server/requirements.txt

run_server:
	COUP_ALLOW_ORIGINS="*" python server/app.py

run_client:
	cd client && REACT_APP_SOCKET_ADDR="http://localhost:8080" npm run start