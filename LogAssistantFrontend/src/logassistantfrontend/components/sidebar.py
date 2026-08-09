import streamlit as st
from logassistantfrontend.services import NetworkManager

class SidebarComponent:
    def render(self) -> None:
        with st.sidebar:
            st.header("Control Panel")
            uploaded_file = st.file_uploader("Upload network logs", type=["log", "txt"])
            
            st.page_link(page="https://github.com/dozoq/AILogAssistant", label="Github Repo")
            if uploaded_file is not None:
                if st.button("Analyse", use_container_width=True):
                    with st.spinner("Analysing"):
                        status = NetworkManager.upload_log_file(uploaded_file.name, uploaded_file.getvalue())
                        if status == 202:
                            st.success("File uploaded successfull")
                        else:
                            st.error(f"error, server redurned: {status}")