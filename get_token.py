import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()
SCOPES = os.getenv("GMAIL_SCOPES").split(",")

def main():
    base_dir = os.path.dirname(__file__)
    token_path = os.path.join(base_dir, 'config', 'token.json')
    credentials_path = os.path.join(base_dir, 'config', 'credentials.json')
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    print("token.json generado correctamente.")

if __name__ == '__main__':
    main()
