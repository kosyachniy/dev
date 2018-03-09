## Описание
``` main.py ``` - основной Python скрипт, который компилируем

``` setup.py ``` - настройки

## Запуск компиляции
### Windows
Py2Exe
``` setup.py py2exe ``` !

### Linux / MacOS
PyInstaller
``` pyinstaller main.py ```

Возможные ошибки:
1. ``` AttributeError: module 'enum' has no attribute 'IntFlag' ``` -> ``` pip uninstall enum34 ```
2. ``` UnicodeDecodeError: 'utf-8' codec can't decode byte 0xef in position 15: invalid continuation byte [6282] Failed to execute script main ``` -> нигде не использовать русский язык

[HabraHabr](https://habrahabr.ru/post/325626/)

1. --onefile — сборка в один файл, т.е. файлы .dll не пишутся.
2. --windowed -при запуске приложения, будет появляться консоль.
3. --noconsole — при запуске приложения, консоль появляться не будет.
4. --icon=app.ico — добавляем иконку в окно.
5. --paths — возможность вручную прописать путь к необходимым файлам, если pyinstaller
не может их найти(например: --paths D:\python35\Lib\site-packages\PyQt5\Qt\bin)
