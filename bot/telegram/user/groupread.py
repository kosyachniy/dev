from func.tg_user import client


from_id = -1001137807617 #-1001262712033 #-1001124440739 #-1001143136828
to_id = 440219158 #136563129

for i in client.get_message_history(from_id)[1]:
	'''
	print(i.id)
	print(i)
	'''

	y = '%d %d\n' % (from_id, i.id)

	try:
		x = i.message
	except:
		x = ''

	try:
		x += i.media.caption
	except:
		pass

	'''
	if not len(x):
		print('STOP')
		break
	'''

	client.send_message(to_id, y + x + '\n--------------------')