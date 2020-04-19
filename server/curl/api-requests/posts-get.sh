# Все посты

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.get", "token": "test"}' http://127.0.0.1:5000/

# Несколько постов

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.get", "params": {"id": [1, 2]}, "token": "test"}' http://127.0.0.1:5000/

# Один пост

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.get", "params": {"id": 1}, "token": "test"}' http://127.0.0.1:5000/