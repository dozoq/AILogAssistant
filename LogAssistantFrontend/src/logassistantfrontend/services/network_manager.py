from queue import Queue
import threading
import time
import websocket
import json
import requests
import os
from typing import Optional
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import streamlit as st


class NetworkManager:
    def __init__(self, http_url: str, ws_url: str, auth_url: str, client_secret: str):
        self.alert_queue: Queue = Queue()
        self.http_url = http_url
        self.ws_url = ws_url
        self.auth_url = auth_url
        self.client_secret = client_secret
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0
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
                on_close=lambda ws, *args: print("Web socket connection closed"),
            )
            ws.run_forever()

        self._ws_thread = threading.Thread(target=_listen, daemon=True)
        if ctx:
            add_script_run_ctx(self._ws_thread, ctx)

        self._ws_thread.start()

    def on_message(self, msg):
        self.alert_queue.put(json.loads(msg))
        print(f"got message {msg}")

    def _get_token(self, force_refresh: bool = False) -> str:
        if not force_refresh and self._token and time.time() < self._token_expires_at:
            return self._token

        response = requests.post(
            self.auth_url,
            data={
                "grant_type": "client_credentials",
                "client_secret": self.client_secret,
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        self._token = payload["access_token"]
        # 30 minut ważności tokena (auth_service.py) minus margines bezpieczeństwa.
        self._token_expires_at = time.time() + (30 * 60) - 60
        return self._token

    def upload_log_file(self, file_name: str, file_bytes: bytes) -> int:
        files = {"file": (file_name, file_bytes, "text/plain")}
        try:
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                self.http_url, files=files, headers=headers, timeout=30
            )

            if response.status_code == 401:
                # Token mógł wygasnąć mimo lokalnego cache'u (np. zegar) albo
                # zostać odrzucony z innego powodu - jedna próba z nowym tokenem.
                token = self._get_token(force_refresh=True)
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.post(
                    self.http_url, files=files, headers=headers, timeout=30
                )

            return response.status_code
        except requests.RequestException as e:
            print(f"upload_log_file network error: {e}")
            return -1


@st.cache_resource
def get_network_manager() -> NetworkManager:
    backend_host = os.getenv("BACKEND_URL", "http://localhost:8000/process-batch")
    backend_ws = os.getenv("BACKEND_WS", "ws://localhost:8000/ws/alerts")
    backend_auth = os.getenv("BACKEND_AUTH_URL", "http://localhost:8000/auth/token")
    client_secret = os.getenv("INTERNAL_CLIENT_SECRET", "InternalSecretPassword2!")
    print("Network manager created")
    return NetworkManager(backend_host, backend_ws, backend_auth, client_secret)


network_manager = get_network_manager()
