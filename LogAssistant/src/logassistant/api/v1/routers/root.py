from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from logassistant.services.connection_manager import connection_manager

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_root():
    return JSONResponse(status_code=418, content="I'm a teapot")


@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
