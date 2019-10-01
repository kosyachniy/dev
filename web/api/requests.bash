curl -X GET http://127.0.0.1:5000/?name=123

curl -X POST -H "Content-Type: application/json" -d '{"123": 456}' http://127.0.0.1:5000/