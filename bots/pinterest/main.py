import json

from py3pin.Pinterest import Pinterest
from libdev.cfg import cfg


USER = 'teenvogue'
BOARD = '259027484757043488'


pinterest = Pinterest(
    email=cfg('pinterest.mail'),
    password=cfg('pinterest.pass'),
    username=cfg('pinterest.user'),
    cred_root=cfg('pinterest.root'),
)
# pinterest.login()

# print(pinterest.get_user_overview())

# boards = pinterest.boards(username=USER)
# print([(
#     board['id'],
#     board['name'],
# ) for board in boards])

pins = pinterest.board_feed(board_id=BOARD)
with open('pins.json', 'w') as file:
    print(json.dumps(pins, indent='\t'), file=file)

for pin in pins:
    print(pin['images']['orig']['url'])
