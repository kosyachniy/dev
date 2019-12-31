from func.db_mongo import db

# Одна коллекция
x = db['test'].find_one({'id': 1})
print(x)

# Все коллекции
for i in db['test'].find():
	print(i)

# Все коллекция с строго больше указанным параметром
for i in db['test'].find({'id': {'$gt': 5}}):
	print(i)
# $eq $ne $gt $gte $lt $lte $exists $type $regex

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
	print(i)

# Выборка полей
for i in db['test'].find({}, {'id'}):
	print(i)
# {'id': True) {'cont': False}

# Выборка вложенных документов
db_condition = {'steps.ladder': 10}
db_filter = {'steps': {'$elemMatch': {'ladder': 10}}, 'steps.ladder': True}
for i in db['users'].find(db_condition, db_filter):
	print(i)

# Логические условия
db_condition = {'$or': [{'teacher': i['user']}, {'student': i['user']}]}
space = db['study'].find_one(db_condition)
print(space)
# $and $nor

# Вывод определённых вложенных элементов списка в коллекции
db_condition = {
	'steps': {
		'$elemMatch': {
			'step': 1,
			'price': {'$exists': True},
			}
		},
	}
db_filter = {
	'_id': False,
	'user': True,
	'steps': {
		'$elemMatch': {
			'step': 1,
			'price': {'$exists': True},
		}
	},
	'steps.price': True,
}
teacher = db['online'].find_one(db_condition, db_filter)
print(teacher)