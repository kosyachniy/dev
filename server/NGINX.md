# Настройка Flask + NGINX + Let's Encrypt на Ubuntu 18.04.02 x64

## Создаём сервер
[DigitalOcean](https://cloud.digitalocean.com/)


## Подключаемся
```
rm ~/.ssh/known_hosts
ssh root@<ip>
yes
```

<password>


## Устанавливаем веб-сервер
```
sudo apt-get update
sudo apt install nginx
y
```

## Входим в Tmux
```
tmux new -s <>
```

## Клонируем код
```
git clone <>
```

Если приватный:
```
login
pass
```

```
cd <>/api
```

## Виртуальное окружение
```
sudo apt install python3-venv
y

python3 -m venv env
env/bin/pip install -r requirements.txt
```

## Настраиваем
```
nano keys.py
```

## Запускаем бэк
```
env/bin/python run.py
```

## Ещё сессия
```
ctrl+b c
```

## Виртуальное окружение
```
cd <>/web

sudo apt install npm
y
npm install
```

## Настраиваем
```
nano src/keys.js
```

## Ещё сессия
```
ctrl+b c
```

## Настраиваем NGINX
```
cd /etc/nginx/
```

```
sudo nano nginx.conf
```

```
	types_hash_max_size 20480;
	client_max_body_size 30m;
```

## Конфигурация проекта
```
cd /etc/nginx/sites-available
```

```
sudo nano <>
```

```
sudo ln -s /etc/nginx/sites-available/<> /etc/nginx/sites-enabled

sudo systemctl restart nginx
```

## Ещё сессия
```
ctrl+b c
```

## База данных
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

```
sudo service mongod start
```

```
mongo
```

```
use admin

db.createUser(
	{
		user: "admin",
		pwd: "<пароль>",
		roles: [ "userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase", "root" ]
	}
)
```

```
ctrl+d
```

```
sudo nano /etc/mongod.conf
```

```
security:
  authorization: "enabled"

net:
  port: 27017
  bindIp: 0.0.0.0
```

```
ctrl+o y
ctrl+x
```

```
sudo service mongod restart
```

## Ещё сессия
```
ctrl+b c
```

## Шифрование
```
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
<enter>
```

```
sudo apt-get update
sudo apt-get install certbot python-certbot-nginx
y
```

```
sudo certbot --nginx
polozhev@mail.ru
A
Y
1
2
```