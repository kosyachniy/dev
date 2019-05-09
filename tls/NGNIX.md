# Настройка Flask + NGINX + Let's Encrypt на Ubuntu 18.04.02 x64

## Создаём сервер
[DigitalOcean](https://cloud.digitalocean.com/)


## Подключаемся
```
rm ~/.ssh/known_hosts
ssh root@<ip>
yes
```

[Почта](https://mail.yandex.ru/)

<password>


## Устанавливаем веб-сервер
```
sudo apt-get update
sudo apt-get install nginx
y
```


## Добавляем пользователя
```
adduser tensy


<password>


y


usermod -aG sudo tensy
exit
```


## Подключаемся
```
ssh tensy@104.248.27.15
```

<password>


## MongoDB
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5

echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -y mongodb-org

sudo service mongod start

systemctl enable mongod.service


<password>
<password>
```


## Настраиваем веб-приложение
```
sudo apt install python3-pip python3-venv
y

git clone https://github.com/tensegrity-dapp/blend 
cd blend

nano wsgi.py
```

```
from app import app
if __name__ == '__main__':
	app.run()
```

```
nano keys.py
```

```
CAPTCHA = '6LeYMmkUAAAAAGo5NZDtluNwkId_H17niBDV1u9s'
```

```
cp re/db_load.py db.py
```

копировать db

копировать load

```
python3 -m venv flask


flask/bin/pip install gunicorn flask requests flask_babel pymongo flask_socketio markdown 
flask/bin/python db.py
```


## Настраиваем связь с сервером
```
sudo ufw allow 5000

sudo nano /etc/systemd/system/myproject.service
```

```
[Unit]
Description=Gunicorn instance to serve myproject
After=network.target

[Service]
User=tensy
Group=www-data
WorkingDirectory=/home/tensy/blend
Environment="PATH=/home/tensy/blend/flask/bin"
ExecStart=/home/tensy/blend/flask/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app
/home/tensy/blend/flask/bin/gunicorn --workers 3 --bind unix:myproject.sock -m 007 wsgi:app
--bind 0.0.0.0:5000

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl start myproject
sudo systemctl enable myproject

sudo systemctl status myproject

sudo nano /etc/nginx/sites-available/myproject
```

```
server {
    listen 80;
    server_name tensy.org www.tensy.org;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/tensy/blend/myproject.sock;
    }

  location ~* \.io {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-NginX-Proxy true;

      proxy_pass http://localhost:3000;
      proxy_redirect off;

      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
    }
}
```

```
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled

sudo nginx -t

sudo systemctl restart nginx

sudo ufw delete allow 5000
sudo ufw allow 'Nginx Full'
```


## Шифрование
```
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
<enter>

sudo apt-get update
sudo apt-get install certbot python-certbot-nginx
y

sudo certbot --nginx
polozhev@mail.ru
A
Y
1
2

sudo certbot renew --dry-run
```


[https://tensy.org/](https://tensy.org/)


## Настройка
### Доступ к серверу
```
ssh tensy@<ip>
<password>
```

```
sudo systemctl restart nginx
```

### Ссылки
[https://tensy.org/](https://tensy.org/) 
[https://www.ssllabs.com/ssltest/analyze.html?d=tensy.org&latest](https://www.ssllabs.com/ssltest/analyze.html?d=tensy.org&latest)

### Логи
* ``` sudo nano /var/log/nginx/error.log ```
* ``` sudo nano /var/log/nginx/access.log ```
* ``` nano /home/tensy/blend/error.log ```

### Конфигурации
* ``` sudo nano /etc/nginx/nginx.conf ```
* ``` sudo nano /etc/nginx/sites-available/myproject ```
* ``` sudo nano /etc/systemd/system/myproject.service ```

### Ключи
* ``` /etc/letsencrypt/live/tensy.org/fullchain.pem ```
* ``` /etc/letsencrypt/live/tensy.org/privkey.pem ```