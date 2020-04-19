# Название

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.edit", "params": {"id": 1, "name": "Название"}, "token": "test"}' http://127.0.0.1:5000/

# Содержание

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.edit", "params": {"id": 1, "cont": "Содержание"}, "token": "test"}' http://127.0.0.1:5000/

# Категория

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.edit", "params": {"id": 1, "category": 1}, "token": "test"}' http://127.0.0.1:5000/

# Теги

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.edit", "params": {"id": 1, "tags": ["Flask", "React"]}, "token": "test"}' http://127.0.0.1:5000/

# Обложка

curl -X POST -H "Content-Type: application/json" -d '{"method": "posts.edit", "params": {"id": 1, "cover": "/9j/2wCEABQQEBkSGScXFycyJh8mMi4mJiYmLj41NTU1NT5EQUFBQUFBREREREREREREREREREREREREREREREREREREREQBFRkZIBwgJhgYJjYmICY2RDYrKzZERERCNUJERERERERERERERERERERERERERERERERERERERERERERERERERP/dAAQABP/uAA5BZG9iZQBkwAAAAAH/wAARCAA5ADkDACIAAREBAhEB/8QAdQAAAgMBAQAAAAAAAAAAAAAABAUBAwYCAAEBAQEBAAAAAAAAAAAAAAAAAQACAxAAAgECBQEGBgIDAAAAAAAAAQIDABEEEiExQVEFEyJhcZEUMlKBwfAVQrHR4REBAQEBAQEBAQAAAAAAAAAAAAERMQIhQXH/2gAMAwAAARECEQA/AM/8TNKSUY77XomBJsRC0sMhEqHxC+4P7p7UtTwetH9hyPHig6LmuCrDyNTnOg/jJXYCUknbWiVRXcK2tFdt4RMPLY3DHxI34P8AulTqwNwbsdQB060dP6mWLI5Xa1e7sgX4qQrBgz34PvROGwD4yUK11B2Xn/lOs5oIgiouetantPBQYLDmyjXwDTk1m/hT9QqL/9DM5SaOwK95G4UgEfmgj6UT2eLuyf2tdQefKi7jEy1GMvlCFiSBpVKIjyWvoBlvRuFvPIqSR5WBNtwQfvx/iuoeznUMcpzHShWWKcFiiGBdbAklT++VarBzYRFz5rNuS1IIRhUASWQF0Ni1iPQDrXUsudgS2g0GXmhrnVmPlkkJAKmNSxA5PFz6cdaWZaMDllaw0G531oXuz0FMFf/RztgeRUqzQussZGZTepyg8V2pCfKBfqeKPgz22Ix3fwF1sHtzwaqikEosm1rMTSHA41lugXOOFY6n79fKmkGLw76qrK3I2rFjr59STL1xiuzsPlDxoMw2DXNUw4TNdmAvyW2tTRy5W8aXPBJ460FjFOXNiHAUHRV3ar+ud+8DYmdHtHFqo5HJ/eKrySfSfaiWVox3jrlJB7tfpHn50L38nWmbRuP/0keHwzSIGdZAWtYoyaj0NScKyta0muq+JPlHzc+1KDv7VHFQyHS4YFhl72+ut49wfXSr5ZJ2BzNITcKtzHbXr+DWerwqLRK0ysqI0wve3ijta3rb7Gg5p2whzZpBiDY3JRl/NK12Nc1Yhb9pYlzdpCSa5/kMR9ZoapqT/9k=", "file": "test.jpg"}, "token": "test"}' http://127.0.0.1:5000/