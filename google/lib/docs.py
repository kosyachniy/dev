"""
Google Documents functionality
"""

from google.oauth2.service_account import Credentials
from libdev.cfg import cfg
import pygsheets
import pandas as pd


credentials = Credentials.from_service_account_info(
    cfg("google.credentials"),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
gc = pygsheets.authorize(custom_credentials=credentials)


class Sheets:
    def __init__(self, key):
        self.id = key
        self.sheets = self._open(key)

    @classmethod
    def create(cls, title, mail=None):
        """Create a spreadsheet"""
        sh = gc.create(title)
        if mail:
            sh.share(mail, role="writer")
        sheets = cls(sh.id)
        return sheets

    @classmethod
    def create_sheets(cls, title, mail):
        """Create a spreadsheet"""
        return cls.create(title, mail).id

    @classmethod
    def _open(cls, key):
        """Open a spreadsheet"""
        return gc.open_by_key(key)

    @classmethod
    def open_sheets(cls, key):
        """Open a spreadsheet"""
        return cls._open(key).worksheets()

    def get_sheets(self):
        """Get sheets"""
        return self.sheets.worksheets()

    def open_sheet(self, sheet):
        """Open a worksheet"""
        for ws in self.get_sheets():
            if ws.id == sheet:
                return ws
        return None

    def replace(self, sheet, data):
        """Replace data in a worksheet"""
        ws = self.open_sheet(sheet)
        ws.clear()

        if not data:
            return

        detected_type = "array"
        for row in data:
            if isinstance(row, dict):
                detected_type = "object"
                break
            if isinstance(row, (list, tuple, set)):
                detected_type = "array"
                break

        if detected_type == "object":
            ws.set_dataframe(pd.DataFrame(data), (1, 1))
        else:
            ws.update_values("A1", [[cell for cell in row] for row in data])
