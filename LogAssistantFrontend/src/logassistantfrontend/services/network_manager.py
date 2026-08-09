from queue import Queue
import threading
import websocket
import json
import requests
import os
from typing import Optional
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import streamlit as st

class NetworkManager:
    def __init__(self, http_url: str, ws_url: str):
        self.alert_queue: Queue = Queue()
        self.http_url = http_url
        self.ws_url = ws_url
        self._ws_thread: Optional[threading.Thread] = None

    def start_websocket_listener(self) -> None:
        if self._ws_thread and self._ws_thread.is_alive():
            return

        ctx = get_script_run_ctx()

        def _listen():
            ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=lambda ws, msg: self.on_message(msg),
                on_error=lambda ws, err: print(f"Web socket error: {err}"),
                on_close=lambda ws, *args: print("Web socket connection closed")
            )
            ws.run_forever()

        self._ws_thread = threading.Thread(target=_listen, daemon=True)
        if ctx:
            add_script_run_ctx(self._ws_thread, ctx)
            
        self._ws_thread.start()

    def on_message(self, msg):
        self.alert_queue.put(json.loads(msg))
        print(f"got message {msg}")

    def upload_log_file(self, file_name: str, file_bytes: bytes) -> int:
        files = {"file": (file_name, file_bytes, "text/plain")}
        response = requests.post(self.http_url, files=files, timeout=30)
        return response.status_code

@st.cache_resource
def get_network_manager() -> NetworkManager:
    backend_host = os.getenv("BACKEND_URL", "http://localhost:8000/process-batch")
    backend_ws = os.getenv("BACKEND_WS", "ws://localhost:8000/ws/alerts")
    print("Network manager created")
    return NetworkManager(backend_host, backend_ws)

network_manager = get_network_manager()