"""
Redis PubSub FastAPI application
"""
import json
import asyncio
import uvicorn
import redis.asyncio as redis
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


app = FastAPI()


# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "chat_channel"


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self.redis_client = None
        self.pubsub = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

        # Initialize Redis connection if not exists
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(CHANNEL_NAME)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Publish message to Redis"""
        if self.redis_client:
            await self.redis_client.publish(CHANNEL_NAME, message)
    async def listen_to_redis(self):
        """Listen to Redis pub/sub and broadcast to all WebSocket clients"""
        if self.pubsub:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    # Send to all connected WebSocket clients
                    for connection in self.active_connections:
                        try:
                            await connection.send_text(data)
                        except:
                            pass


manager = ConnectionManager()