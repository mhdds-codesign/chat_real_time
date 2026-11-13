import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.services.connection_manager import manager

router = APIRouter()

@router.websocket("/{room_name}")
async def websocket_endpoint(
    websocket: WebSocket,
    room_name: str,
    username: str = Query(...),
    password: Optional[str] = Query(None),
):
    # 1) Verifica existência da sala
    if room_name not in manager.active_connections:
        await websocket.accept()
        await websocket.send_json({
            "username": "system",
            "message": f"Room '{room_name}' does not exist.",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error"
        })
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Room does not exist")
        return

    # 2) Verifica senha se sala for privada
    if not manager.authenticate(room_name, password):
        await websocket.accept()
        await websocket.send_json({
            "username": "system",
            "message": "Incorrect room password.",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error"
        })
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Incorrect room password")
        return

    # 3) Impede nickname duplicado
    if manager.is_username_taken(room_name, username):
        await websocket.accept()
        await websocket.send_json({
            "username": "system",
            "message": f"User '{username}' already exists in this room.",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error"
        })
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Username already taken")
        return

    # Conecta e notifica entrada
    await manager.connect(room_name, username, websocket)
    await manager.broadcast(room_name, {
        "username": "system",
        "message": f"{username} joined the room.",
        "timestamp": datetime.utcnow().isoformat(),
        "type": "system"
    })

    try:
        while True:
            text = await websocket.receive_text()
            timestamp = datetime.utcnow().isoformat()

            # Se for JSON, usa payload; senão, trata como texto
            try:
                payload = json.loads(text)
                msg = {
                    "username": username,
                    "timestamp": timestamp,
                    **payload
                }
            except json.JSONDecodeError:
                msg = {
                    "username": username,
                    "timestamp": timestamp,
                    "type": "text",
                    "message": text
                }

            await manager.broadcast(room_name, msg)

    except WebSocketDisconnect:
        manager.disconnect(room_name, username)
        await manager.broadcast(room_name, {
            "username": "system",
            "message": f"{username} left the room.",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "system"
        })
