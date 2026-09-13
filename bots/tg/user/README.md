# Telethon

## Find a chat by name

```sh
python search_chats.py "part of the chat name"
python search_chats.py "old group" --limit 20 --no-last-message
```

Uses the same `tg.id`, `tg.hash` and `tg.session` configuration as `chats.py`.
Prints results and saves them to `chats_search.txt` (`--output` changes the path).
Includes the name, username if present, entity type, raw and marked IDs,
migration target if present, and latest message ID when available.

Searches known chats by title/username using the personalized results from
[`contacts.search`](https://core.telegram.org/constructor/contacts.found),
the same mechanism used by
[TDLib's server chat search](https://github.com/tdlib/td/blob/master/td/telegram/DialogManager.cpp).
A username is not required. This makes one search request plus at most one
batch request for latest message IDs; `--no-last-message` skips that second
request. Authentication can make additional requests. It never scans all
dialogs or retries a flood wait. If metadata fails, IDs and titles are still
saved, with the latest message column left blank.

Telegram controls matching and can cap results; a missing result does not
prove the chat is gone. Try a distinctive part of its current title. This
search does not discover arbitrary private chats outside your account.

## Источники


## Ошибки
Чтобы использовать вместе с Flask: ``` pip install telethon-sync ```


```
pip install telethon==0.19.1.6
```

[Новая версия](https://docs.telethon.dev/en/latest/misc/compatibility-and-convenience.html)

[Приложения Telegram](https://my.telegram.org/auth?to=apps)

https://github.com/LonamiWebs/Telethon/issues/597

https://tl.telethon.dev/methods/messages/search.html
