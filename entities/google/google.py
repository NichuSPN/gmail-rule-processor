import os
import json
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()


class GoogleService:
    def __init__(self, service_name, version, scopes, cred_path=None, token_path=None):
        self.service_name = service_name
        self.version = version
        self.scopes = scopes
        self.cred_path = cred_path or os.getenv(
            "GOOGLE_CREDENTIALS_PATH", "credentials.json"
        )
        self.token_path = token_path or os.getenv("GOOGLE_TOKEN_PATH", "token.json")
        self.service = None

    def authenticate(self):
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(self.token_path).read()), self.scopes
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.cred_path, self.scopes
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build(self.service_name, self.version, credentials=creds)
        print("Authenticated... Let's Go...")
        return self.service

    def logout(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
