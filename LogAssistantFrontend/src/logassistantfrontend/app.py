import streamlit as st
import os
from logassistantfrontend.models.models import WebSocketAlert
from logassistantfrontend.services import NetworkManager
from logassistantfrontend.components.sidebar import SidebarComponent
from logassistantfrontend.components.alerts_panel import AlertsPanelComponent


class LogAssistantApp:
    def __init__(self):
        st.set_page_config(page_title="Log Analyst Dashboard", page_icon="🪳")
        self.sidebar = SidebarComponent()
        self.alerts_panel = AlertsPanelComponent()

        if "history" not in st.session_state:
            st.session_state.history = []


    def run(self) -> None:
        st.title("Log Assistant")
        st.subheader("Autonomous Real-Time Threat Detection System")

        NetworkManager.start_websocket_listener()
        self.sidebar.render()
        self._render_reactive_alerts_panel()

    @st.fragment(run_every="1s")
    def _render_reactive_alerts_panel(self) -> None:
        self._process_incoming_queue()
        
        alerts_panel = AlertsPanelComponent()
        alerts_panel.render(st.session_state.history)

    def _process_incoming_queue(self) -> bool:
        while not NetworkManager.alert_queue.empty():
            raw_data = NetworkManager.alert_queue.get()
            try:
                validated_alert = WebSocketAlert.model_validate(raw_data)
                st.session_state.history.insert(0, validated_alert)
            except Exception as e:
                print(f"queue exception: {e}")

app = LogAssistantApp()
app.run()