import praw
from libdev.cfg import cfg


reddit = praw.Reddit(
    client_id=cfg('reddit.id'),
    client_secret=cfg('reddit.secret'),
    username=cfg('reddit.user'),
    password=cfg('reddit.pass'),
    user_agent="kosyachniy script",
)

print(reddit.user.me(), reddit.read_only)
