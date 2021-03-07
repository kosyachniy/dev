from func.tg_user import client


# print(client.get_entity(input()))

def get_entity(name):
	def convert(cont):
		try:
			return int(cont)
		except:
			return cont

	return client.get_entity(convert(name))

print(get_entity(input()))