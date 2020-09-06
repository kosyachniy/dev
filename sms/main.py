from func.smsc import SMSC


sms = SMSC()


if __name__ == '__main__':
	res = sms.send_sms('79811635578', 'Привет')
	success = int(float(res[-1])) > 0

	print(success)