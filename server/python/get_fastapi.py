from fastapi import FastAPI, Request

app = FastAPI()

@app.get('/')
async def index(request: Request):
	return request.query_params

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('get_fastapi:app')