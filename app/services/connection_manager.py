from typing import Dict, Optional

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.rooms_passwords: Dict[str, str] = {}
        # اتاق‌های پیش‌فرض جهت تست اولیه (Public & Private)
        self.create_room("general")
        self.create_room("vip-lounge", "admin123")

    def create_room(self, name: str, password: Optional[str] = None):
        if name in self.active_connections:
            raise ValueError("Sala já existe")
        self.active_connections[name] = {}
        if password:
            self.rooms_passwords[name] = password

    def delete_room(self, name: str):
        if name not in self.active_connections:
            raise ValueError("Sala não existe")
        # opcional: só permitir se não há usuários dentro
        if self.active_connections[name]:
            raise ValueError("Não é possível deletar uma sala com usuários ativos")
        del self.active_connections[name]
        self.rooms_passwords.pop(name, None)

    def list_rooms(self):
        return [
            {
                "name": room,
                "private": room in self.rooms_passwords,
                "users": len(self.active_connections.get(room, {}))
            }
            for room in self.active_connections
        ]

    def authenticate(self, room: str, password: Optional[str] = None) -> bool:
        if room not in self.rooms_passwords:
            return True
        return self.rooms_passwords[room] == (password or "")

    def is_username_taken(self, room: str, username: str) -> bool:
        return username in self.active_connections.get(room, {})

    async def connect(self, room: str, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room][username] = websocket

    def disconnect(self, room: str, username: str):
        self.active_connections.get(room, {}).pop(username, None)

    async def broadcast(self, room: str, message: dict):
        for conn in list(self.active_connections.get(room, {}).values()):
            await conn.send_json(message)

# instância única
manager = ConnectionManager()
