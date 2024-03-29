# Docker
## Install
[Docker Docs](https://docs.docker.com/engine/install/ubuntu/)

```
sudo apt-get update
```

```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

```
sudo apt-key fingerprint 0EBFCD88
```

```
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

```
sudo docker run hello-world
```

## Set
```
docker build -t test1 .
```

```
docker run -p 5000:5000 test1
```
OR
```
docker run -p 5000:5000 --network host test1
```

## Debug & testing
```
docker ps -a
```

```
docker kill <ID>
```

```
docker rm <ID>
```

```
docker logs <ID>
```

```
curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.get", "token": "test"}' http://127.0.0.1:5000/
```

## Push
```
docker login
```

```
docker tag test1 kosyachniy/test1:0.1
```

```
docker push kosyachniy/test1:0.1
```

## Pull
```
docker pull kosyachniy/test1
```

## Connect
```
docker exec -it mongodb bash
```

## Docker Compose
```
apt install docker-compose
```

```
docker-compose build
```

```
docker-compose up
```

## Clear
Удалить неиспользуемые данные
```
docker system prune -a
```

Очистить всё
```
docker kill $(docker ps -q)
docker_clean_ps
docker rmi $(docker images -a -q)
```

## Verify that Docker Engine is installed correctly by running the ` hello-world ` image
```
sudo docker run hello-world
```

## Ошибки
```
docker.errors.DockerException: Error while fetching server API version: ('Connection aborted.', ConnectionRefusedError(61, 'Connection refused'))
[22012] Failed to execute script docker-compose
```

Решение: Запустить сам Docker

## Источники
[Статья 1](https://tproger.ru/translations/how-to-start-using-docker/)

[Статья 2](https://habr.com/ru/post/448094/)

[Документация](https://docs.docker.com/engine/install/ubuntu/)

[Справочник](https://dker.ru/docs/docker-engine/engine-reference/dockerfile-reference/)

[Flask пример](https://github.com/testdrivenio/flask-on-docker/blob/master/services/web/Dockerfile), [Статья к примеру](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/)

[Docker Hub](https://hub.docker.com/)