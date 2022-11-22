from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()


class Input(BaseModel):
    id: int = None

class Output(BaseModel):
    test: str


@app.get('/', response_model=Output)
async def index(request: Request):
    return {
        'test': 'test',
        'alo': 'alo',
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('ivan:app')
