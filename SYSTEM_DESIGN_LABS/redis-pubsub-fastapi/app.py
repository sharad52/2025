"""
Redis PubSub FastAPI application
"""
import json
import asyncio
from fastapi.routing import Lifespan
import uvicorn
import redis.asyncio as redis
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager


app = FastAPI(lifespan=Lifespan)


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start Redis listner on startup"""
    asyncio.create_task(manager.listen_to_redis)


@app.get("/")
async def get():
    """Serve HTML test interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Redis Chat</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
            }
            #messages {
                border: 1px solid #ccc;
                height: 400px;
                overflow-y: scroll;
                padding: 10px;
                margin-bottom: 10px;
                background-color: #f9f9f9;
            }
            .message {
                padding: 8px;
                margin: 5px 0;
                border-radius: 5px;
                background-color: #e3f2fd;
            }
            .system {
                background-color: #fff3cd;
                font-style: italic;
            }
            input[type="text"] {
                width: 70%;
                padding: 10px;
                font-size: 16px;
            }
            button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            button:hover {
                background-color: #45a049;
            }
            #status {
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 5px;
            }
            .connected {
                background-color: #d4edda;
                color: #155724;
            }
            .disconnected {
                background-color: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <h1>WebSocket + Redis Pub/Sub Chat</h1>
        <div id="status" class="disconnected">Disconnected</div>
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type your message..." />
        <button onclick="sendMessage()">Send</button>
        
        <script>
            let ws;
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            const statusDiv = document.getElementById('status');
            
            function connect() {
                ws = new WebSocket("ws://localhost:8000/ws");
                
                ws.onopen = function(event) {
                    statusDiv.textContent = "Connected";
                    statusDiv.className = "connected";
                    addMessage("Connected to server", true);
                };
                
                ws.onmessage = function(event) {
                    addMessage(event.data, false);
                };
                
                ws.onclose = function(event) {
                    statusDiv.textContent = "Disconnected";
                    statusDiv.className = "disconnected";
                    addMessage("Disconnected from server", true);
                    // Reconnect after 3 seconds
                    setTimeout(connect, 3000);
                };
                
                ws.onerror = function(error) {
                    console.error("WebSocket error:", error);
                };
            }
            
            function addMessage(message, isSystem = false) {
                const messageElement = document.createElement('div');
                messageElement.className = isSystem ? 'message system' : 'message';
                messageElement.textContent = message;
                messagesDiv.appendChild(messageElement);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function sendMessage() {
                const message = messageInput.value.trim();
                if (message && ws.readyState === WebSocket.OPEN) {
                    ws.send(message);
                    messageInput.value = '';
                }
            }
            
            messageInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Connect on page load
            connect();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from WebSocket client
            data = await websocket.receive_text()

            # Create message with timestamp
            message = f"[{websocket.client.host}]: {data}"

            #publish to Redis (which will broadcast to all clients)
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {websocket.client.host} disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    