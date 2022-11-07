from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get('/')
async def index(request: Request):
    response = JSONResponse(content={'json_key': 'json_value'})
    response.set_cookie(key='cookie_key', value='cookie_value')
    return response

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('cookie:app')
