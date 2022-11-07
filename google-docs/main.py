import gspread
from oauth2client.service_account import ServiceAccountCredentials


credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json',
    [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive',
    ],
)
client = gspread.authorize(credentials)


def create(name, mail):
    sheet = client.create(name)
    sheet.share(mail, perm_type='user', role='writer')
    return sheet.url


print(create('Title', 'alexypoloz@gmail.com'))
