"""
Create Google keys

pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

from libdev.cfg import cfg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = (
    'https://www.googleapis.com/auth/gmail.send',
    # 'https://www.googleapis.com/auth/spreadsheets',
    # 'https://www.googleapis.com/auth/drive',
)


def main():
    creds = None
    if (
        cfg('google.token')
        and cfg('google.refresh_token')
        and cfg('google.token_uri')
        and cfg('google.cliend_id')
        and cfg('google.client_secret')
    ):
        creds = Credentials(
            token=cfg('google.token'),
            refresh_token=cfg('google.refresh_token'),
            token_uri=cfg('google.token_uri'),
            client_id=cfg('google.cliend_id'),
            client_secret=cfg('google.client_secret'),
            scopes=SCOPES,
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES,
            )
            creds = flow.run_local_server(port=0)

    print(creds.to_json())


if __name__ == '__main__':
    main()
