BLACK=black -l 120 -t py36 app.py coup_clone
format:
	isort app.py coup_clone
	${BLACK}

lint:
	${BLACK} --check
	flake8 app.py coup_clone/

mypy:
	mypy -m app -p coup_clone

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	