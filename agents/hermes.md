# Set Up Server
1. Update
```
sudo apt update
sudo apt dist-upgrade -o APT::Get::Always-Include-Phased-Updates=true
sudo apt autoremove --purge
sudo apt autoclean
sudo apt update
sudo apt upgrade -y
```

2. Choose
- install the package maintainer's version

3. Install packages
```
sudo apt install -y tmux make nginx git gh htop ripgrep jq nodejs npm mkcert ca-certificates curl wget openssl python3 unzip zip xz-utils build-essential sqlite3 rsync openssh-client util-linux
curl -LsSf https://astral.sh/uv/install.sh \
  | env UV_INSTALL_DIR="/usr/local/bin" UV_NO_MODIFY_PATH=1 sh
```

4. Set up
```
timedatectl set-timezone Etc/UTC
```

5. Restart
```
sudo reboot
```

# Obsidian
1. Syncthing
```
mkdir -p /etc/apt/keyrings

curl -L \
  -o /etc/apt/keyrings/syncthing-archive-keyring.gpg \
  https://syncthing.net/release-key.gpg

echo \
  "deb [signed-by=/etc/apt/keyrings/syncthing-archive-keyring.gpg] https://apt.syncthing.net/ syncthing stable-v2" \
  > /etc/apt/sources.list.d/syncthing.list

printf \
  "Package: *\nPin: origin apt.syncthing.net\nPin-Priority: 990\n" \
  > /etc/apt/preferences.d/syncthing.pref

apt update
apt install -y syncthing
```

# Hermes
1. Set up user
```
adduser --disabled-password --gecos "" hermes
```

2. Set up structure
```
install -d -o hermes -g hermes -m 0750 /srv/hermes
install -d -o hermes -g hermes -m 0750 /srv/hermes/data
install -d -o hermes -g hermes -m 0750 /srv/hermes/data/vault
install -d -o hermes -g hermes -m 0750 /srv/hermes/data/workspace

install -d -o hermes -g hermes -m 0700 /srv/hermes/backups

install -d -o hermes -g hermes -m 0700 /home/hermes/.ssh
install -d -o hermes -g hermes -m 0700 /home/hermes/.local/bin
install -d -o hermes -g hermes -m 0700 /home/hermes/.config/systemd/user

chown -R hermes:hermes \
  /home/hermes/.local \
  /home/hermes/.config \
  /home/hermes/.ssh

install -d \
  -o hermes \
  -g hermes \
  -m 0700 \
  /home/hermes/.local/state

install -d \
  -o hermes \
  -g hermes \
  -m 0700 \
  /home/hermes/.local/state/syncthing
```

3. Allow working on restart
```
loginctl enable-linger hermes

HERMES_UID="$(id -u hermes)"
systemctl start "user@${HERMES_UID}.service"

loginctl show-user hermes \
  -p Linger \
  -p State
```

4. Switch user
```
sudo -iu hermes
```

5. Set up PATH
```
cat >> ~/.profile <<'EOF'

export PATH="$HOME/.local/bin:$PATH"

if [ -d "/run/user/$(id -u)" ]; then
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
  export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
fi
EOF

source ~/.profile
```

6. Set up syncthing
```
systemctl --user enable --now syncthing.service
```

# Set Up Obsidian








use uv, pnpm for scripts

