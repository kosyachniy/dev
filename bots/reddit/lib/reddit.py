"""
Functionality for working with Reddit
"""

import shutil

import requests
from libdev.cfg import cfg
import praw
from praw.models import InlineImage


DATA_PATH = 'data/'


def get_image(url):
    image = f"{DATA_PATH}{url.split('/')[-1].split('?')[0]}"

    try:
        res = requests.get(url, stream=True, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    except requests.exceptions.ReadTimeout:
        return None
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


def post(channel, title=None, data=None, image=None, flair=None):
    channel = reddit.subreddit(channel)

    if image:
        image = get_image(image)
        if image is None:
            return None

        post = channel.submit_image(
            title,
            image_path=image,
            # discussion_type='CHAT',
            flair_id=flair,
        )
        # channel.submit_gallery(title, [{
        #     "image_path": image3,
        #     "caption": "Image caption 3",
        #     "outbound_url": "https://example.com/link3",
        # }])

        if data:
            post.reply(data)

        return post

    return channel.submit(
        title,
        # inline_media={
        #     'image1': get_inline_image(IMAGE, CAPTION),
        # },
        selftext=data,
        # discussion_type='CHAT',
        flair_id=flair,
    )


# import os
# os.remove("data/")
