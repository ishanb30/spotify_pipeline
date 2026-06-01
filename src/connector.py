"""
connector.py - Connects to Snowflake warehouse, database, and schema based
on credentials stored in .env.

Assumptions:
    1. .env exists at the project root - path resolved relative to
        utils/env.py, not the working directory

    2. The six .env variable names are the exhaustive set - adding new ones
       requires updating var_names

    3. Credentials are valid at the time of the call - no retry on auth
       failure, no credential rotation handling

    4. Caller is responsible for closing the connection - no pooling, no
       reuse, no automatic cleanup unless caller uses with

    5. Auth failures and bad config raise DatabaseError; network failures
       raise OSError - anything outside these two categories is unhandled
"""

from dotenv import load_dotenv
import os
import snowflake.connector
from utils.paths import ENV_PATH

def load_env() -> dict:
    load_dotenv(ENV_PATH)

    var_names = ["ACCOUNT_IDENTIFIER", "USERNAME", "PASSWORD", "DATA_WAREHOUSE", "DATABASE", "SCHEMA"]
    env_var = {}
    for var in var_names:
        var_value = os.environ.get(var)
        if var_value is None:
            raise ValueError(f"Variable name ({var}) is missing from .env")
        else:
            env_var[var] = var_value

    return env_var

def get_connection() -> snowflake.connector.SnowflakeConnection:
    env_var = load_env()

    try:
        connection = snowflake.connector.connect(
            account=env_var["ACCOUNT_IDENTIFIER"],
            user=env_var["USERNAME"],
            password=env_var["PASSWORD"],
            warehouse=env_var["DATA_WAREHOUSE"],
            database=env_var["DATABASE"],
            schema=env_var["SCHEMA"],
            autocommit=False
        )

    except snowflake.connector.errors.DatabaseError as e:
        raise RuntimeError("Failed to connect to Snowflake") from e

    except OSError as e:
        raise RuntimeError("Failed to connect to Snowflake due to network error") from e

    return connection

if __name__ == "__main__":
    with get_connection() as conn:
        print("Connection successful")

