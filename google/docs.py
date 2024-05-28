import json

from google.oauth2.service_account import Credentials
from libdev.cfg import cfg
import pygsheets
import pandas as pd


credentials = Credentials.from_service_account_info(cfg('google.credentials'), scopes=[
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
])
gc = pygsheets.authorize(custom_credentials=credentials)

sh = gc.create('Test Sheet')

print(sh)
print(dir(sh))
