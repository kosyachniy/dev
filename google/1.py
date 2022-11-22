"""
Google Documents functionality for the API
"""

from libdev.cfg import cfg
import gspread
# from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = (
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
)


# credentials = Credentials(
#     token=cfg('google.token'),
#     refresh_token=cfg('google.refresh_token'),
#     token_uri=cfg('google.token_uri'),
#     client_id=cfg('google.cliend_id'),
#     client_secret=cfg('google.client_secret'),
#     scopes=SCOPES,
# )
credentials = ServiceAccountCredentials.from_json(
    cfg('google.credentials'), SCOPES,
)
client = gspread.authorize(credentials)
sheets = client.open_by_key(cfg('google_sheet')).worksheets()
