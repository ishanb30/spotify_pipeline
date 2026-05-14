
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

    if not data.get("items"):
        print("Missing data from Spotify response")
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

def get_api_data(headers: dict, max_retries: int=3) -> dict:
    last_exception = None
    for i in range(max_retries):
        try:
            response = requests.get(
                "https://api.spotify.com/v1/me/player/recently-played",
                headers=headers,
                timeout=5
            )

            response.raise_for_status()
            data = validate_recently_played(response)
            return data

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
                wait = int(response.headers.get("Retry-After") or 2 ** (i + 1))
                time.sleep(wait)
                last_exception = e
                continue

            else:
                raise RuntimeError(f"Get request failed with status code: {response.status_code}") from e

        except requests.exceptions.RequestException as e:
            raise RuntimeError("Get request failed") from e

    raise RuntimeError("Max retries exhausted") from last_exception

def write_data(headers: dict) -> None:
    data = get_api_data(headers, 3)

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








