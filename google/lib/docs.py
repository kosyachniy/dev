"""
Google Documents functionality
"""

from google.oauth2.service_account import Credentials
from libdev.cfg import cfg
import pygsheets
from pygsheets.custom_types import VerticalAlignment, HorizontalAlignment

# from pygsheets.utils import format_addr
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
    def __init__(self, key, sheet=None):
        self.id = key
        self.sheets = self._open(key)
        self.sheet = self.open_sheet(sheet) if sheet is not None else None

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

    def open_sheet(self, sheet=None):
        """Open a worksheet"""
        if sheet is None:
            return self.sheet
        for ws in self.get_sheets():
            if ws.id == sheet:
                return ws
        return None

    def _get_sheet(self, sheet=None):
        if sheet is not None:
            return self.open_sheet(sheet)
        return self.sheet

    def replace(self, data, sheet=None):
        """Replace data in a worksheet"""
        ws = self._get_sheet(sheet)

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

    def freeze(self, rows=1, cols=1, sheet=None):
        ws = self._get_sheet(sheet)
        ws.frozen_rows = rows
        ws.frozen_cols = cols

    @staticmethod
    def _get_col_range(col):
        if ":" in col:
            start, end = col.split(":")
        else:
            start, end = col, col
        return start, end

    @classmethod
    def _get_cols_range(cls, cols=None):
        rngs = []
        for col in cols or []:
            rngs.append(cls._get_col_range(col))
        return rngs

    @staticmethod
    def _get_row_range(row):
        row = str(row)
        if ":" in row:
            start, end = row.split(":")
        else:
            start, end = row, row
        return start, end

    @classmethod
    def _get_rows_range(cls, rows=None):
        rngs = []
        for row in rows or []:
            rngs.append(cls._get_row_range(row))
        return rngs

    def _get_range(self, cols=None, rows=None, sheet=None):
        ws = self._get_sheet(sheet)
        rngs = self._get_cols_range(cols) + self._get_rows_range(rows)

        ranges = []
        for rng in rngs:
            ranges.append(ws.get_values(rng[0], rng[1], returnas="range"))

        return ranges

    def align(self, align="left", cols=None, rows=None, sheet=None):
        rngs = self._get_range(cols, rows, sheet)

        for rng in rngs:
            model = pygsheets.Cell("A1")
            model.set_horizontal_alignment(getattr(HorizontalAlignment, align.upper()))
            model.set_vertical_alignment(VerticalAlignment.TOP)

            rng.apply_format(model)

    def background(self, color=(1.0, 1.0, 1.0), cols=None, rows=None, sheet=None):
        rngs = self._get_range(cols, rows, sheet)

        for rng in rngs:
            model = pygsheets.Cell("A1")
            model.color = color
            # model.format = (pygsheets.FormatType.PERCENT, "")

            rng.apply_format(model)

    @staticmethod
    def _get_col_idx(col):
        """
        Convert a column letter (e.g., 'A', 'Z', 'AA') to a column index (1-based).
        """
        index = 0
        for char in col.upper():
            index = index * 26 + (ord(char) - ord("A") + 1)
        return index

    def width(self, size=None, cols=None, sheet=None):
        ws = self._get_sheet(sheet)
        rngs = self._get_cols_range(cols)

        for rng in rngs:
            ws.adjust_column_width(
                self._get_col_idx(rng[0]), self._get_col_idx(rng[1]), size
            )
