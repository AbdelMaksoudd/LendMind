from fastapi import WebSocket, WebSocketDisconnect

from ws_manager import manager


async def handle_websocket_connection(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
