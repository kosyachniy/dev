from lib.reddit import reddit, post


post(
    channel='retestme',
    title='Title by Bot',
    data='''
        # Data by Bot
        \n\n
        https://github.com/kosyachniy/dev/tree/master/bots/reddit
    ''',
    image='https://tensy.s3.eu-central-1.amazonaws.com/local/R2U3Tf55tGdZYk7xNk3L8KMUnBrgFXWz.png',
    flair='e60b685c-904c-11ed-b6c6-de305ea9767f',
)

for flair in reddit.subreddit("retestme").flair():
    print(flair)
for template in reddit.subreddit("retestme").flair.templates:
    print(template)

for s in reddit.subreddit("OUTFITS").new(limit=100):
    print(s, s.author_flair_text, s.link_flair_text, sep=" | ")
    print(s.flair.choices())

user = reddit.redditor('p__yos')
submissions = user.submissions.new(limit=None)
for link in submissions:
    print(link, link.link_flair_text)
    print(link.flair.choices())
    break
