import asyncio
import time
from fastapi import FastAPI, HTTPException
from datetime import datetime
from os import environ
from http import HTTPStatus

app = FastAPI()

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