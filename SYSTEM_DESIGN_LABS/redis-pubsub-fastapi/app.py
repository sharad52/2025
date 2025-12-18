"""
Redis PubSub FastAPI application
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
import asyncio
import json
from typing import List
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL_NAME = "chat_channel"

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client = None
        self.pubsub = None
        self.listener_task = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")
        
        # Initialize Redis connection if not exists
        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis(
                    host=REDIS_HOST, 
                    port=REDIS_PORT, 
                    decode_responses=True
                )
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis connected successfully")
                
                self.pubsub = self.redis_client.pubsub()
                await self.pubsub.subscribe(CHANNEL_NAME)
                logger.info(f"Subscribed to Redis channel: {CHANNEL_NAME}")
                
                # Start listener if not already running
                if self.listener_task is None:
                    self.listener_task = asyncio.create_task(self.listen_to_redis())
            except Exception as e:
                logger.error(f"Redis connection error: {e}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        """Publish message to Redis"""
        try:
            if self.redis_client:
                await self.redis_client.publish(CHANNEL_NAME, message)
                logger.info(f"Published to Redis: {message}")
        except Exception as e:
            logger.error(f"Error publishing to Redis: {e}")

    async def listen_to_redis(self):
        """Listen to Redis pub/sub and broadcast to all WebSocket clients"""
        logger.info("Started listening to Redis")
        try:
            if self.pubsub:
                async for message in self.pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"]
                        logger.info(f"Received from Redis: {data}")
                        # Send to all connected WebSocket clients
                        disconnected = []
                        for connection in self.active_connections:
                            try:
                                await connection.send_text(data)
                            except Exception as e:
                                logger.error(f"Error sending to client: {e}")
                                disconnected.append(connection)
                        
                        # Remove disconnected clients
                        for conn in disconnected:
                            self.disconnect(conn)
        except Exception as e:
            logger.error(f"Redis listener error: {e}")

manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Application starting up...")

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
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
            }
            #messages {
                border: 1px solid #ccc;
                height: 400px;
                overflow-y: scroll;
                padding: 10px;
                margin-bottom: 10px;
                background-color: white;
                border-radius: 5px;
            }
            .message {
                padding: 8px;
                margin: 5px 0;
                border-radius: 5px;
                background-color: #e3f2fd;
                animation: fadeIn 0.3s;
            }
            .system {
                background-color: #fff3cd;
                font-style: italic;
                color: #856404;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px;
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            button {
                padding: 12px 24px;
                font-size: 16px;
                cursor: pointer;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #45a049;
            }
            button:disabled {
                background-color: #ccc;
                cursor: not-allowed;
            }
            #status {
                padding: 12px;
                margin-bottom: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            .connected {
                background-color: #d4edda;
                color: #155724;
            }
            .disconnected {
                background-color: #f8d7da;
                color: #721c24;
            }
            .connecting {
                background-color: #d1ecf1;
                color: #0c5460;
            }
            #debug {
                margin-top: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-family: monospace;
                font-size: 12px;
                max-height: 150px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <h1>🚀 WebSocket + Redis Pub/Sub Chat</h1>
        <div id="status" class="disconnected">Disconnected</div>
        <div id="messages"></div>
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message..." disabled />
            <button id="sendButton" onclick="sendMessage()" disabled>Send</button>
        </div>
        
        <h3>Debug Info:</h3>
        <div id="debug"></div>
        
        <script>
            let ws;
            let reconnectAttempts = 0;
            const maxReconnectAttempts = 5;
            const messagesDiv = document.getElementById('messages');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const statusDiv = document.getElementById('status');
            const debugDiv = document.getElementById('debug');
            
            function log(message) {
                console.log(message);
                const timestamp = new Date().toLocaleTimeString();
                debugDiv.innerHTML += `[${timestamp}] ${message}<br>`;
                debugDiv.scrollTop = debugDiv.scrollHeight;
            }
            
            function connect() {
                const wsUrl = `ws://${window.location.host}/ws`;
                log(`Attempting to connect to: ${wsUrl}`);
                
                statusDiv.textContent = "Connecting...";
                statusDiv.className = "connecting";
                
                try {
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function(event) {
                        log("WebSocket connection opened successfully!");
                        statusDiv.textContent = "✓ Connected";
                        statusDiv.className = "connected";
                        messageInput.disabled = false;
                        sendButton.disabled = false;
                        reconnectAttempts = 0;
                        addMessage("Connected to server", true);
                    };
                    
                    ws.onmessage = function(event) {
                        log(`Received message: ${event.data}`);
                        addMessage(event.data, false);
                    };
                    
                    ws.onclose = function(event) {
                        log(`WebSocket closed. Code: ${event.code}, Reason: ${event.reason}`);
                        statusDiv.textContent = "✗ Disconnected";
                        statusDiv.className = "disconnected";
                        messageInput.disabled = true;
                        sendButton.disabled = true;
                        addMessage("Disconnected from server", true);
                        
                        // Reconnect logic
                        if (reconnectAttempts < maxReconnectAttempts) {
                            reconnectAttempts++;
                            const delay = Math.min(1000 * reconnectAttempts, 5000);
                            log(`Reconnecting in ${delay/1000} seconds... (Attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                            setTimeout(connect, delay);
                        } else {
                            log("Max reconnection attempts reached. Please refresh the page.");
                            addMessage("Connection lost. Please refresh the page.", true, true);
                        }
                    };
                    
                    ws.onerror = function(error) {
                        log(`WebSocket error: ${error.message || 'Unknown error'}`);
                        console.error("WebSocket error:", error);
                        addMessage("Connection error occurred", true, true);
                    };
                } catch (error) {
                    log(`Error creating WebSocket: ${error.message}`);
                    addMessage("Failed to create WebSocket connection", true, true);
                }
            }
            
            function addMessage(message, isSystem = false, isError = false) {
                const messageElement = document.createElement('div');
                messageElement.className = 'message';
                if (isSystem) messageElement.classList.add('system');
                if (isError) messageElement.classList.add('error');
                
                const timestamp = new Date().toLocaleTimeString();
                messageElement.textContent = `[${timestamp}] ${message}`;
                messagesDiv.appendChild(messageElement);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }
            
            function sendMessage() {
                const message = messageInput.value.trim();
                if (message && ws && ws.readyState === WebSocket.OPEN) {
                    log(`Sending message: ${message}`);
                    ws.send(message);
                    messageInput.value = '';
                } else if (!message) {
                    log("Cannot send empty message");
                } else {
                    log(`Cannot send message. WebSocket state: ${ws ? ws.readyState : 'not initialized'}`);
                    addMessage("Not connected. Cannot send message.", true, true);
                }
            }
            
            messageInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Connect on page load
            log("Page loaded. Initializing WebSocket connection...");
            connect();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = "unknown"
    if manager.redis_client:
        try:
            await manager.redis_client.ping()
            redis_status = "connected"
        except:
            redis_status = "disconnected"
    
    return {
        "status": "ok",
        "websocket_connections": len(manager.active_connections),
        "redis_status": redis_status
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from WebSocket client
            data = await websocket.receive_text()
            logger.info(f"Received from client: {data}")
            
            # Create message with timestamp
            client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
            message = f"[{client_info}]: {data}"
            
            # Publish to Redis (which will broadcast to all clients)
            await manager.broadcast(message)
            
    except WebSocketDisconnect:
        logger.info("Client disconnected normally")
        manager.disconnect(websocket)
        await manager.broadcast(f"Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    