import json


with open('categories.json', 'r') as file:
	CATEGORIES = json.loads(file.read())


if __name__ == '__main__':
	x = input().strip()

	if x in CATEGORIES:
		print(CATEGORIES[x])