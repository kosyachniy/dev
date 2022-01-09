include .env

run:
	docker-compose up --build

connect:
	docker exec -it `docker ps -a | grep ${PROJECT_NAME}/test_service | cut -d ' ' -f 1` bash
