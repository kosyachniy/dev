##############
# kosyachniy #
##############

server {
    listen 80;
    server_name kosyachniy.com www.kosyachniy.com;
    client_max_body_size 20M;

    location /api/ {
		include proxy_params;
        rewrite ^/api/?(.*)$ /$1 break;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /load/ {
        alias /root/web/data/load/;
    }

    location /socket.io/ {
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_pass http://127.0.0.1:5000/socket.io/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;include proxy_params;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_redirect off;
        proxy_buffering off;

        proxy_set_header HOST $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass_request_headers on;
        #proxy_pass http://<server ip="">:<server port="">;
        proxy_http_version 1.0;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
}