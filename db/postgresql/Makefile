PYTHON := env/bin/python
NAME := mypsql

setup:
	python3 -m venv env
	$(PYTHON) -m pip install -U --force-reinstall pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	docker pull postgres
	docker run --name $(NAME) -e POSTGRES_PASSWORD=password -e POSTGRES_DB=main -d -p 5432:5432 postgres

stop:
	docker stop $(NAME)
	docker rm $(NAME)

check:
	docker ps -a | grep $(NAME)

connect:
	docker exec -it $(NAME) psql -h localhost -p 5432 -U postgres
