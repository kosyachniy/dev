# BASH
## Команды терминала
1. Локальные хосты
```
sudo arp-scan --localnet
```

2. Открытые порты
```
sudo netstat -ntulp
sudo lsof -nP -i | grep LISTEN
```

3. Содержимое папки
```
ls -aFGlsh
```

4. Размер папки
```
du -sh
```

5. Список пользователей
```
cut -d: -f1 /etc/passwd
```

6. Очистить ключи ssh
```
rm ~/.ssh/known_hosts
```

7. Назначить команду
```
alias python=python3
alias pip3='/usr/local/bin/pip3.7'
```
```
unalias python
```

8. Запустить файл
``` ./<> ``` или ``` source <> ```

9. Прервать
``` Ctrl + c ```

10. Закрыть
``` Ctrl + d ```

11. Путь до текущей директории
``` pwd ```

12. MD5 сумма папки
``` cat ./* | md5 ```

13. Изменить права
``` sudo chown -R `whoami`:admin /<путь> ```

14. Список ip-адресов посредников
``` traceroute yandex.ru ```

15. Сменить пароль
``` passwd ```

16. Закрыть процесс на порту
```
lsof -i tcp:<порт>
kill -9 <PID>
```

17. Разархивировать GZIP
```
gunzip example.gz
```

18. Свободное место ЖД
```
df -h
```

19. История подключений SSH
```
sudo tail -f /var/log/auth.log
```

20. Версия системы
```
lsb_release -a
```

21. История команд
[Больше →](https://losst.ru/istoriya-komand-linux)
```
history
```

22. История подключений
```
last
```

Неудачные попытки
```
lastb
```

23. Нагрузка и процессы
```
htop
```

24. Архивация GZIP

25. Архивация TAR GZIP

26. Количество файлов
```
ls -l | wc
```

27. Сменить права
```
chmod 777 -r
```

28. Сменить владельца
```
sudo chown user ./file
```

29. Реалтайм поиск по ключевому слову & обрезка строки
```
cat data/logs/api.log | grep "Unknown brand" | cut -c 74- | sort -u
```

30. Сгенерировать SSH ключи
```
ssh-keygen
pbcopy < ~/.ssh/id_rsa.pub
```

```
ssh-keygen -t rsa -b 4096 -f deploy
cat ~/deploy.pub >> ~/.ssh/authorized_keys
service sshd reload
pbcopy < ~/deploy
```

31. Копирование файлов между серверами
```
scp /<path_to_file> root@<ip>:/<new_path>
```

## Команды Tmux
[Шпаргалка](https://habr.com/ru/post/126996/)
Команда | Описание
---|---
``` tmux ``` | Создать сессию
``` tmux new -s <имя> ``` | Создать именнованную сессию
``` tmux attach ``` | Присоединиться к существующей сессии
``` tmux attach -t <имя> ``` | Присоединиться к существующей именнованной сессии
``` Ctrl + b n ``` | Следующее окно
``` Ctrl + b p ``` | Предыдущее окно
``` Ctrl + b x ``` | Закрыть окно
``` Ctrl + b c ``` | Создать окно
``` Ctrl + b d ``` / ``` tmux detach ``` | Отключиться (выйти из сессии)
``` tmux ls ``` | Список сессий
``` Ctrl + b PgUp ``` | Режим копирования
``` q ``` | Выход из режима копирования
``` Ctrl + b [ ↑ ``` | Прокрутка вверх


## Команды Vim
Команда | Описание
---|---
``` :i ``` | Вставить текст
``` Esc ``` | Выйти из вставки текста
``` :q ``` | Выйти
``` :q! ``` | Выйти и сохранить
``` :wq ``` | Записать и выйти
``` :wq! ``` | Насильно записать и выйти
``` :x ```, ``` :exit ``` | Записать и выйти, если есть изменения
``` :qa ``` | Выйти отовсюду
``` :cq ``` | Закрыть без сохранения, выйти с ошибкой

[Подробнее](https://losst.ru/kak-polzovatsya-tekstovym-redaktorom-vim)


## Команды Nano basics
Команда | Описание
---|---
``` nano <> ``` | Открыть файл <>
``` Ctrl + o ``` | Сохранить
``` Ctrl + x ``` | Выйти