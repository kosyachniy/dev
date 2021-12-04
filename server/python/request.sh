# cURL - FastAPI - Flask

curl -X POST -d '123' http://127.0.0.1:8000/
# {"headers":{"host":"127.0.0.1:8000","user-agent":"curl/7.64.1","accept":"*/*","content-length":"3","content-type":"application/x-www-form-urlencoded"},"body":"123","json":123,"params":{}}
# {"form":{"123":""},"headers":"Host: 127.0.0.1:5000\r\nUser-Agent: curl/7.64.1\r\nAccept: */*\r\nContent-Length: 3\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n","json":null,"values":{}}
# {
#         "headers": {
#                 "host": "127.0.0.1:8000",
#                 "user-agent": "curl/7.64.1",
#                 "accept": "*/*",
#                 "content-length": "3",
#                 "content-type": "application/x-www-form-urlencoded"
#         },
#         "body": "b'123'",
#         "json": 123,
#         "client": "127.0.0.1:54003",
#         "path_params": {},
#         "query_params": {}
# }

curl -X POST -H "Content-Type: application/json" -d '{"key": "value"}' http://127.0.0.1:8000/
# {"headers":{"host":"127.0.0.1:8000","user-agent":"curl/7.64.1","accept":"*/*","content-type":"application/json","content-length":"16"},"body":"{\"key\": \"value\"}","json":{"key":"value"},"params":{}}
# {"form":{},"headers":"Host: 127.0.0.1:5000\r\nUser-Agent: curl/7.64.1\r\nAccept: */*\r\nContent-Type: application/json\r\nContent-Length: 16\r\n\r\n","json":{"key":"value"},"values":{}}
# {
#         "headers": {
#                 "host": "127.0.0.1:8000",
#                 "user-agent": "curl/7.64.1",
#                 "accept": "*/*",
#                 "content-type": "application/json",
#                 "content-length": "16"
#         },
#         "body": "b'{\"key\": \"value\"}'",
#         "json": {
#                 "key": "value"
#         },
#         "client": "127.0.0.1:53825",
#         "path_params": {},
#         "query_params": {}
# }

curl -X GET -d key=value http://127.0.0.1:8000/
# {"headers":{"host":"127.0.0.1:8000","user-agent":"curl/7.64.1","accept":"*/*","content-length":"9","content-type":"application/x-www-form-urlencoded"},"body":"key=value","json":null,"client":["127.0.0.1",60894]}
# {"form":{"key":"value"},"headers":"Host: 127.0.0.1:5000\r\nUser-Agent: curl/7.64.1\r\nAccept: */*\r\nContent-Length: 9\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n","json":null,"values":{}}
# {
#         "headers": {
#                 "host": "127.0.0.1:8000",
#                 "user-agent": "curl/7.64.1",
#                 "accept": "*/*",
#                 "content-length": "9",
#                 "content-type": "application/x-www-form-urlencoded"
#         },
#         "body": "b'key=value'",
#         "json": null,
#         "client": "127.0.0.1:54209",
#         "path_params": {},
#         "query_params": {}
# }

request.get('http://127.0.0.1:8000', headers={'a':'b'}, params='c', data='d', json={'e': 'f'})
# {"headers":{"host":"127.0.0.1:8000","user-agent":"python-requests/2.26.0","accept-encoding":"gzip, deflate","accept":"*/*","connection":"keep-alive","a":"b","content-length":"1"},"body":"d","json":null,"client":["127.0.0.1",64442],"path_params":{},"query_params":{"c":""}}
# {
#         "headers": {
#                 "host": "127.0.0.1:8000",
#                 "user-agent": "python-requests/2.26.0",
#                 "accept-encoding": "gzip, deflate",
#                 "accept": "*/*",
#                 "connection": "keep-alive",
#                 "a": "b",
#                 "content-length": "1"
#         },
#         "body": "b'd'",
#         "json": null,
#         "client": "127.0.0.1:54358",
#         "path_params": {},
#         "query_params": {
#                 "c": ""
#         }
# }

request.get('http://127.0.0.1:8000', headers={'a':'b'}, params='c', data={'e': 'f'})
# {"headers":{"host":"127.0.0.1:8000","user-agent":"python-requests/2.26.0","accept-encoding":"gzip, deflate","accept":"*/*","connection":"keep-alive","a":"b","content-length":"3","content-type":"application/x-www-form-urlencoded"},"body":"e=f","json":null,"client":["127.0.0.1",64650],"path_params":{},"query_params":{"c":""}}
# {
#         "headers": {
#                 "host": "127.0.0.1:8000",
#                 "user-agent": "python-requests/2.26.0",
#                 "accept-encoding": "gzip, deflate",
#                 "accept": "*/*",
#                 "connection": "keep-alive",
#                 "a": "b",
#                 "content-length": "3",
#                 "content-type": "application/x-www-form-urlencoded"
#         },
#         "body": "b'e=f'",
#         "json": null,
#         "client": "127.0.0.1:54552",
#         "path_params": {},
#         "query_params": {
#                 "c": ""
#         }
# }

request.get('http://127.0.0.1:8000', headers={'a':'b'}, params='c', json={'e': 'f'})
# {"headers":{"host":"127.0.0.1:8000","user-agent":"python-requests/2.26.0","accept-encoding":"gzip, deflate","accept":"*/*","connection":"keep-alive","a":"b","content-length":"10","content-type":"application/json"},"body":"{\\"e\\": \\"f\\"}","json":{"e":"f"},"client":["127.0.0.1",64751],"path_params":{},"query_params":{"c":""}}
# {
#         "headers": {
#                 "host": "127.0.0.1:8000",
#                 "user-agent": "python-requests/2.26.0",
#                 "accept-encoding": "gzip, deflate",
#                 "accept": "*/*",
#                 "connection": "keep-alive",
#                 "a": "b",
#                 "content-length": "10",
#                 "content-type": "application/json"
#         },
#         "body": "b'{\"e\": \"f\"}'",
#         "json": {
#                 "e": "f"
#         },
#         "client": "127.0.0.1:54639",
#         "path_params": {},
#         "query_params": {
#                 "c": ""
#         }
# }

request.post('http://127.0.0.1:8000', headers={'a':'b'}, params='c', data='d', json={'e': 'f'})
# {"headers":{"host":"127.0.0.1:8000","user-agent":"python-requests/2.26.0","accept-encoding":"gzip, deflate","accept":"*/*","connection":"keep-alive","a":"b","content-length":"1"},"body":"d","json":null,"client":["127.0.0.1",65213],"path_params":{},"query_params":{"c":""}}

request.post('http://127.0.0.1:8000', headers={'a':'b'}, params='c', data={'e': 'f'})
# {"headers":{"host":"127.0.0.1:8000","user-agent":"python-requests/2.26.0","accept-encoding":"gzip, deflate","accept":"*/*","connection":"keep-alive","a":"b","content-length":"3","content-type":"application/x-www-form-urlencoded"},"body":"e=f","json":null,"client":["127.0.0.1",65309],"path_params":{},"query_params":{"c":""}}

request.post('http://127.0.0.1:8000', headers={'a':'b'}, params='c', json={'e': 'f'})
# {"headers":{"host":"127.0.0.1:8000","user-agent":"python-requests/2.26.0","accept-encoding":"gzip, deflate","accept":"*/*","connection":"keep-alive","a":"b","content-length":"10","content-type":"application/json"},"body":"{\\"e\\": \\"f\\"}","json":{"e":"f"},"client":["127.0.0.1",65376],"path_params":{},"query_params":{"c":""}}
