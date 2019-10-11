# React
## Источники
* [Описание](https://habr.com/ru/post/249107/)
* [Старт](https://learn.javascript.ru/screencast/react)

## Разработка
JSX

Redux

Создать шаблонный проект:
```
npm install -g create-react-app
create-react-app имя
```

Добавить библиотеку: ``` npm install имя ``` / ``` yarn add имя ```

Запуск сервера (с горячей перезагрузкой): ``` npm start ```

[Жизненный цикл компонент](https://habr.com/ru/post/358090/)

## Ошибки
1. Нехватает модулей, которых нет в проекте

``` react Error: Cannot find module '@csstools/normalize.css' ```

```
sudo npm install -g npm@latest
npm cache clean
npm install
```