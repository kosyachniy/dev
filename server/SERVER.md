# Set up a server from scratch
## Base
1. Update the ` apt ` package index
```
sudo apt update
```

2. Update packages
```
sudo apt upgrade
```

3. Install main packages
```
apt install tmux make nginx git htop
```

## Installing Docker [link →](https://docs.docker.com/engine/install/ubuntu/)
5. Update the ` apt ` package index and install packages to allow ` apt ` to use a repository over HTTPS
```
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

6. Add Docker’s official GPG key
```
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

7. Set up the repository
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

8. Update the ` apt ` package index, and install the latest version of Docker Engine, containerd, and Docker Compose
```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## Installing Docker Compose
9. Run
```
apt install docker-compose
```

<!-- ## Set up Docker Swarm (if you need)
10. Make a cluster with 1 node
```
docker swarm init --advertise-addr 157.230.103.16
```
(your IP instead of ` 157.230.103.16 `)

## Set up server
11. Customize NGINX for your project

Take [`docker/server/nginx.server.conf`](docker/server/nginx.server.conf) as a basis and add configuration:
```
sudo nano /etc/nginx/sites-enabled/web.conf
```
(your project name instead of ` web `) -->

12. Configure NGINX

Change lines in ` /etc/nginx/nginx.conf `:
```
types_hash_max_size 20480;
client_max_body_size 30m;
```

13. Restart NGINX
```
sudo systemctl restart nginx
```

## Set up encryption [link →](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
14. Install Snap
```
apt install snapd
```

15. Ensure that your version of snapd is up to date
```
sudo snap install core; sudo snap refresh core
```

16. Install Let's Encrypt
```
sudo snap install --classic certbot
```

17. Prepare the Certbot command
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

18. Configure encryption
```
sudo certbot --nginx
```


# TODO: права для проксирования файлов в nginx
# TODO: git формат файла
