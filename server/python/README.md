# Запуск
## Запросы
``` get_request.py ```

``` post_request.py ```

## Сервер
``` get_flask.py ```

``` post_flask.py ```

``` server.py ```

Запуск командой внутри директории: ``` python -m http.server ```


# Полезное
## NGINX + Flask + Gunicorn + Socket.IO
[FOSSASIA](https://blog.fossasia.org/setting-up-nginx-gunicorn-and-flask-socketio/)

``` pip install flask-socketio eventlet ```

``` gunicorn app:app --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload ```

```
server {
    listen 80;
    location / {
        proxy_pass http://127.0.0.1:5001;
    }
}
```

[Read the docs](https://flask-socketio.readthedocs.io/en/latest/)

``` gunicorn --worker-class eventlet -w 1 module:app ```

```
server {
    listen 80;
    server_name _;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    location /socket.io {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:5000/socket.io;
    }
}
```

[GitHub](https://github.com/miguelgrinberg/Flask-SocketIO/issues/474)

``` gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind unix:app.sock -m 007 wsgi:app ```

```
upstream nodes {
    ip_hash;
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name xxx.xxx.xxx.xxx;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/me/website/website.sock;
    }

    location /socket.io {
        proxy_pass http://nodes/socket.io;
        proxy_http_version 1.1;
        proxy_redirect off;
        proxy_buffering off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}
```

[GitHub](https://github.com/miguelgrinberg/Flask-SocketIO/issues/436)

```
server {
    listen 8080;
    server_name myserver;

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:5000;
    }

    location /socket.io {
        include proxy_params;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:5000/socket.io;
    }
}
```

[Qari.site](http://qaru.site/questions/1224020/correct-configuration-for-flask-socketio)

```
server {
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_redirect off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://localhost:8000/socket.io;
        proxy_redirect off;
        proxy_buffering off;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";

    }

}
```

```
bind = '127.0.0.1:8000'
workers = 2
worker_class = 'socketio.sgunicorn.GeventSocketIOWorker'
```

[Qaru.site](http://qaru.site/questions/4922028/flask-socketio-gunicorn-nginx-through-unix-socket-file-errno-2)

``` gunicorn --worker-class socketio.sgunicorn.GeventSocketIOWorker chat:app -b unix:///var/sockets/gunicorn.sock ```


# Источники
## POST
[TProger](https://www.youtube.com/watch?list=PL1A2CSdiySGIPxpSlgzsZiWDavYTAx61d&v=bTThyxVy7Sk)

## Реализация сервера
[Python Docs](https://docs.python.org/3/library/http.server.html)
 | [HabraHabr](https://habrahabr.ru/sandbox/28540/)