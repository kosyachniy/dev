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

4. Configure Git
```
git config --global credential.credentialStore cache
```

## Installing Docker [link →](https://docs.docker.com/engine/install/ubuntu/)
5. Install packages to allow ` apt ` to use a repository over HTTPS
```
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
```

6. Add Docker’s official GPG key
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

7. Set up the stable repository
```
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

8. Update the ` apt ` package index, and install the latest version of Docker Engine and containerd
```
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

## Installing Docker Compose [link →](https://docs.docker.com/compose/install/)
9. Run this command to download the current stable release of Docker Compose
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

10. Apply executable permissions to the binary
```
sudo chmod +x /usr/local/bin/docker-compose
```

11. Test the installation
```
docker-compose --version
```

## Set up Docker Swarm (if you need)
12. Make a cluster with 1 node
```
docker swarm init --advertise-addr 157.230.103.16
```
(your IP instead of ` 157.230.103.16 `)

## Set up server
13. Customize NGINX for your project

Take [`docker/server/nginx.server.conf`](docker/server/nginx.server.conf) as a basis and add configuration:
```
sudo nano /etc/nginx/sites-enabled/web.conf
```
(your project name instead of ` web `)

14. Configure NGINX

Change lines in ` /etc/nginx/nginx.conf `:
```
types_hash_max_size 20480;
client_max_body_size 30m;
```

15. Restart NGINX
```
sudo systemctl restart nginx
```

## Set up encryption [link →](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
16. Install Snap
```
apt install snapd
```

17. Ensure that your version of snapd is up to date
```
sudo snap install core; sudo snap refresh core
```

18. Install Let's Encrypt
```
sudo snap install --classic certbot
```

19. Prepare the Certbot command
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

20. Configure encryption
```
sudo certbot --nginx
```
