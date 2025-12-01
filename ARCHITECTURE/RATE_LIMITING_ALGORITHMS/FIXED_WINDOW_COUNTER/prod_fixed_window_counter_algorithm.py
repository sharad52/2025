import time
from fastapi import FastAPI, Request, HTTPException
import redis


LIMIT = 100 # requests
WINDOW = 60 # Seconds

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


def key_for_the_requests(req: Request):
    """Evaluate key for for the request"""
    return f"rl:{req.headers.get('X-API-Key', req.client.host)}"

def is_allowed(key):
    """Production ready fixed window counter with redis INCR with EXPIRE Fallback"""
    current = r.incr(key)
    if current == 1:
        r.expire(key, WINDOW)
    if current > LIMIT:
        ttl = r.ttl(key)
        return False, ttl
    return True, r.ttl(key)

app = FastAPI()

@app.get("/")
async def root(request: Request):
    allowed, ttl = is_allowed(key_for_the_requests(request))
    if not allowed:
        raise HTTPException(status_code=429, detail="Too Many Request")
    return {"msg": "OK", "reset_in": ttl}
