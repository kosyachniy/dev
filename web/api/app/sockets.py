from app import app, sio
from flask import request # !


# Socket.IO

from threading import Lock
from flask_socketio import emit, join_room, leave_room, rooms, Namespace # !

thread = None
thread_lock = Lock()


#

# @sio.on('online', namespace='/main')
# def online_users(mes):
# 	# # join_room('hello')
# 	# sio.emit('notification', {
# 	# 	'message': 'test',
# 	# }, room=request.sid, namespace='/main')

# 	global thread
# 	with thread_lock:
# 		if thread is None:
# 			thread = sio.start_background_task(target=background_thread)

# Видеочат

@sio.on('call', namespace='/space')
def rtc_call(mes):
	print('-' * 100) # !
	print('!1', mes)
	sio.emit('call', {
		'description': mes['description'],
	}, namespace='/space')

@sio.on('answer', namespace='/space')
def rtc_answer(mes):
	print('!2', mes)
	sio.emit('answer', {
		'description': mes['description'],
	}, namespace='/space')

@sio.on('cand1', namespace='/space')
def rtc_cond1(mes):
	print('!3', mes)
	sio.emit('cand1', {
		'description': mes['description'],
	}, namespace='/space')

@sio.on('cand2', namespace='/space')
def rtc_cond2(mes):
	print('!4', mes)
	sio.emit('cand2', {
		'description': mes['description'],
	}, namespace='/space')

#


if __name__ == '__main__':
	sio.run(app, debug=True)


# def background_thread():
# 	while True:
# 		timestamp = time.time()

# 		pass