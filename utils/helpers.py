
import time
import random
from dotenv import load_dotenv
import os
from utils.paths import ENV_PATH

def delay_retry(i: int) -> None:
    jitter = random.randint(1, 6)
    time.sleep(2 ** (i + 1) + jitter)

def _load_env(var_names: list[str]) -> dict:
    load_dotenv(ENV_PATH)

    env_var = {}
    for var in var_names:
        var_value = os.environ.get(var)
        if var_value is None:
            raise ValueError(f"Variable name ({var}) is missing from .env")

        env_var[var] = var_value

    return env_var