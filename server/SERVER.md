# Set up a server from scratch
## Installing Docker [link →](https://docs.docker.com/engine/install/ubuntu/)
1. Update the ` apt ` package index
```
sudo apt update
```

2. Update packages
```
sudo apt upgrade
```

2. Install packages to allow ` apt ` to use a repository over HTTPS
```
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
```

3. Add Docker’s official GPG key
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

4. Set up the stable repository
```
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

5. Update the ` apt ` package index, and install the latest version of Docker Engine and containerd
```
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

6. Verify that Docker Engine is installed correctly by running the ` hello-world ` image
```
sudo docker run hello-world
```

## Installing Docker Compose [link →](https://docs.docker.com/compose/install/)
7. Run this command to download the current stable release of Docker Compose
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

8. Apply executable permissions to the binary
```
sudo chmod +x /usr/local/bin/docker-compose
```

9. Test the installation
```
docker-compose --version
```

## Set up Docker Swarm (if you need)
10. Make a cluster with 1 node
```
docker swarm init --advertise-addr 157.230.103.16
```
(your IP instead of ` 157.230.103.16 `)

## Set up server
11. Install NGINX
```
sudo apt install nginx
```

12. Customize NGINX for your project

Take [`docker/server/nginx.server.conf`](docker/server/nginx.server.conf) as a basis and add configuration:
```
sudo nano /etc/nginx/sites-enabled/web.conf
```
(your project name instead of ` web `)

13. Configure NGINX

Change lines in ` /etc/nginx/nginx.conf `:
```
types_hash_max_size 20480;
client_max_body_size 30m;
```

14. Restart NGINX
```
sudo systemctl restart nginx
```

## Set up encryption [link →](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx)
15. Ensure that your version of snapd is up to date
```
sudo snap install core; sudo snap refresh core
```

16. Remove any Certbot OS packages
```
sudo apt-get remove certbot
```

17. Install Let's Encrypt
```
sudo snap install --classic certbot
```

18. Prepare the Certbot command
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

19. Configure encryption
```
sudo certbot --nginx
```

## Installing Make
20. Install Make
```
apt install make
```
