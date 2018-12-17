from func.smsc import SMSC


sms = SMSC()


if __name__ == '__main__':
	sms.send_sms('79811635578', 'Привет')