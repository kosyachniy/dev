# # Create board
# from pinterest.organic.boards import Board

# board_create=Board.create(
#   name="Summer Recipes",
#   description="My favorite summer recipes",
#   privacy="PUBLIC"
# )
# print("Board Id: %s, Board name:%s"%(board_create.id, board_create.name))

# Create pin
from pinterest.organic.pins import Pin

BOARD_ID="1063553336940651725"

pin_create = Pin.create(
    board_id=BOARD_ID,
    title="Platye",
    description="Krytoe platye",
    media_source={
        "source_type": "image_url",
        "content_type": "image/jpeg",
        "data": "string",
        'url': 'https://slimages.macysassets.com/is/image/MCY/products/6/optimized/23504216_fpx.tif?op_sharpen=1&wid=560&fit=fit,1&$filtersm$',
    },
)
print("Pin Id: %s, Pin Title:%s" %(pin_create.id, pin_create.title))
