import sys
import streamlit.web.cli as stcli

def main() -> None:
    sys.argv = ["streamlit", "run", "./src/logassistantfrontend/app.py"]
    sys.exit(stcli.main())
