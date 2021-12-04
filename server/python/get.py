import json

from fastapi import FastAPI, Request
import uvicorn


app = FastAPI()


@app.get('/')
@app.post('/')
async def index(request: Request):
    try:
        data_json = await request.json()
    except Exception:
        data_json = None

    data = {
        'headers': dict(request.headers),
        'body': str(await request.body()),
        'json': data_json,
        'client': f"{request.client[0]}:{request.client[1]}",
        'path_params': dict(request.path_params),
        'query_params': dict(request.query_params),
    }

    print(json.dumps(data, ensure_ascii=False, indent='\t'))
    return True


if __name__ == '__main__':
    uvicorn.run('get:app', host="0.0.0.0", port=8991)
