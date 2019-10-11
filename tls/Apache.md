# Настройка Flask + Apache + Let's Encrypt на Ubuntu 18.04.02 x64
## Создаём сервер
[DigitalOcean](https://cloud.digitalocean.com/)

[Почта](https://mail.yandex.ru/)


## Подключаемся
```
rm ~/.ssh/known_hosts
ssh root@<ip>
yes
```


## Устанавливаем веб-сервер
```
sudo apt update

sudo apt install apache2
y
```


## Добавляем пользователя
```
adduser tensy

usermod -aG sudo tensy
exit
```


## Подключаемся
```
ssh tensy@<ip>
```


## MongoDB
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -y mongodb-org

sudo service mongod start
```


## Настраиваем веб-приложение
```
sudo apt install libapache2-mod-wsgi-py3 python3-pip python3-venv

cd /var/www
sudo git clone https://github.com/tensegrity-dapp/blend 
cd blend
sudo python3 -m venv flask
sudo flask/bin/pip install flask requests flask_babel pymongo flask_socketio markdown 
sudo nano keys.py
```

```
CAPTCHA = '6LeYMmkUAAAAAGo5NZDtluNwkId_H17niBDV1u9s'
```


## Настраиваем связь с сервером
```
sudo nano tensy.wsgi
```

```
import sys
sys.path.insert(0, '/var/www/blend/')
from app import app as application
```

```
cd /etc/apache2/sites-available/
sudo nano tensy.conf
```

```
<VirtualHost *:80>
    ServerName tensy.org

    WSGIScriptAlias / /var/www/blend/tensy.wsgi
    WSGIDaemonProcess flask python-home=/var/www/blend/flask
    WSGIProcessGroup flask

    <Directory /var/www/blend>
        Order deny,allow
        Allow from all
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
</VirtualHost>
```

```
sudo apt-get install a2enmod
sudo a2ensite tensy.conf
systemctl reload apache2
```


## Ошибки
[Apache error "Could not reliably determine the server's fully qualified domain name"](https://askubuntu.com/questions/256013/apache-error-could-not-reliably-determine-the-servers-fully-qualified-domain-n)

ServerName localhost   

This is just a friendly warning and not really a problem (as in that something does not work).
If you insert a
ServerName localhost   
in either httpd.conf or apache2.conf in /etc/apache2 and restart apache the notice will disappear.
If you have a name inside /etc/hostname you can also use that name instead of localhost.

And it uses 127.0.1.1 if it is inside your /etc/hosts:
127.0.0.1 localhost
127.0.1.1 myhostname


## Настройка
### Доступ к серверу
```
ssh tensy@<ip>
<password>
sudo service mongod start
systemctl start apache2
```

### Ссылки
* [http://157.230.103.16/](http://157.230.103.16/)
* [http://157.230.103.16:5000/](http://157.230.103.16:5000/)

### Логи
```
sudo nano /var/log/apache2/error.log
```