from func.db_mongo import *

el = {
	'param 1': 'text',
	'param 2': 123,
	'param 3': {
		'la': [1, 4, 6],
		're': False,
	}
}
db['test'].insert_one(el)