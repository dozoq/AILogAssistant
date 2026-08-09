from fastapi import Depends, FastAPI, UploadFile, File, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from logassistant.services.connection_manager import connection_manager
from logassistant.services.log_service import LogService

app = FastAPI()
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def get_root():
    return JSONResponse(status_code=418, content="I'm a teapot")

@app.post("/process-batch")
async def process_batch_data(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        log_analyzer_service: LogService = Depends(LogService)
    ):
    background_tasks.add_task(log_analyzer_service.run_analysis, file)
    return JSONResponse(status_code=202, content="Accepted")

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)