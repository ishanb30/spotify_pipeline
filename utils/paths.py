
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

ENV_PATH = BASE_DIR / ".env"
LOGS_DIR = BASE_DIR / "logs"
SRC_DIR = BASE_DIR / "src"
DBT_DIR = BASE_DIR / "transform"