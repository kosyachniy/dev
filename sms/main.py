from urllib.request import urlopen
from urllib.parse import quote
import json, time

with open('set.txt', 'r') as file:
    s = json.loads(file.read())
 
def send_sms(phones, text, notsend=0):
    login = s['login']
    password = s['password']
    sender = 'SMSC.RU' # Имя отправителя

    #Возможные ошибки
    errors = {
        1: 'Ошибка в параметрах.',
        2: 'Неверный логин или пароль.',
        3: 'Недостаточно средств на счете Клиента.',
        4: 'IP-адрес временно заблокирован из-за частых ошибок в запросах. Подробнее',
        5: 'Неверный формат даты.',
        6: 'Сообщение запрещено (по тексту или по имени отправителя).',
        7: 'Неверный формат номера телефона.',
        8: 'Сообщение на указанный номер не может быть доставлено.',
        9: 'Отправка более одного одинакового запроса на передачу SMS-сообщения либо более пяти одинаковых запросов на получение стоимости сообщения в течение минуты. '
    }

#Отправка запроса
    text = quote(text)
    url = "http://smsc.ru/sys/send.php?login=%s&psw=%s&phones=%s&mes=%s&cost=%d&sender=%s&fmt=3" % (login, password, phones, text, notsend, sender)
    answer = json.loads(urlopen(url).read().decode('utf-8'))

    if 'error_code' in answer:
        #Возникла ошибка
        return errors[answer['error_code']]
    else:
        if notsend:
#Не отправлять, узнать только цену
            return 'Будут отправлены: %d SMS, цена рассылки: %s₽' % (answer['cnt'], answer['cost'])
        else:
            #СМС отправлен, ответ сервера
            return answer
 
print(send_sms("89811635578", 'Приветикиии:))', 0))