from fastapi import APIRouter, WebSocket

from controllers.ws_controller import handle_websocket_connection

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket_connection(websocket)
