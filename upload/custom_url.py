import requests


URL = 'https://web.kosyachniy.com/api/upload/'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6InJHN2o0cDd1OUcyNlNTVzFaQkNUamRpVTc2RDg1NDNNIiwidXNlciI6NiwibmV0d29yayI6MX0.dSL960Yg5vuC4FfPrejOnLwW6sj7bygzdJ0tSrlkwOw'


with open('web/public/user.png', 'rb') as file:
    data = file.read()

res = requests.post(
    URL,
    files={'upload': data},
    headers={'Authorization': f'Bearer {TOKEN}'},
).text

print(res)
