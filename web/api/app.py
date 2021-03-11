from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Input(BaseModel):
	method: str
	params: dict = {}
	locale: str = 'en'
	token: str = None


app = FastAPI(title='Web app API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/')
async def api(data: Input, request: Request):
	print(data, request.client.host, request.client.port)
	return {'error': 0, 'result': {'data': 'result'}}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app:app', port=5000, reload=True)