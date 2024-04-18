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
sudo apt install tmux make nginx git htop
```

## Install Docker [link →](https://docs.docker.com/engine/install/ubuntu/)
5. Add Docker's official GPG key
```
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

6. Add the repository to Apt sources
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

7. Install the latest version of Docker Engine, containerd, and Docker Compose
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## Set up server
8. Configure NGINX

Change lines in ` /etc/nginx/nginx.conf `:
```
types_hash_max_size 20480;
client_max_body_size 30m;
```

9. Restart NGINX
```
sudo systemctl restart nginx
```

## Set up encryption [link →](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
10. Install Snap
```
sudo apt install snapd
```

11. Ensure that your version of snapd is up to date
```
sudo snap install core
sudo snap refresh core
```

12. Install Let's Encrypt
```
sudo snap install --classic certbot
```

13. Prepare the Certbot command
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

## Set up GitHub
14. Create RSA SSH key
```
ssh-keygen
```

15. Copy public key to https://github.com/settings/keys
```
cat ~/.ssh/id_rsa.pub
```

16. `~/.ssh/config`:
```
Host github.com
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

## Set up project
17. Clone a project
```
git clone git@github.com:USER/REPO.git
```
(your GitHub user and repository name)

(exactly this format of the link)

18. Set up NGINX config & run certbot
```
certbot --nginx
```

19. Run project
```
docker compose up --build -d
```
