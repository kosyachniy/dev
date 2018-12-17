import re


def replace(cont):
	return re.sub(r'^qwe\w+: ', '', cont)


if __name__ == '__main__':
	print(replace('qweblabla: 123'))