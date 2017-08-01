import re

text='qweblabla: 123'
print(re.sub(r'^qwe\w+: ', '', text))