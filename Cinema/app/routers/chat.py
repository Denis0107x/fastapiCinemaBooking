import asyncio
import json
from fastapi import APIRouter, WebSocket, Depends, Cookie, WebSocketDisconnect
from typing import List
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.core.security import decode_token
import logging

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)
        logging.info(f"WebSocket connection established: {websocket.client}")

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections:
                try:
                    if websocket.application_state != WebSocketState.DISCONNECTED:
                        await websocket.close()
                        logging.info(f"WebSocket connection closed: {websocket.client}")
                except RuntimeError as e:
                    logging.error(f"Failed to close WebSocket connection for {websocket.client}: {e}")
                finally:
                    self.active_connections.remove(websocket)


    async def broadcast(self, message: str):
        async with self.lock:
            for connection in self.active_connections:
                if connection.application_state == WebSocketState.CONNECTED:
                    try:
                        await connection.send_text(message)
                    except RuntimeError as e:
                        logging.error(f"Failed to send message to {connection.client}: {e}")
                        await self.disconnect(connection)
                    finally:
                        if connection.application_state != WebSocketState.CONNECTED:
                            logging.error(f"Connection state after send attempt: {connection.application_state}")
                else:
                    logging.error(f"Connection {connection.client} is not in CONNECTED state, skipping message sending.")
        logging.info(f"Broadcasted message: {message}")



manager = ConnectionManager()

@router.websocket("/ws/movies/{movie_id}")
async def websocket_endpoint(websocket: WebSocket, movie_id: int, db: Session = Depends(get_db), access_token: str = Cookie(default=None)):
    await manager.connect(websocket)
    
    user = "Anonymous"
    user_id = None

    try:
        if access_token:
            token_data = decode_token(access_token)
            if token_data:
                username = token_data.get("email")
                userdata = crud.get_user_by_email(db=db, email=username)
                if userdata:
                    user = userdata.username
                    user_id = userdata.id
        
        if not user_id:
            await websocket.send_text(json.dumps({"error": "User authentication failed"}))
            await manager.disconnect(websocket)
            return
        
        # Notify about user connection
        await manager.broadcast(json.dumps({"system": f"{user} has connected."}))
        
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                if "text" in message_data:
                    message_text = message_data["text"]
                    message = schemas.MessageCreate(text=message_text, user_id=user_id, movie_id=movie_id)
                    created_message = crud.create_message(db, message, user_id, movie_id)
                    if created_message:
                        message_broadcast = {"username": user, "text": message_text}
                        await manager.broadcast(json.dumps(message_broadcast))
                    else:
                        logging.error("Failed to create message")
                else:
                    logging.error("Received message does not contain 'text' key")
            except WebSocketDisconnect:
                logging.info(f"WebSocket disconnected: {websocket.client}")
                break
            except Exception as e:
                logging.error(f"Error processing WebSocket message: {e}")
                continue
    except Exception as e:
        logging.error(f"Error in WebSocket endpoint: {e}")
    finally:
        # Notify about user disconnection
        await manager.broadcast(json.dumps({"system": f"{user} has disconnected."}))
        await manager.disconnect(websocket)
