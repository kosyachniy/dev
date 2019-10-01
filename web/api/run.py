#!env/bin/python
from app import app

from sets import SERVER


host, port = SERVER['ip'].split(':')

if __name__ == '__main__':
	app.run(
		host=host,
		port=port,
		debug=True,
		threaded=True,
	)