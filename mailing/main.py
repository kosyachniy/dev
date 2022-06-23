from libdev.cfg import cfg
from pysendpulse.pysendpulse import PySendPulse


SENDPULSE_ID = cfg('sendpulse.id')
SENDPULSE_SECRET = cfg('sendpulse.secret')
TOKEN_STORAGE = 'memcached'
MEMCACHED_HOST = '127.0.0.1:11211'

ADDRESSBOOK = 152713
MAIL = 'polozhev@mail.ru'


SPApiProxy = PySendPulse(SENDPULSE_ID, SENDPULSE_SECRET, TOKEN_STORAGE, memcached_host=MEMCACHED_HOST)


# # All methods
# print(*dir(SPApiProxy), sep="\n")

# # Get balance
# print(SPApiProxy.get_balance('RUR'))

# Get Mailing Lists list example
res = SPApiProxy.get_list_of_addressbooks()
print(*[f"{book['id']}\t | {book['name']}" for book in res], sep="\n")

res = SPApiProxy.get_email_info_from_all_addressbooks(MAIL)
process_variables = lambda variables: ", ".join([
    f"{variable['name']}={variable['value']}"
    for variable in variables
])
print('-' * 100)
print(*[(
    f"{address['book_id']}"
    f"\t | {address['status_explain']}"
    f"\t | {process_variables(address['variables'])}"
) for address in res], sep="\n")

# # Add emails with variables to addressbook
# res = SPApiProxy.add_emails_to_addressbook(ADDRESSBOOK, [{
#     'email': 'polozhev@mail.ru',
#     'variables': {
#         'name': 'Test 1',
#     },
# }, {
#     'email': 'alexey@tensy.io',
#     'variables': {
#         'name': 'Test 2',
#         'id': 0,
#     },
# }])
# print(res['result'])

# # Create new email campaign
# res = SPApiProxy.add_campaign(
#     from_email='info@tensy.io',
#     from_name='Tensy',
#     subject='Test campaign from REST API',
#     body=b"<h1>Hello, John!</h1><p>This is the test task from https://sendpulse.com/api REST API!</p>",
#     addressbook_id=161621,
#     campaign_name='AutoCheck',
#     # attachments={'attach1.txt': '12345\n', 'attach2.txt': '54321\n'},
# )
# print(res)

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
