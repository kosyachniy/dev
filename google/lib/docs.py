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
        return cls.create(title, mail).sheets.url

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
        """Get the specified sheet, or the default sheet if no sheet is specified"""
        if sheet is not None:
            return self.open_sheet(sheet)
        return self.sheet

    def insert(self, data, cell="A1", sheet=None):
        """Insert data in a worksheet"""

        if not data:
            return

        ws = self._get_sheet(sheet)

        detected_type = "array"
        for row in data:
            if isinstance(row, dict):
                detected_type = "object"
                break
            if isinstance(row, (list, tuple, set)):
                detected_type = "array"
                break

        if detected_type == "object":
            ws.set_dataframe(pd.DataFrame(data), cell)
        else:
            ws.update_values(cell, [[col for col in row] for row in data])

    def replace(self, data, sheet=None):
        """Replace data in a worksheet"""
        ws = self._get_sheet(sheet)
        ws.clear()
        self.insert(data, sheet=sheet)

    def freeze(self, rows=1, cols=1, sheet=None):
        """Freeze rows and columns in a worksheet"""
        ws = self._get_sheet(sheet)
        ws.frozen_rows = rows
        ws.frozen_cols = cols

    @staticmethod
    def _get_col_range(col):
        """Get the start and end of a column range"""
        if ":" in col:
            start, end = col.split(":")
        else:
            start, end = col, col
        return start, end

    @classmethod
    def _get_cols_range(cls, cols=None):
        """Get the ranges for multiple columns"""
        rngs = []
        for col in cols or []:
            rngs.append(cls._get_col_range(col))
        return rngs

    @staticmethod
    def _get_row_range(row):
        """Get the start and end of a row range"""
        row = str(row)
        if ":" in row:
            start, end = row.split(":")
        else:
            start, end = row, row
        return start, end

    @classmethod
    def _get_rows_range(cls, rows=None):
        """Get the ranges for multiple rows"""
        rngs = []
        for row in rows or []:
            rngs.append(cls._get_row_range(row))
        return rngs

    def _get_range(self, cols=None, rows=None, sheet=None):
        """Get the range of cells for specified columns and rows"""

        ws = self._get_sheet(sheet)
        rngs = self._get_cols_range(cols) + self._get_rows_range(rows)

        ranges = []
        for rng in rngs:
            ranges.append(ws.get_values(rng[0], rng[1], returnas="range"))

        return ranges

    @classmethod
    def _get_cell(cls, cols=None, rows=None):
        for col in cols or []:
            start, _ = cls._get_col_range(col)
            if start:
                return start
        for row in rows or []:
            start, _ = cls._get_row_range(row)
            if start:
                return start
        return "A1"

    def _get_base(self, cols=None, rows=None, sheet=None):
        ws = self._get_sheet(sheet)
        return ws.cell(self._get_cell(cols, rows))

    def align(self, align="left", cols=None, rows=None, sheet=None):
        """Align the content of specified columns and rows in a worksheet"""

        rngs = self._get_range(cols, rows, sheet)

        for rng in rngs:
            model = self._get_base(cols, rows, sheet)
            model.set_horizontal_alignment(getattr(HorizontalAlignment, align.upper()))
            model.set_vertical_alignment(VerticalAlignment.TOP)

            rng.apply_format(model)

    def background(self, color=(1.0, 1.0, 1.0), cols=None, rows=None, sheet=None):
        """Set the background color of specified columns and rows in a worksheet"""

        rngs = self._get_range(cols, rows, sheet)

        for rng in rngs:
            model = self._get_base(cols, rows, sheet)
            model.color = color
            # model.format = (pygsheets.FormatType.PERCENT, "")

            rng.apply_format(model)

    def get_background(self, cell, sheet=None):
        ws = self._get_sheet(sheet)
        return ws.cell(cell).color

    def format(self, format, value=True, cols=None, rows=None, sheet=None):
        rngs = self._get_range(cols, rows, sheet)

        for rng in rngs:
            model = self._get_base(cols, rows, sheet)
            model.set_text_format(format, value)
            rng.apply_format(model)

    def color(self, color=(0, 0, 0), cols=None, rows=None, sheet=None):
        if len(color) == 3:
            color = (*color, 1.0)
        return self.format("foregroundColor", color, cols, rows, sheet)

    def get_color(self, cell, sheet=None):
        ws = self._get_sheet(sheet)
        styles = ws.cell(cell).text_format

        style = styles.get("foregroundColorStyle", {}).get("rgbColor", {})
        if style:
            color = (
                style.get("red", 0),
                style.get("green", 0),
                style.get("blue", 0),
                style.get("alpha", 0),
            )
        else:
            color = styles["foregroundColor"]

        return color

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
        """Set the width of specified columns in a worksheet"""

        ws = self._get_sheet(sheet)
        rngs = self._get_cols_range(cols)

        for rng in rngs:
            ws.adjust_column_width(
                self._get_col_idx(rng[0]), self._get_col_idx(rng[1]), size
            )

    def merge(self, cells, sheet=None):
        """Merge specified cells in a worksheet"""

        if isinstance(cells, str):
            cells = [cells]

        ws = self._get_sheet(sheet)
        rngs = self._get_cols_range(cells)

        for rng in rngs:
            ws.merge_cells(rng[0], rng[1])

    # TODO: рамка, тип данных, вставка ссылки, формула, создать вкладку, переименовать вкладку
