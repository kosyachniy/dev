from flask import request
from app import app

# Яндекс.Деньги
import hashlib
import binascii

from keys import YANDEX_PAY


@app.route('/pay/ya/', methods=['POST'])
def pay():	
	# Проверка подлинность

	check_str = '{}&{}&{}&{}&{}&{}&{}&{}&{}'.format(
		request.values.get('notification_type'),
		request.values.get('operation_id'),
		request.values.get('amount'),
		request.values.get('currency'),
		request.values.get('datetime'),
		request.values.get('sender'),
		request.values.get('codepro'),
		YANDEX_PAY,
		request.values.get('label'),
	)

	str_hash = hashlib.sha1(bytes(check_str, 'utf-8')).hexdigest()
	check_hash = request.values.get('sha1_hash')

	if str_hash != check_hash:
		return '', 200

	# Тестовые запросы

	try:
		test = request.values.get('test_notification') == 'true'
	except:
		test = False

	if test:
		return '', 200

	# Параметры

	try:
		count = float(request.values.get('withdraw_amount'))
	except:
		try:
			count = float(request.values.get('amount'))
		except:
			count = 0

	try:
		user_id = int(request.values.get('label'))
	except:
		user_id = 0

	# Зачисление средств

	print(user_id, count)

	return '', 200