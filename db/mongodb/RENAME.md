# Переименовать БД

1. Входим в БД
```
use db1
```

2. Копируем коллекции в БД с новым названием
```
db.getCollectionNames().forEach(function(collectionName) {
   var documents = db[collectionName].find();
   while(documents.hasNext()) {
      var doc = documents.next();
      db.getSiblingDB("db2")[collectionName].insert(doc);
   }
})
```

3. Удаляем старую БД
```
db.dropDatabase()
```
