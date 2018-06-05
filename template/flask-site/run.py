#!flask/bin/python
from app import app
app.run(host='0.0.0.0', port=80, debug=True, threaded=True) #, ssl_context=('server.crt', 'server.key')