# Single process dev use

import time
from fastapi import FastAPI, Request, HTTPException


app = FastAPI()
LIMIT = 100 # requests
WINDOW = 60 # seconds
counters = {} # key -> (window_current, count)


def key_for_requests(req: Request):
    return req.client.host


def is_allowed(key):
    now = int(time.time())
    start, count = counters.get(key, (now, 0))
    if now - start >= WINDOW:
        counters[key] = (now, 1)
        return True, WINDOW - 1
    if count < LIMIT:
        counters[key] = (start, count + 1)
        return True, LIMIT - (count +1)
    return False, 0

@app.get("/")
async def root(request: Request):
    allowed, remaining = is_allowed(key_for_requests(request))
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests")
    return {"msg": "OK", "ramining": remaining}