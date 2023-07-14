BLACK=black -l 120 coup_clone
format:
	python -m isort coup_clone
	${BLACK}

lint:
	${BLACK} --check
	flake8 coup_clone/

mypy:
	mypy -p coup_clone

test: lint mypy
	pytest tests

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
