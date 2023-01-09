"""
Functionality for working with Reddit
"""

import shutil

import requests
from libdev.cfg import cfg
import praw
from praw.models import InlineImage


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


def post(channel, title=None, data=None, image=None):
    channel = reddit.subreddit(channel)

    if image:
        post = channel.submit_image(
            title,
            image_path=get_image(image),
            # discussion_type='CHAT',
        )
        # channel.submit_gallery(title, [{
        #     "image_path": image3,
        #     "caption": "Image caption 3",
        #     "outbound_url": "https://example.com/link3",
        # }])
        post.reply(data)
        return post

    return channel.submit(
        title,
        # inline_media={
        #     'image1': get_inline_image(IMAGE, CAPTION),
        # },
        selftext=data,
        # discussion_type='CHAT',
    )


# import os
# os.remove("data/")
