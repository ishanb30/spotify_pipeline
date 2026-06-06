"""
connector.py - Connects to Snowflake warehouse, database, and schema based
on credentials stored in .env.

Assumptions:
    1. .env exists at the project root - path resolved relative to
        utils/paths.py, not the working directory

    2. The six .env variable names are the exhaustive set - adding new ones
       requires updating var_names

    3. Credentials are valid at the time of the call - no retry on auth
       failure, no credential rotation handling

    4. Caller is responsible for closing the connection - no pooling, no
       reuse, no automatic cleanup unless caller uses with

    5. Any errors propagate naturally and are handled by the callers
"""

import snowflake.connector
from utils.helpers import _load_env

def get_connection() -> snowflake.connector.SnowflakeConnection:
    var_names = ["ACCOUNT_IDENTIFIER", "USERNAME", "PASSWORD", "DATA_WAREHOUSE", "DATABASE", "SCHEMA"]
    env_var = _load_env(var_names)

    connection = snowflake.connector.connect(
        account=env_var["ACCOUNT_IDENTIFIER"],
        user=env_var["USERNAME"],
        password=env_var["PASSWORD"],
        warehouse=env_var["DATA_WAREHOUSE"],
        database=env_var["DATABASE"],
        schema=env_var["SCHEMA"],
        autocommit=False
    )

    return connection

if __name__ == "__main__":
    with get_connection() as conn:
        print("Connection successful")

