# Flask
## Gunicorn
### Настройка
``` gunicorn.service ```

```
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=kosyachniy
Group=www-data
WorkingDirectory=/home/kosyachniy/web/api/
ExecStart=/home/steve/kosyachniy/web/api/env/bin/gunicorn --access-logfile - --error-logfile error.log --workers 2 --bind unix:/home/kosyachniy/web/api/forum.sock testforum.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Источники