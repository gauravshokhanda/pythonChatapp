# app/websocket_server.py

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from datetime import datetime
from app.services import (
    create_message,
    update_message_status,
    mark_message_seen,
    get_or_create_conversation,
)

active_connections: Dict[str, WebSocket] = {}
online_users = set()

def websocket_app(app):
    @app.websocket("/ws/{user_id}")
    async def chat_socket(websocket: WebSocket, user_id: str):
        await websocket.accept()
        active_connections[user_id] = websocket
        online_users.add(user_id)
        print(f"🔌 {user_id} connected")

        try:
            while True:
                data = await websocket.receive_json()
                event_type = data.get("type")

                if event_type == "message":
                    await handle_message(data, user_id)
                elif event_type == "seen":
                    message_id = data.get("message_id")
                    mark_message_seen(message_id)

        except WebSocketDisconnect:
            print(f"❌ {user_id} disconnected")
            active_connections.pop(user_id, None)
            online_users.discard(user_id)

async def handle_message(data, sender_id):
    receiver_id = str(data.get("to"))
    content = data.get("message")

    # Create or get conversation ID
    conversation_id = get_or_create_conversation(sender_id, receiver_id)

    # Save message
    msg_id = create_message({
        "conversation_id": conversation_id,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "content": content,
        "status": "sent"
    })

    # Prepare message payload
    message_data = {
        "from": sender_id,
        "to": receiver_id,
        "message": content,
        "conversation_id": conversation_id,
        "timestamp": datetime.now().isoformat(),
        "message_id": msg_id
    }

    # Send to receiver if online
    if receiver_id in active_connections:
        await active_connections[receiver_id].send_json(message_data)
        update_message_status(msg_id, "delivered")

    # Also send to sender (for real-time chat update)
    if sender_id in active_connections:
        await active_connections[sender_id].send_json(message_data)
