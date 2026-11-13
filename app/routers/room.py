from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.room import RoomCreate, RoomInfo, RoomOut, RoomVerify
from app.services.connection_manager import manager

router = APIRouter()

@router.post("/", response_model=RoomOut)
def create_room(room: RoomCreate):
    try:
        manager.create_room(room.name, room.password)
        return RoomOut(name=room.name, private=bool(room.password))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[RoomInfo])
def list_rooms():
    return manager.list_rooms()

@router.post("/verify")
def verify_room(data: RoomVerify):
    if data.name not in manager.active_connections:
        raise HTTPException(status_code=404, detail="Room not found")
    if not manager.authenticate(data.name, data.password):
        raise HTTPException(status_code=403, detail="Incorrect room password")
    if data.username and manager.is_username_taken(data.name, data.username):
        raise HTTPException(status_code=409, detail=f"Username '{data.username}' is already taken in this room")
    return {"status": "ok"}

@router.delete("/{room_name}", status_code=204)
def delete_room(room_name: str):
    try:
        manager.delete_room(room_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
