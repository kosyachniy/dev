from func.tg_user import client


for i in range(535,560):
	client.delete_messages(-1001124440739, i)