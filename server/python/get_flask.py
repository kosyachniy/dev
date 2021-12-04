from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    print(
        dir(request),
        request.view_args,
        request.values, # !
        # request.user_agent,
        request.remote_addr,
        request.query_string,
        request.path,
        request.origin,
        request.mimetype,
        request.method,
        request.json,
        # request.input_stream,
        request.full_path,
        request.files,
        request.endpoint,
        request.data,
        request.cookies,
        request.args,
        sep='\n',
    )
    return jsonify({
        'headers': str(request.headers),
        'form': request.form,
        'json': request.json,
        'values': request.values,
    })

if __name__=='__main__':
	app.run()