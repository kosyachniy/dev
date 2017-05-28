import threading
from post import post
from user import user

#Автопостинг твитов на базе интернета / популярных твитов (твитить 2400 в день)
threading.Thread(target=post).start()
#Подписываться для накрутки, проверка языка (фолловинг 1 раз в минуту, список 1 раз в минуту)
threading.Thread(target=user).start()