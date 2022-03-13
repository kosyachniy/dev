import sys, ssl, chardet, pymongo, codecs
from urllib.request import urlopen, Request

#Standart
def read(name='db.txt'):
    with codecs.open('db.txt', 'r', encoding='utf-8') as file:
        print(file.read())

def write(text,name='db.txt'):
    with open('db.txt', 'a', encoding='utf-8') as file:
        print(text, file=file)

#CSV
def read_csv(name='db', sign=','):
    with open(name+'.csv', 'r') as file:
        return [i for i in csv.reader(file, delimiter=sign, quotechar=' ')]

def write_csv(text, name='db', sign=','):
    with open(name+'.csv', 'a') as file:
        csv.writer(file, delimiter=sign, quotechar=' ', quoting=csv.QUOTE_MINIMAL).writerow(text)

#JSON
def read_json(file='db'):
    with open(name+'.json', 'r') as file:
        return loads(file.read())

def write_json(cont, name='db'):
    with open('db.json', 'w') as file:
        print(dumps(cont, ensure_ascii=False), file=file)

#MongoDB
def db(name):
    return pymongo.MongoClient('mongodb://root:asdrqwerty09@invo-shard-00-00-guyjh.mongodb.net:27017,invo-shard-00-01-guyjh.mongodb.net:27017,invo-shard-00-02-guyjh.mongodb.net:27017/INVO?ssl=true&replicaSet=INVO-shard-0&authSource=admin')[name]

def site(src):
    with urlopen(Request(src,None,{'User-Agent':''}),context=ssl._create_unverified_context()) as site:
        return site.read().decode('utf-8')
