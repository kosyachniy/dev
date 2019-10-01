# Видеочат

@sio.on('candidate1', namespace='/space')
def candidate1(mes):
	print('!cand1', mes)
	sio.emit('candidate1', mes, namespace='/space')

@sio.on('description1', namespace='/space')
def description1(mes):
	print('!desc1', mes)
	sio.emit('description1', mes, namespace='/space')

@sio.on('candidate2', namespace='/space')
def candidate2(mes):
	print('!cand2', mes)
	sio.emit('candidate2', mes, namespace='/space')

@sio.on('description2', namespace='/space')
def description2(mes):
	print('!desc2', mes)
	sio.emit('description2', mes, namespace='/space')