import hashlib as hasher
import os, json

class Block:
	def __init__(self, index, timestamp, data, previous_hash):
		self.index = index
		self.timestamp = timestamp
		self.data = data
		self.previous_hash = previous_hash
		self.hash = self.hash_block()
	
	def hash_block(self):
		sha = hasher.sha256()
		cont = (str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).encode('utf-8')
		#print(cont)
		sha.update(cont)
		return sha.hexdigest()

import datetime as date

#Вручную создаем блок с нулевым индексом и произвольным хэшем предыдущего блока
def create_genesis_block():
	return Block(0, date.datetime.now(), 'Genesis Block', '0')

def next_block(last_block, data):
	this_index = last_block.index + 1
	this_timestamp = date.datetime.now()
	this_hash = last_block.hash
	return Block(this_index, this_timestamp, data, this_hash)

style = lambda x: {'index': x.index, 'time': str(x.timestamp), 'data': x.data, 'previous_hash': x.previous_hash, 'hash': x.hash}

#Первый блок
blockchain = [create_genesis_block()]
previous_block = blockchain[0]

#Добавление нового блока
while True:
	try:
		data = input()
		block_to_add = next_block(previous_block, data)
		blockchain.append(block_to_add)
		previous_block = block_to_add

		print('Блок #{} был добавлен в блокчейн!'.format(block_to_add.index))
		print('Хэш: {}\n'.format(block_to_add.hash))
	except:
		break

with open('blockchain', 'w') as file:
	print(json.dumps([style(i) for i in blockchain]) ,file=file)
#print('\n\n***** Начало цепочки блоков *****\n', *[i.data for i in blockchain], '\n***** Конец цепочки блоков *****\n\n', sep='\n'+'-'*100+'\n')