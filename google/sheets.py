from lib.docs import Sheets


SHEETS = "1lyCWXhWkIEeCINTSgosOMeLEA9EvxEEfIa5pOZIWW1Q"
SHEET = 0


# # Create a spreadsheet
# # sh = create_sheets("Test", "alexypoloz@gmail.com")
# # print(f"https://docs.google.com/spreadsheets/d/{sh}")
# sh = Sheets.create("Test", "alexypoloz@gmail.com")
# for ws in sh.get_sheets():
#     print(ws.id, ws.title)

sh = Sheets(SHEETS, SHEET)

# # Get sheets
# # sh = open_sheets(SHEETS)
# # for ws in sh:
# #     print(ws.id, ws.title)
# for ws in sh.get_sheets():
#     print(ws.id, ws.title)

# # Print data
# data = [
#     ("Name", "Value"),
#     ("Alex", 123),
#     ("Alice", 456),
# ]
# # ws = open_sheet(SHEETS, SHEET)
# # replace(ws, data)
# sh.replace(data)

# Print structured data
data = [
    {"Name": "Alex", "Data": 24, "City": "Los Angeles"},
    {"Name": "Alice", "Data": 26, "City": "Miami"},
    {"Name": "Bred", "Data": 30, "City": "Tokyo"},
]
sh.replace(data)

# Format
sh.freeze()
sh.align("left", cols=["A:C"])
sh.align("center", cols=["B"], rows=[1, 3])
sh.background((0.5, 0.5, 0.5, 0.5), cols=["1:1"])
