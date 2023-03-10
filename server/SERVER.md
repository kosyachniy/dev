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
5. Install packages to allow ` apt ` to use a repository over HTTPS
```
sudo apt install ca-certificates curl gnupg lsb-release
```

6. Add Docker’s official GPG key
```
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

7. Set up the repository
```
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

8. Install the latest version of Docker Engine, containerd, and Docker Compose
```
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## Set up server
9. Configure NGINX

Change lines in ` /etc/nginx/nginx.conf `:
```
types_hash_max_size 20480;
client_max_body_size 30m;
```

10. Restart NGINX
```
sudo systemctl restart nginx
```

## Set up encryption [link →](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
11. Install Snap
```
sudo apt install snapd
```

12. Ensure that your version of snapd is up to date
```
sudo snap install core
sudo snap refresh core
```

13. Install Let's Encrypt
```
sudo snap install --classic certbot
```

14. Prepare the Certbot command
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

## Set up GitHub
15. Create RSA SSH key
```
ssh-keygen
```

16. Copy public key to https://github.com/settings/keys
```
cat ~/.ssh/id_rsa.pub
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
