from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from src.config.config import templates
from src.database.database import get_last_messages_from_db, add_messages
from src.secure.secure import get_current_user

from src.services.ws_manager import manager

router = APIRouter(
    prefix="/chat",
    tags=["chats"]
)


@router.get("/auth_user")
def get_chat_page(request: Request, current_user: Optional[dict] = Depends(get_current_user)):
    user = current_user['sub']
    username = user['username']
    id = user['id']
    return templates.TemplateResponse("chat.html", {"request": request, "id": id, "username": username})


@router.get("")
def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request, "id": 1, "username": 'username'})


@router.get("1")
def get_chat_page1(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request, "id": 2, "username": 'username2'})


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            recipient_user_id, message = data.split(":")
            await manager.send_personal_message(f"Пользователь #{client_id} написал: {message}", websocket)
            for connection in manager.active_connections:
                if connection.scope.get("path").split("/")[-1] == recipient_user_id:
                    await add_messages(sender_id=int(client_id), receiver_id=int(recipient_user_id), message=message)
                    await manager.send_personal_message(f"Пользователь #{client_id} написал: {message}", connection)
                    break

    except WebSocketDisconnect as error:
        manager.disconnect(websocket)


@router.get("/last_messages")
async def get_last_messages(id):
    messages = await get_last_messages_from_db(int(id))
    return messages[::-1]
