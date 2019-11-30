# Git
1. Инициализировать репозиторий 
```
echo "# <>" >> README.md
git init
git add .
git commit -m "Pilot"
git remote add origin https://github.com/kosyachniy/<>.git
git push -u origin master
```

2. Залить
```
git add .
git commit -m '<>'
git push
```

3. Обновить
```
git pull
```

4. Отменить добавление
```
git reset <>
```

5. Откатить коммиты
```
git reset --hard a3775a5485af0af20375cedf46112db5f813322a
git push --force
```

6. История коммитов
```
git log
```

7. Не учитывать изменения mode
```
git config core.filemode false
```

8. Создать ветку
```
git branch <>
git checkout <>
```

9. Насильно обновить локальный репозиторий
```
git fetch --all
git reset --hard origin/master
git pull origin master
```

10. Авторизация
```
git config --global user.name "<логин>"
git config --global user.password "<пароль>"
```

11. Дополнить сделанный коммит (не глобальный)
```
git commit -a --amend
```