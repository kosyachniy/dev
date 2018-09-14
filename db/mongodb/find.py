from func.db_mongo import *

# Одна коллекция
x = db['test'].find_one({'id': 1})
print(x)

# Все коллекции
for i in db['test'].find():
	print(i)

# Все коллекция с строго больше указанным параметром
for i in db['test'].find({'id': {'$gt': 5}}):
	print(i)
# $eq $ne $gt $gte $lt $lte $exsist $type $regex

# Все коллекции, у которых параметр входит в список
for i in db['test'].find({'id': {'$in': (5, 8)}}):
	print(i)
# $in $nin 

# Условие для вложенного документа
for i in db['test'].find({'param 3.re': False}):
	print(i)

# Условия для массивов
for i in db['test'].find({'param 3.la': {'$all': (1, 4)}}):
	print(i)
# $all $size

# Условия для вложенных в массив документов (хотя бы одно совпадение внутри)
for i in db['test'].find({'list': {'$elemMatch': {'id': {'$gt': 5}, 'lang': 'ru'}}}):
	print('!!!', i)

# Выборка полей
for i in db['test'].find({}, {'id'}):
	print(i)
# {'id': True) {'cont': False}