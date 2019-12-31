# WebPack
## Источники
* [Старт](https://habr.com/ru/post/309306/)

## Установка
```
npm install -g webpack
npm init

npm install -S jquery
npm install -S underscore

npm install -S webpack
```

## Компиляция
```
webpack js/profile.js dist/bundle.js
```

Если ошибка:
```
One CLI for webpack must be installed. These are recommended choices, delivered as separate packages:
 - webpack-cli (https://github.com/webpack/webpack-cli)
   The original webpack full-featured CLI.
We will use "npm" to install the CLI via "npm install -D".
Do you want to install 'webpack-cli' (yes/no): yes
Installing 'webpack-cli' (running 'npm install -D webpack-cli')...
npm WARN test@0.1.0 No repository field.

+ webpack-cli@3.2.3
updated 1 package and audited 5207 packages in 3.096s
found 0 vulnerabilities

{ Error: Cannot find module 'webpack-cli'
    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:581:15)
    at Function.Module._load (internal/modules/cjs/loader.js:507:25)
    at Module.require (internal/modules/cjs/loader.js:637:17)
    at require (internal/modules/cjs/helpers.js:20:18)
    at runCommand.then (/usr/local/lib/node_modules/webpack/bin/webpack.js:143:5)
    at process._tickCallback (internal/process/next_tick.js:68:7) code: 'MODULE_NOT_FOUND' }
```
Устанавливаем сами WebPack CLI глобально: ``` npm install webpack-cli -g ```


Файл с конфигурацией: ``` webpack.config.js ```

Автоматическая компиляция: ``` webpack -w ```

Горячая перезагрузка:
```
npm install -g webpack-dev-server
webpack-dev-server --port 10000
```
Адрес: [``` http://localhost:10000/ ```](http://localhost:10000/)

## Разработка
Подключение стилей: ``` npm install style-loader css-loader --save-dev ```

Если ошибка:
```
Invalid configuration object. Webpack has been initialised using a configuration object that does not match the API schema.
 - configuration.module has an unknown property 'loaders'. These properties are valid:
   object { defaultRules?, exprContextCritical?, exprContextRecursive?, exprContextRegExp?, exprContextRequest?, noParse?, rules?, strictExportPresence?, strictThisContextOnImports?, unknownContextCritical?, unknownContextRecursive?, unknownContextRegExp?, unknownContextRequest?, unsafeCache?, wrappedContextCritical?, wrappedContextRecursive?, wrappedContextRegExp? }
   -> Options affecting the normal modules (`NormalModuleFactory`).
```
Нужно заменить
```
loaders: [
	{test : /\.css$/, loader: 'style!css!'}
]
```
на
```
rules: [
	{test: /\.css$/, use: 'css-loader'}
]
```
И закомментировать, потому что это нахер не нужно!


Если ошибка:
```
ERROR in ./js/profile.js
Module not found: Error: Can't resolve 'style' in '/Users/kosyachniy/Re/project/dev/js/webpack/js'
BREAKING CHANGE: It's no longer allowed to omit the '-loader' suffix when using loaders.
                 You need to specify 'style-loader' instead of 'style',
                 see https://webpack.js.org/migrate/3/#automatic-loader-module-name-extension-removed
 @ ./js/profile.js 1:0-36
```
Заменить ``` require('style!css!../css/main.css'); ``` на ``` require('style-loader!css-loader!../css/main.css'); ```

## Запуск
```
npm install
webpack
webpack-dev-server
```

``` http://localhost:10000/ ``` (указан в ``` webpack.config.js ```)