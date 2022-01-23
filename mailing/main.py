from libdev.cfg import cfg
from pysendpulse.pysendpulse import PySendPulse


REST_API_ID = cfg('sendpulse.id')
REST_API_SECRET = cfg('sendpulse.secret')
TOKEN_STORAGE = 'memcached'
MEMCACHED_HOST = '127.0.0.1:11211'
SPApiProxy = PySendPulse(REST_API_ID, REST_API_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)

# Get balance
print(SPApiProxy.get_balance('RUR'))

# Create new email campaign
res = SPApiProxy.add_campaign(
    from_email='info@tensy.io',
    from_name='Tensy',
    subject='Test campaign from REST API',
    body=b"<h1>Hello, John!</h1><p>This is the test task from https://sendpulse.com/api REST API!</p>",
    addressbook_id=161621,
    campaign_name='AutoCheck',
    # attachments={'attach1.txt': '12345\n', 'attach2.txt': '54321\n'},
)
print(res)

# # Send mail using SMTP
# res = SPApiProxy.smtp_send_mail({
#     'subject': 'This is the test task from REST API',
#     'html': '<h1>Hello, John!</h1><p>This is the test task from https://sendpulse.com/api REST API!</p>',
#     'text': 'Hello, John!\nThis is the test task from https://sendpulse.com/api REST API!',
#     'from': {'name': 'Tensy', 'email': 'info@tensy.io'},
#     'to': [
#         {'name': 'Alexey Poloz', 'email': 'upolozal@gmail.com'},
#     ],
#     # 'bcc': [
#     #     {'name': 'Richard Roe', 'email': 'richard.roe@domain.com'},
#     # ],
# })
# print(res)
