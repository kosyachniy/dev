# MongoDB
[Linux](https://docs.mongodb.com/v3.6/tutorial/install-mongodb-on-ubuntu/)

## Установка сервера
### Linux
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 9DA31620334BD75D9DCB49F368818C72E52529D4
```

Для Ubuntu 19.04 / 18.04:
```
echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
```

Для Ubuntu 16.04:
```
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
```

```
sudo apt-get update
sudo apt-get install -y mongodb-org
```

### MacOS
```
brew tap mongodb/brew
brew install mongodb-community@4.2
```

``` mongod --config /usr/local/etc/mongod.conf ```

## Настройка аутентификации
### Создания пользователей
``` mongo ``` (сначала нужно запустить ``` sudo service mongod start ```)

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

### Изменение пароля пользователя
``` mongo admin -u admin -p '<пароль>' ```

``` use admin ```

``` db.changeUserPassword('admin', '<новый пароль>') ```

### Отключение доступа вне пользователя
Linux: ``` sudo nano /etc/mongod.conf ```

MacOS: ``` sudo nano /usr/local/etc/mongod.conf ```

```
security:
  authorization: "enabled"
```

``` sudo service mongod restart ``` / ``` brew services restart mongodb-community@4.2 ```

## Настройка удалённого подключения
``` sudo nano /etc/mongod.conf ```

```
net:
  port: 27017
  bindIp: 0.0.0.0
```

``` sudo service mongod restart ``` / ``` brew services restart mongodb-community@4.2 ```

## Запуск сервера
### Linux
``` sudo service mongod start ```

### MacOS
``` brew services start mongodb ```

``` brew services start mongodb-community@4.2 ```

## Подключение к серверу
### Локально
``` mongo ```

### На своём сервере
``` mongo <ip> --port 27017 -u "admin" --authenticationDatabase "admin" ```

``` mongo <db> -u <login> -p <password> --authenticationDatabase admin ```

### В базе Mongo
``` mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database.collection][?options]] ```

Добавление IP адреса в белый список: ``` Clusters -> Security -> IP Whitelist ```

## Справочники
[METANIT.COM](https://metanit.com/nosql/mongodb/2.8.php)

[BruzhMelev](https://bruzh.wordpress.com/2016/06/25/%D1%88%D0%BF%D0%B0%D1%80%D0%B3%D0%B0%D0%BB%D0%BA%D0%B0-mongodb/)