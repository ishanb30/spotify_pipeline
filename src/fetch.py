"""
fetch.py — Fetches recently played tracks from the Spotify Web API and writes
them to a local JSON file (temporary scaffolding, to be replaced by Snowflake
connector).

Assumptions:
    1. Valid auth headers are passed in by the caller (via token_manager).
       The script also assumes write permissions on the /src directory.

    2. The Spotify API returns a JSON object (dict) at the top level. If the
       response cannot be parsed or is not a dict, a RuntimeError is raised
       before any field access is attempted.

    3. Each item in the response must contain: track, played_at, context.
       track and played_at must be non-null. context may be null — expected
       when tracks are played directly from search with no playlist or album
       context.

    4. The API returns items ordered most recent to oldest. The before cursor
       moves backwards in time on each page. If this ordering were reversed,
       the pagination loop would have no natural stopping condition and would
       continue requesting progressively older data indefinitely.

    5. Pagination termination is detected in two ways: (a) an empty items list
       signals no more data exists; (b) a non-null page with no cursor signals
       the last page was reached. In practice, (a) is the common case.

    6. The Retry-After header, when present on a 429 response, is assumed to
       be a parseable numeric string (e.g. "30" or "1.5"). If absent, falls
       back to exponential backoff.

    7. No watermark lower bound is applied. Every run fetches all available
       recently played tracks. Deduplication is not handled here — deferred
       until the run log table exists in Snowflake.

    8. write_data silently skips the file write if no tracks are returned.
       The caller receives no signal that a write was skipped — upstream logs
       in get_api_data are the only indicator.
"""
import requests
from token_manager import get_auth_headers
import time
import random
from pathlib import Path
import json
import os

SRC_DIR = Path(__file__).parent

def delay_retry(i: int) -> None:
    jitter = random.randint(1, 10)
    time.sleep(2 ** (i + 1) + jitter)

def validate_recently_played(response: requests.Response) -> dict:
    try:
        data = response.json()

    except requests.exceptions.JSONDecodeError as e:
        raise RuntimeError("Malformed JSON response - cannot be parsed") from e

    if not isinstance(data, dict):
        raise RuntimeError("JSON response is not a dict - cannot be validated")

    if "items" not in data:
        raise RuntimeError("Required key (items) missing from Spotify response")

    if "cursors" not in data:
        raise RuntimeError("Required key (cursors) missing from Spotify response")
    elif data["cursors"] is None:
        pass
    elif "before" not in data["cursors"]:
        raise RuntimeError("Required key (before) missing from Spotify response")

    if not data["items"]:
        return data

    items = data["items"]
    required = ["track", "played_at", "context"]
    non_null = ["track", "played_at"]
    for item in items:
        for key in required:
            if key not in item:
                raise RuntimeError(f"Required key ({key}) missing from Spotify response")
            elif key in non_null:
                if not item[key]:
                    raise ValueError(f"Missing data from {key}")

    return data

def get_api_data(headers: dict, max_retries: int=3) -> list:
    all_items = []
    cursor = None
    page_number = 0
    while True:
        page_number += 1
        last_exception = None
        for i in range(max_retries):
            try:
                response = requests.get(
                    "https://api.spotify.com/v1/me/player/recently-played",
                    headers=headers,
                    params={"before": cursor, "limit": 50} if cursor else {"limit": 50},
                    timeout=5
                )

                response.raise_for_status()
                data = validate_recently_played(response)
                break

            except requests.exceptions.ConnectionError as e:
                delay_retry(i)
                last_exception = e
                continue

            except requests.exceptions.Timeout as e:
                delay_retry(i)
                last_exception = e
                continue

            except requests.exceptions.HTTPError as e:
                if response.status_code >= 500:
                    delay_retry(i)
                    last_exception = e
                    continue

                elif response.status_code == 429:
                    wait = float(response.headers.get("Retry-After") or 2 ** (i + 1))
                    time.sleep(wait)
                    last_exception = e
                    continue

                else:
                    raise RuntimeError(f"Get request failed with status code: {response.status_code}") from e

            except requests.exceptions.RequestException as e:
                raise RuntimeError("Get request failed") from e

        else:
            raise RuntimeError(f"Max retries exhausted on page {page_number}") from last_exception

        items = data["items"]
        if items:
            all_items.extend(items)
        elif page_number == 1:
            print("Page 1 is empty - no tracks listened to recently")
            break
        else:
            print(f"Pagination complete after page {page_number - 1} - no more tracks to fetch")
            break

        cursors = data["cursors"]
        if cursors is not None and cursors["before"]:
            cursor = cursors["before"]
        else:
            print(f"Pagination complete - no more pages left for cursor to point to after page {page_number - 1}")
            break

    return all_items

def write_data(headers: dict) -> None:
    data = get_api_data(headers, 3)

    if data:
        try:
            with open(SRC_DIR / "src_data.json.tmp", "w") as f:
                json.dump(data, f)

        except IOError as e:
            try:
                os.remove(SRC_DIR / "src_data.json.tmp")
            except IOError as e:
                pass
            raise IOError("Failed to write src_data.json.tmp - cleanup attempted") from e

        try:
            os.replace(SRC_DIR / "src_data.json.tmp", SRC_DIR / "src_data.json")
        except IOError as e:
            try:
                os.remove(SRC_DIR / "src_data.json.tmp")
            except IOError as e:
                pass
            raise IOError("Atomic swap failed - src_data.json.tmp has correct data") from e

if __name__ == "__main__":
    headers = get_auth_headers()
    write_data(headers)








