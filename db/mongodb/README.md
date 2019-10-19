# MongoDB
[Linux](https://docs.mongodb.com/v3.6/tutorial/install-mongodb-on-ubuntu/)

## Установка сервера
### Linux
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

### MacOS
```
brew install mongodb
```

## Настройка аутентификации
### Создания пользователей
``` mongo ```

``` use admin ```

```
db.createUser(
	{
		user: "admin",
		pwd: "<пароль>",
		roles: [ "userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase", "root" ]
	}
)
```

### Отключение доступа вне пользователя
``` sudo nano /etc/mongod.conf ```

```
security:
  authorization: "enabled"
```

``` sudo service mongod restart ```

## Настройка удалённого подключения
``` sudo nano /etc/mongod.conf ```

```
net:
  port: 27017
  bindIp: 0.0.0.0
```

``` sudo service mongod restart ```

## Запуск сервера
### Linux
``` sudo service mongod start ```

### MacOS
``` brew services start mongodb ```

## Подключение к серверу
### Локально
``` mongo ```

### На своём сервере
``` mongo <ip> --port 27017 -u "admin" --authenticationDatabase "admin" ```

### В базе Mongo
``` mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database.collection][?options]] ```

Добавление IP адреса в белый список: ``` Clusters -> Security -> IP Whitelist ```

## Справочники
[METANIT.COM](https://metanit.com/nosql/mongodb/2.8.php)

[BruzhMelev](https://bruzh.wordpress.com/2016/06/25/%D1%88%D0%BF%D0%B0%D1%80%D0%B3%D0%B0%D0%BB%D0%BA%D0%B0-mongodb/)