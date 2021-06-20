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
```

!!! И залить !!!
```
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

8. Создать ветку и переключаться на неё
```
git checkout -b <>
```

9. Переключаться на ветку
```
git checkout <>
```

10. Удалить ветку
Из локального репозитория:
```
git branch -d <>
```

Из глобального репозитория:
```
git push origin --delete <>
```

11. Насильно обновить локальный репозиторий
```
git fetch --all
git reset --hard origin/master
git pull origin master
```

12. Авторизация
```
git config --global user.name "<логин>"
git config --global user.email "<почта>"
```

```
git config --global user.password "<пароль>"
```

13. Дополнить сделанный коммит (не глобальный)
```
git commit -a --amend
```

14. Зеркальная копия репозитория без форка
```
git clone --bare https://github.com/exampleuser/old-repository.git
cd old-repository.git
git push --mirror https://github.com/exampleuser/new-repository.git
cd ..
rm -rf old-repository.git
```

15. Отменить локальный коммит без изменения файлов
```
git reset --soft HEAD^
```

16. Переименовать коммит
```
git commit --amend -m '<>'
```

17. Изменить ссылку на репозиторий (git remote url)
```
git remote set-url origin <новая ссылка>
```

18. Не отслеживать изменения файла

! Нужно указывать полный путь до файла
```
git update-index --assume-unchanged /Users/kosyachniy/Re/projects/web/data/example.txt
```
Отмена:
```
git update-index --no-assume-unchanged /Users/kosyachniy/Re/projects/web/data/example.txt
```

19. Слить ветки
```
git checkout master
git merge dev
git push
```

! Сделать ветку master основной (если это не так)

20. Переименовать ветку

На GitHub переименовать ветку, потом:

```
git branch -m <старая ветка> <новая ветка>
git fetch origin
git branch -u origin/<новая ветка> <новая ветка>
git remote set-head origin -a
```