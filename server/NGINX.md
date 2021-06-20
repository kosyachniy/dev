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

## База данных
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

```
sudo service mongod start
```

Если требуются пользователи для БД:
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
# env/bin/pip install eventlet gunicorn
```

## Настраиваем (если требуется для бэка)
```
nano keys.py
```

Меняем IP и адреса:
```
nano sets.py
```

## Запускаем бэк
```
env/bin/gunicorn app:app -c gun.py
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

## Настраиваем (если требуется для фронта)
```
nano src/keys.js
```

Меняем IP и адреса:
```
nano src/sets.js
```

## Запускаем фронт
```
npm start
```

Если продакшн-версии:
```
serve -s build -p 3000
```

## Ещё сессия
```
ctrl+b c
```

## Настраиваем NGINX
```
sudo nano /etc/nginx/nginx.conf
```

Если нет доступа к статике:
```
	user root;
```

Если будет загрузка больших файлов:
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
Вставляем конфигурацию из репозитория

```
sudo ln -s /etc/nginx/sites-available/<> /etc/nginx/sites-enabled

sudo systemctl restart nginx
```

## Ещё сессия
```
ctrl+b c
```

## Шифрование
```
sudo snap install core; sudo snap refresh core
sudo apt-get remove certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

```
sudo certbot --nginx
polozhev@mail.ru
A
Y
1
2
```