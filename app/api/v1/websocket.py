from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for any client messages if needed
            # For this use case, we primarily push updates to clients
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
