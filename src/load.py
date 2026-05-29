"""
load.py - connects to Snowflake database and loads data

Assumptions:
    1. get_api_data() either returns an empty list or a list of dicts
    2. RECENTLY_PLAYED table exists in the schema configured in .env with
       a RAW_DATA VARIANT column
    3. An empty list is an expected state, not an error — load() returns
       silently without opening a connection
"""


from token_manager import get_auth_headers
from fetch import get_api_data
from connector import get_connection
import json
import snowflake.connector
from utils.helpers import delay_retry

def load(max_retries: int=3):
    headers = get_auth_headers()
    data = get_api_data(headers, max_retries)

    if data:
        last_exception = None
        for i in range(max_retries + 1):
            with get_connection() as conn:
                try:
                    with conn.cursor() as cursor:
                        for d in data:
                            cursor.execute(
                                "INSERT INTO RECENTLY_PLAYED (RAW_DATA) "
                                "SELECT PARSE_JSON(%s)",
                                (json.dumps(d),)
                            )

                        break

                except snowflake.connector.errors.OperationalError as e:
                    delay_retry(i)
                    last_exception = e

                except snowflake.connector.errors.DatabaseError as e:
                    raise RuntimeError("Failed to load to RECENTLY_PLAYED via Snowflake connector") from e

                except OSError as e:
                    delay_retry(i)
                    last_exception = e

        else:
            if isinstance(last_exception, snowflake.connector.errors.OperationalError):
                raise RuntimeError("Max retries exhausted: "
                                   "Failed to load to RECENTLY_PLAYED via Snowflake connector") from last_exception

            elif isinstance(last_exception, OSError):
                raise RuntimeError("Max retries exhausted: "
                                   "Failed to load to Snowflake due to network error") from last_exception


if __name__ == "__main__":
    load(3)







