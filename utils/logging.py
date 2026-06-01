
import logging
import os
from utils.paths import LOGS_DIR

def get_logger(name: str, run_id: str) -> logging.LoggerAdapter:
    root = logging.getLogger()

    if not root.handlers:
        os.makedirs(LOGS_DIR, exist_ok=True)

        handler = logging.FileHandler(LOGS_DIR / "pipeline.log")
        formatter = logging.Formatter(
            "%(asctime)s - %(run_id)s - %(funcName)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        root.setLevel(logging.INFO)
        root.addHandler(handler)

    logger = logging.getLogger(name)
    adapter = logging.LoggerAdapter(logger, {"run_id": run_id})

    return adapter





