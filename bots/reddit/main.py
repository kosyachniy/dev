import shutil

import requests
from libdev.cfg import cfg
import praw
from praw.models import InlineImage


CHANNEL = 'retestme'
TITLE = 'Title by Bot'
DATA = '''
# Data by Bot
\n\n
{image1}
\n\n
https://github.com/kosyachniy/dev/tree/master/bots/reddit
'''
IMAGE = 'https://tensy.s3.eu-central-1.amazonaws.com/local/R2U3Tf55tGdZYk7xNk3L8KMUnBrgFXWz.png'
CAPTION = 'Caption by Bot'


def get_image(url):
    image = f"data/{url.split('/')[-1]}"

    res = requests.get(url, stream = True)
    if res.status_code != 200:
        return None

    with open(image, 'wb') as file:
        shutil.copyfileobj(res.raw, file)
    return image

def get_inline_image(url, caption=None):
    return InlineImage(path=get_image(url), caption=caption)


reddit = praw.Reddit(
    client_id=cfg('reddit.id'),
    client_secret=cfg('reddit.secret'),
    username=cfg('reddit.user'),
    password=cfg('reddit.pass'),
    user_agent="kosyachniy script",
)

channel = reddit.subreddit(CHANNEL)
print(reddit.user.me(), channel)

channel.submit(
    TITLE,
    inline_media={
        'image1': get_inline_image(IMAGE, CAPTION),
    },
    selftext=DATA,
    discussion_type='CHAT',
)
channel.submit_image(
    TITLE,
    image_path=get_image(IMAGE),
    discussion_type='CHAT',
)
# channel.submit_gallery(TITLE, [{
#     "image_path": image3,
#     "caption": "Image caption 3",
#     "outbound_url": "https://example.com/link3",
# }], discussion_type='CHAT')
