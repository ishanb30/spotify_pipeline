"""
run.py - orchestrates each pipeline run

Assumptions:
    1. The table PIPELINE_RUNS exists to be written to

Known Limitations:
    1. If the UPDATE query in the finally block fails, then RUN_STATUS will
       not be updated to FAILED in PIPELINE_RUNS. Therefore, it is possible
       that a failed pipeline run could have a RUN_STATUS of STARTED.
       However the failure is caught and logged to pipeline.log
"""

import uuid
from src.load import load
from src.fetch import get_api_data
from utils.logging import get_logger
from src.connector import get_connection
from datetime import datetime, timezone

run_id = str(uuid.uuid4())
logger = get_logger(__name__, run_id)

watermark = None
status = "STARTED"

try:
    logger.info("Pipeline run started")
    run_start = datetime.now(timezone.utc).replace(tzinfo=None)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO SPOTIFY_PIPELINE.RAW.PIPELINE_RUNS (RUN_ID, RUN_START, RUN_STATUS) "
                "VALUES (%s, %s, %s)",
                (run_id, run_start, status)
            )
            conn.commit()

    data = get_api_data(run_id)
    watermark = load(run_id, data)

    if watermark:
        # dbt orchestration goes here
        status = "COMPLETED"
        # logger.info("dbt transformation layer complete")

    else:
        status = "COMPLETED"
        logger.info("Pipeline exited early - transformation layer skipped")

except Exception as e:
    status = "FAILED"
    logger.error(f"{e} | caused by: {e.__cause__}")

finally:
    run_end = datetime.now(timezone.utc).replace(tzinfo=None)

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE SPOTIFY_PIPELINE.RAW.PIPELINE_RUNS "
                    "SET RUN_END = %s, WATERMARK_TIMESTAMP = %s, RUN_STATUS = %s "
                    "WHERE RUN_ID = %s",
                    (run_end, watermark, status, run_id)
                )
                conn.commit()

        logger.info(f"Pipeline run finalised with status: {status}")

    except Exception as meta_e:
        logger.error(f"Failed to write pipeline metadata to Snowflake: {meta_e}")

