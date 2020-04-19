curl --include \
     --no-buffer \
     --header "Connection: Upgrade" \
     --header "Upgrade: websocket" \
     --header "Host: 0.0.0.0:5000" \
     --header "Sec-WebSocket-Key: qweqwe" \
     --header "Sec-WebSocket-Version: 13" \
	 --output "term2.txt" \
    http://0.0.0.0:5000/socket.io/

curl --location --request GET 'http://0.0.0.0:5000/socket.io/' \
--header 'Upgrade: WebSocket' \
--header 'Connection: Upgrade' \
--header 'Sec-Websocket-Version: 13' \
--header 'Sec-Websocket-Key: {{client_token}}' \
--output 'term.txt'

curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: 0.0.0.0" -H "Origin: http://0.0.0.0:5000/socket.io/" --output "termsock2.txt" http://0.0.0.0:5000/socket.io/

curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: kosyachniy.com" -H "Origin: https://kosyachniy.com/socket.io/" --output "termsock.txt" https://kosyachniy.com/socket.io/



curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: 0.0.0.0" -H "Origin: http://0.0.0.0:5000/socket.io/" -H "Content-Type: application/json" -d '42/main,["online",{"task":617,"cont":"efe"}]' --output "termsock2.txt" http://0.0.0.0:5000/socket.io/

curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Host: 0.0.0.0" -H "Origin: http://0.0.0.0:5000/socket.io/" -H "Content-Type: application/json" -t '42/main,["online",{"task":617,"cont":"efe"}]' --output "termsock2.txt" http://0.0.0.0:5000/socket.io/



var ws = new WebSocket("http://0.0.0.0:5000/socket.io/")



