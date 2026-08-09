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
sudo apt install tmux make nginx git htop ripgrep
```

4. Create user (if needed)
4.1. Create user
```
apt-get update
apt-get install -y curl ca-certificates git jq wget
useradd -m -s /bin/bash openclaw
```

4.2. Copy SSH keys
```
sudo mkdir -p /home/openclaw/.ssh
sudo cp ~/.ssh/authorized_keys /home/openclaw/.ssh/authorized_keys
sudo chown -R openclaw:openclaw /home/openclaw/.ssh
sudo chmod 700 /home/openclaw/.ssh
sudo chmod 600 /home/openclaw/.ssh/authorized_keys
```

4.3. Give access
```
usermod -aG sudo openclaw
echo 'openclaw ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/openclaw
chmod 440 /etc/sudoers.d/openclaw
```

## Install Docker [link →](https://docs.docker.com/engine/install/ubuntu/)
5. Set up Docker's `apt` repository.
```
# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
```

6. Install the Docker packages.
```
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

7. Access
```
sudo usermod -aG docker $USER
```

## Set up encryption [link →](https://certbot.eff.org/instructions?ws=nginx&os=ubuntufocal)
8. Install Snap
```
sudo apt install snapd
```

9. Ensure that your version of snapd is up to date
```
sudo snap install core
sudo snap refresh core
```

10. Install Let's Encrypt
```
sudo snap install --classic certbot
```

11. Prepare the Certbot command
```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

## Set up GitHub
12. Create RSA SSH key
```
ssh-keygen
```

13. Copy public key to https://github.com/settings/keys
```
cat ~/.ssh/id_rsa.pub
```
- or -
```
cat ~/.ssh/id_ed25519.pub
```

14. `~/.ssh/config`:
```
Host github.com
  StrictHostKeyChecking no
  UserKnownHostsFile /dev/null
```

## Set up project
15. Clone a project
```
git clone git@github.com:USER/REPO.git
```
(your GitHub user and repository name)

(exactly this format of the link)


## Set up server
16. Configure NGINX

Change lines in ` /etc/nginx/nginx.conf `:
```
types_hash_max_size 20480;
client_max_body_size 30m;
```

17. Set up NGINX config & run certbot
```
sudo certbot --nginx
```

18. Run project
```
docker compose up --build -d
```
