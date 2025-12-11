from google_auth_oauthlib.flow import InstalledAppFlow
import os

from auth_config import SCOPES

# Combined Scopes

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def setup_auth():
    print("Starting Authentication Setup...")
    print(f"Requesting scopes: {SCOPES}")
    
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"ERROR: {CREDENTIALS_FILE} not found!")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    # redirect_uris in credentials.json is usually http://localhost which supports any port for Desktop apps,
    # but sometimes specifying a fixed port helps.
    creds = flow.run_local_server(port=8080)
    
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print(f"Success! {TOKEN_FILE} created with all permissions.")

if __name__ == "__main__":
    setup_auth()
