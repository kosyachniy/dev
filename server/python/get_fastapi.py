from fastapi import FastAPI, Request

app = FastAPI()

@app.get('/')
@app.post('/')
async def index(request: Request):
    print(
        dir(request),
        # request.__dict__,
        # list(request.items()),
        request.path_params,
        request.query_params,
        # await request.form(),
        # request.cookies,
        sep='\n',
    )

    try:
        json = await request.json()
    except Exception:
        json = None

    return {
        'headers': request.headers,
        'body': await request.body(),
        'json': json,
        'client': request.client,
        'path_params': request.path_params,
        'query_params': request.query_params,
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('get_fastapi:app')