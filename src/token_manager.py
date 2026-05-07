
from dotenv import load_dotenv
import os
import json
from pathlib import Path
import time
import base64
import requests


def load_tokens():
    try:
        with open(Path(__file__).parent / "tokens.json", "r") as f:
            data = json.load(f)

        return data

    except FileNotFoundError as e:
        raise FileNotFoundError("tokens.json not found - run auth.py first") from e


load_dotenv()
REDIRECT_URI = "http://127.0.0.1:3000"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Missing client information")


def create_request_params():
    refresh_token = load_tokens()["refresh_token"]
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}"}

    return data, headers

def update_tokens_json(response):
    updated_token_data = response.json()

    access_token = updated_token_data["access_token"]
    refresh_token = updated_token_data.get("refresh_token", load_tokens()["refresh_token"])
    expires_at = time.time() + updated_token_data["expires_in"]

    tokens_json = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }

    with open(Path(__file__).parent / "tokens.json", "w") as f:
        json.dump(tokens_json, f)

    return access_token

def get_access_token():
    token_data = load_tokens()
    if time.time() > token_data["expires_at"]:
        data, headers = create_request_params()
        response = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
        response.raise_for_status()
        access_token = update_tokens_json(response)
        return access_token

    else:
        access_token = token_data["access_token"]
        return access_token
