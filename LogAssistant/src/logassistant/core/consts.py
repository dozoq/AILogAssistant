from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CWD = BASE_DIR.parent.parent
ENV = CWD / ".env"