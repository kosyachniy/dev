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
sudo apt-get install nginx
y
```


## Добавляем пользователя
```
adduser kosyachniy


<password>


y


usermod -aG sudo kosyachniy
exit
```


## Подключаемся
```
ssh kosyachniy@<ip>

<password>
```


## Настраиваем связь с сервером
```
sudo ufw allow 5000

sudo nano /etc/nginx/sites-available/<имя проекта>
```

```
#################
# <имя проекта> #
#################

server {
    listen 443 ssl; # managed by Certbot
    server_name <домен> www.<домен>;
    client_max_body_size 20M;

    location /api/ {
        rewrite ^/api/?(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /load/ {
        proxy_pass http://127.0.0.1:5000/static/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000/socket.io/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_redirect off;
        proxy_buffering off;

        #proxy_set_header Host $host;
        #proxy_set_header X-Real-IP $remote_addr;
        #proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header HOST $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass_request_headers on;
        #proxy_pass http://<server ip="">:<server port="">;
        proxy_http_version 1.0;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}

server {
    listen 80;
    server_name <домен> www.<домен>;

    if ($host = <домен>) {
        return 301 https://$host$request_uri;
    } # managed by Certbot

    return 404; # managed by Certbot
}
```

```
sudo ln -s /etc/nginx/sites-available/<имя проекта> /etc/nginx/sites-enabled

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
```

Если нужно добавить другие домены:
```
certbot certonly --expand -d example.com -d www.example.com -d shop.example.com
```

```
sudo certbot --nginx
polozhev@mail.ru
A
Y
1
2

sudo certbot renew --dry-run
```


## Настройка
### Доступ к серверу
```
ssh kosyachniy@<ip>
<password>
```

```
sudo systemctl restart nginx
```

### Ссылки
[https://www.ssllabs.com/ssltest/analyze.html?d=<домен>&latest](https://www.ssllabs.com/ssltest/analyze.html?d=<домен>&latest)

### Логи
* ``` sudo nano /var/log/nginx/error.log ```
* ``` sudo nano /var/log/nginx/access.log ```

### Конфигурации
* ``` sudo nano /etc/nginx/nginx.conf ```
* ``` sudo nano /etc/nginx/sites-available/<имя проекта> ```

### Ключи
* ``` /etc/letsencrypt/live/<домен>/fullchain.pem ```
* ``` /etc/letsencrypt/live/<домен>/privkey.pem ```