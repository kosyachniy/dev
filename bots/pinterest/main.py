# # import json

# from py3pin.Pinterest import Pinterest
# from libdev.cfg import cfg


# USER = 'teenvogue'
# BOARD = '259027484757043488'


# pinterest = Pinterest(
#     email=cfg('pinterest.mail'),
#     password=cfg('pinterest.pass'),
#     username=cfg('pinterest.user'),
#     cred_root=cfg('pinterest.root'),
# )
# pinterest.login()

# print(pinterest.get_user_overview())

# # # boards = pinterest.boards(username=USER)
# # # print([(
# # #     board['id'],
# # #     board['name'],
# # # ) for board in boards])

# pins = pinterest.board_feed(board_id="1063553336940651725")
# with open('pins.json', 'w') as file:
#     print(json.dumps(pins, indent='\t'), file=file)

# # # for pin in pins:
# # #     print(pin['images']['orig']['url'])

# # # print (pinterest.boards(username='chilleco'))



import pinterest

# Generate OAuth2 authorization link
# link = pinterest.oauth2.authorization_url(app_id, redirect_uri)

# Initialize API by passing OAuth2 token
api = pinterest.Pinterest(token="pina_...")

# Fetch authenticated user's data
print(api.me())


pin = pinterest.pin(
    board_id="1063553336940651725",
    image_url="https://m.media-amazon.com/images/I/71eTw6M1DUL._SX550_.jpg",
    title="Test",
    description="Test",
    # description=(
    #     # f"#### 🔥 View the product: https://styletyx.com/product/the-north-face-beanies-the-north-face-oh-mega-city-pom-beanie-1"
    #     f"\n**Price with discount: 24$** ~~45$~~ (-44%)"
    # ),
    link="https://styletyx.com/product/the-north-face-beanies-the-north-face-oh-mega-city-pom-beanie-1",
)
print(dir(pin))
with open('res.html', 'w') as file:
    print(pin.text, file=file)


# pin_response = pinterest.upload_pin(
#     board_id='1063553336940651725',
#     image_file='/Users/kosyachniy/Desktop/proj/dev/bots/pinterest/1.jpg',
#     description='test',
#     title='test',
#     # link='link',
# )
# print(pin_response.content)
# # print(json.loads(pin_response.content))



# import pinterest

# Generate OAuth2 authorization link
# link = pinterest.oauth2.authorization_url(app_id, redirect_uri)

# print(link)

# https://api.pinterest.com/oauth/?response_type=code&client_id=&redirect_uri=https%3A%2F%2Fweb.kosyachniy.com%2Fpinterest&state=%5B%27C%27%2C+%27V%27%2C+%27G%27%2C+%27S%27%2C+%27X%27%2C+%27c%27%2C+%27G%27%2C+%27i%27%5D&scope=read_public%2Cwrite_public%2Cread_relationships%2Cwrite_relationships

# api = pinterest.Pinterest(token=access_token)


# Fetch authenticated user's data
# print(api.boards())

# # Initialize API by passing OAuth2 token
# api = pinterest.Pinterest(token="")

# # Fetch authenticated user's data
# api.me()

# # Fetch authenticated user's boards
# api.boards()

# # Create board
# api.board().create("Halloween", description="Fun Costumes")

# # Fetch board
# api.board("695665542379607495").fetch()
# api.board("username/halloween").fetch()

# # Fetch pins on board
# api.board("username/halloween").pins()

# # Edit board
# api.board("username/halloween").edit(new_name="Costumes", new_description="Halloween Costume Ideas")

# # Delete board
# api.board("username/halloween").delete()

# # Fetch board suggestions
# api.suggest_boards(pin=162129655315312286)

# # Fetch authenticated user's pins
# api.pins()

# # Create a pin
# api.pin().create(board, note, link, image_url=image_url)

# # Fetch a pin
# api.pin(162129655315312286).fetch()

# # Edit a pin
# api.pin(162129655315312286).edit(board, note, link)

# # Delete a pin
# api.pin(162129655315312286).delete()

# # Search boards (Optional cursor)
# api.search_boards(query, cursor=None)

# # Search pins (Optional cursor)
# api.search_pins(query, cursor=None)

# # Follow a board
# api.follow_board(board)

# # Follow a user
# api.follow_user(username)

# # Return the users who follow the authenticated user
# api.followers(cursor=None)

# # Return the boards that the authenticated user follows
# api.following_boards(cursor=None)

# # Return the topics the authenticated user follows
# api.following_interests(cursor=None)

# # Return the users the authenticated user follows
# api.following_users(cursor=None)

# # Unfollow board
# api.unfollow_board(board)

# # Make authenticated user unfollow user
# api.unfollow_user(username)

# # Fetch another user's info
# api.user(username)

# # Fetch board sections
# api.board("695665542379586148").sections()

# # Create board section
# api.board("695665542379586148").section("Section Title").create()

# # Delete board section
# api.board("695665542379586148").section("4989415010584246390").delete()

# # Fetch pins in board section
# api.board("695665542379586148").section("4989343507360527350").pins()
