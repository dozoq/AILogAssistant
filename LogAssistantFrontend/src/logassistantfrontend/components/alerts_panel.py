import streamlit as st
from typing import List
from logassistantfrontend.models.models import WebSocketAlert

class AlertsPanelComponent:
    def render(self, alerts: List[WebSocketAlert]) -> None:
        if not alerts:
            st.info("Awaiting cyber threats... Upload a log file in the sidebar to wake up the system.")
            return

        st.write(f"Active Incidents in current session: **{len(alerts)}**")
        
        for idx, alert in enumerate(alerts):
            report = alert.ai_report
            sev = report.severity.upper()
            color = "red" if sev == "CRITICAL" else "orange" if sev == "HIGH" else "blue" if sev == "MEDIUM" else "green"
            
            with st.expander(f"[{sev}] {report.threat_type} — Attacker: {alert.attacker_ip}", expanded=(idx == 0)):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Severity Level:** :{color}[{sev}]")
                    st.markdown(f"**Attacker IP:** `{alert.attacker_ip}`")
                    st.markdown(f"**Detection:** ")
                with col2:
                    st.markdown("**AI Investigation Summary:**")
                    st.info(report.threat_type)
                    st.markdown("**Mitigation plan:**")
                    st.code(report.mitigation_plan, language="bash")
                st.divider()
                st.caption(f"**Raw log line:** `{alert.raw_details}`")
                st.button("Resolve", idx, on_click=lambda _: alerts.remove(alert)  )