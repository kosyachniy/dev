from fastapi import FastAPI, Request

app = FastAPI()

@app.post('/')
async def index(request: Request):
	return await request.json()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('post_fastapi:app')