
from dotenv import load_dotenv
import os
import urllib.parse
import webbrowser
import requests
import http.server
import base64
import time
import json
from pathlib import Path


class CatchRedirectURI(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_string = urllib.parse.parse_qs(parsed_url.query)
        if "code" not in query_string.keys():
            raise RuntimeError("User denied access")
        CatchRedirectURI.auth_code = query_string["code"][0]

load_dotenv()
REDIRECT_URI = "http://127.0.0.1:3000"
SCOPE = "user-read-recently-played"
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Missing client information")

auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE
})


server = http.server.HTTPServer(("127.0.0.1", 3000), CatchRedirectURI)
webbrowser.open(auth_url)
server.handle_request()

data = {
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code": CatchRedirectURI.auth_code
}

credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded = base64.b64encode(credentials.encode()).decode()
headers = {"Authorization": f"Basic {encoded}"}

response = requests.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
response.raise_for_status()
token_data = response.json()

access_token = token_data["access_token"]
refresh_token = token_data["refresh_token"]
expires_at = time.time() + token_data["expires_in"]

tokens_json = {
    "access_token": access_token,
    "refresh_token": refresh_token,
    "expires_at": expires_at
}

with open(Path(__file__).parent / "tokens.json", "w") as f:
    json.dump(tokens_json, f)
