#  Получение токена пользователя

7076877

Да. VK_VIDEO_USER_TOKEN это обычный user access_token VK, не group key.

  Для твоего кейса нужен токен пользователя, который:

  - админ нужного сообщества
  - выдан для твоего VK app
  - имеет scope минимум video,groups,offline

  Самый быстрый способ получить его вручную:

  1. Создай/открой VK app и возьми APP_ID.
  2. Открой в браузере ссылку, подставив свой APP_ID:

  https://oauth.vk.com/authorize?client_id=APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,groups,offline&response_type=token&v=5.199

  3. Войди тем VK-аккаунтом, который админит сообщество.
  4. Нажми “Разрешить”.
  5. На https://oauth.vk.com/blank.html в адресной строке будет:
     #access_token=...&expires_in=0&user_id=...
  6. Значение после access_token= и есть VK_VIDEO_USER_TOKEN.

  Дальше положи его в .env:

  VK_VIDEO_USER_TOKEN="..."
  VK_GROUP_ID="151412216"

  Потом перезапусти vk-bot, bot, scheduler.

  Если хочешь более правильный server-side вариант, используй Authorization Code Flow:

  1. Открой authorize URL с response_type=code
  2. Получи code
  3. Обменяй его на токен через oauth.vk.com/access_token с client_secret

  Но для разового получения рабочего токена под staging ручной response_type=token обычно быстрее.

  Как проверить, что токен реально подходит:

  - video.get должен отрабатывать для входных видео
  - video.save должен отрабатывать для отправки результата в сообщество

  Пример проверки video.save:
    -d "name=test" \
    -d "v=5.199"

  Если вернётся upload_url, токен подходит.

  - group token для этого не заменяет user token: video.get и video.save у VK сейчас user-only

  Источники:
  "error": "invalid_request",
  "error_description": "invalid scope"
  }```[Image #1]


• Проверяю, какие scope VK сейчас реально принимает для user OAuth и нет ли ограничения по типу приложения. Потом дам рабочую authorize-ссылку, а
  не общую догадку.

• Searched site:dev.vk.com VK OAuth invalid scope video groups offline authorize blank.html

• Searched dev.vk.com oauth permissions video scope user token

• Searched "invalid scope" VK oauth authorize groups offline video app type

• Searched site:dev.vk.com "direct auth" "invalid scope" VK app

• Searched site:vk.com/dev permissions video groups offline VK access token

• Searched https://vksdk.github.io/vk-sdk-android/auth/

• Searched site:vk.com/dev/implicit_flow_user Standalone приложение VK

───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Да, и ошибка указывает, что проблема не в формате ссылки, а в самом приложении или наборе прав.

  Что важно:

  - Для нашей задачи groups обычно не нужен. Для video.get/video.save нужен user token с video, а offline нужен для бессрочности.
  - Так что сначала пробуй урезанный scope:

  https://oauth.vk.com/authorize?client_id=54463329&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,offline&response_type=token&v=5.199

  Если video,offline тоже даёт invalid scope, то почти наверняка текущий app id 54463329 не подходит для классического user OAuth с такими правами.
  Это обычно бывает, когда приложение не того типа. Практическое решение: завести отдельное Standalone приложение в VK и получать
  VK_VIDEO_USER_TOKEN через него, а не через текущий mini app.

  Рабочая схема:

  1. Создай отдельное VK Standalone app.
  2. Возьми его APP_ID.
  3. Открой:

  https://oauth.vk.com/authorize?client_id=NEW_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=video,offline&response_type=token&v=5.199

  4. Авторизуйся тех-аккаунтом, который админит сообщество.
  5. Возьми access_token из blank.html#access_token=...
  6. Положи его в VK_VIDEO_USER_TOKEN.

  Если нужен именно server-side flow, можно делать response_type=code, но для staging проще и быстрее именно token.

  Мой вывод про тип приложения тут частично выводный, но он хорошо согласуется с тем, что:

  - VK SDK docs показывают обычный user auth со scope-строкой и ссылаются на классический access_token flow: VK SDK Auth
    (https://vksdk.github.io/vk-sdk-android/auth/)
  - наши нужные методы video.get и video.save действительно user-only: video methods schema
    (https://raw.githubusercontent.com/VKCOM/vk-api-schema/master/video/methods.json)
  - похожий invalid scope кейс для VK обычно лечится Standalone app: Stack Overflow RU (https://ru.stackoverflow.com/q/1093586)

  Итого:

  - Сначала попробуй без groups: scope=video,offline
  - Если всё ещё invalid scope, не мучай 54463329; создай отдельное Standalone app и бери токен через него

  Если хочешь, я могу сразу дать тебе короткий чеклист: где в кабинете VK создать Standalone app и как потом проверить токен через
  video.save/video.get.
