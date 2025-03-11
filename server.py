import asyncio
import time
from fastapi import FastAPI, HTTPException, Form
from datetime import datetime
from os import environ
from http import HTTPStatus

from typing import Annotated

from pydantic import BaseModel, Field

from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'))

@app.get("/health")
def health():
    return {'message': 'I am up and running', 'error': None}


@app.get('/sleep/sys')
def nsys_sleep():
    time.sleep(1)
    return {'error': None}


@app.get('/sleep/async-sys')
async def sys_sleep():
    time.sleep(1)
    return {'error': None}


@app.get('/sleep/async-aio')
async def aio_sleep():
    await asyncio.sleep(1)
    return {'error': None}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app)

@app.get('/info')
def info():
    return {
        'version': '0.1.0',
        'time': datetime.now(),
        'home': environ['HOMEPATH']
    }

# http://localhost:3000/logs?start=2025-03-03&end=2025-03-04&level=info
@app.get('/logs')
def logs(start: datetime, end: datetime, level: str = None):
    # do a query to db to retrieve logs in this time range
    if start >= end:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='start must be before end'
        )
    
    if level not in ["INFO", 'WARNING', 'ERROR']:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="invalid log level"
        )
    
    if level in ["WARNING"]:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="not found"
        )
    
    return {
        'start': start,
        'end': end,
        'level': level,
    }


class Sale(BaseModel):
    time: datetime
    customer_id: str = Field(min_length=2)
    amount: int = Field(gt=0)
    price: float = Field(gt=0)


@app.post('/sales/')
def new_sale(sale: Sale):
    # store in database
    return {
        "id": "1234" 
    }


@app.get('/sales/{id}')
def get_sale(id: str) -> Sale:
    # get the data from database
    s = {
        'time': datetime.now(),
        "customer_id": "1234",
        "amount": 100,
        "price": 2.50,

    }
    return s

from fastapi.responses import RedirectResponse
from http import HTTPStatus

@app.post('/survey')
def survey(name: Annotated[str, Form()], 
           happy: Annotated[str, Form()],
           course: Annotated[str, Form()]):
    print("submitted name: ", name)
    print("submitted happy: ", happy)
    print("submitted course: ", course)
    return RedirectResponse(
        url='/static/thanks.html',
        status_code=HTTPStatus.FOUND
    )

from fastapi import Request

@app.post('/example_raw_api')
def example_raw_api(request: Request):
    print(f"{request.headers}")
    return {'headers': request.headers}


MAX_IMAGE_SIZE = 5 * 1024 * 1024

@app.post('/size')
async def size(request: Request):
    size = int(request.headers.get('Content-Length', 0))
    if not size:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='missing content-length header'
        )
    if size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='size can not exceed 5MB'
        )
    
    data = await request.body()
    from io import BytesIO
    io = BytesIO(data)
    from PIL import Image
    image = Image.open(io)
    return {'width': image.width, 'height': image.height}



from enum import Enum
from uuid import uuid4

class OSImage(Enum):
    ubuntu = 'ubuntu:24.04'
    debian = 'debian:bookworm'
    alpine = 'alpine:3.20'

class VirtualMachine(BaseModel):
    cpu_count: int = Field(gt=0, lt=65)
    mem_size_gb: int = Field(ge=8, lt=1025)
    image: OSImage

vms = {}

@app.post('/vm/start')
def start_vm(vm: VirtualMachine):
    id = uuid4()
    vms[id] = vm
    return {'id': id}