from random import random
from time import time
import hmac, hashlib
from base64 import b64decode

def hash_hmac(algo, data, key):
    return hmac.new(key.encode(), data.encode(), algo).digest() #hexdigest

nonce=hashlib.md5(str(random()).encode('utf-8')).hexdigest()
times=round(time())
url='https://api.twitter.com/oauth/request_token?oauth_callback=http%3A%2F%2Fzodzu.com%2Fauth.php&oauth_consumer_key=mcactbAgFofues75dpMkFKLsg&oauth_nonce='+nonce+'&oauth_signature_method=HMAC-SHA1&oauth_timestamp='+str(times)+'&oauth_version=1.0'
signature=b64decode(hash_hmac('sha1', 'GET&https%3A%2F%2Fapi.twitter.com2Foauth2Frequest_token&'+url, '2H1KU0cR3kcYXgHgfFLnLwzqYdF7Ie5QBsqIVYA7zzN6jEN7QU&'))
url='https://api.twitter.com/oauth/request_token?oauth_callback=http%3A%2F%2Fzodzu.com%2Fauth.php&oauth_consumer_key=mcactbAgFofues75dpMkFKLsg&oauth_nonce='+nonce+'&oauth_signature='+signature+'&oauth_signature_method=HMAC-SHA1&oauth_timestamp='+str(times)+'&oauth_version=1.0'
print(url)