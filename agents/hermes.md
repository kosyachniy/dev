# Set Up Server (`root` user)
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

# Obsidian sync (`root` user)
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

# Access (`root` user)
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

4. MacOS:
```
cat ~/.ssh/id_ed25519.pub
```

5. Copy

6. Add to VPS
```
nano ~/.ssh/authorized_keys
```

7. Copy to user
```
install -d \
  -o hermes \
  -g hermes \
  -m 0700 \
  /home/hermes/.ssh

cp \
  /root/.ssh/authorized_keys \
  /home/hermes/.ssh/authorized_keys

chown hermes:hermes \
  /home/hermes/.ssh/authorized_keys

chmod 600 \
  /home/hermes/.ssh/authorized_keys
```

8. Switch user
```
sudo -iu hermes
```

9. Set up PATH
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

10. Set up `ls` formatting
```
cat >> ~/.bashrc <<'EOF'

# Display UTF-8 filenames literally in ls
alias ls='ls --color=auto --quoting-style=literal --show-control-chars'
EOF

source ~/.bashrc
```

11. Set up `git` formatting
```
cd /srv/hermes/data
git config core.quotepath false
```

# Obsidian sync (`hermes` user)
1. Set up syncthing
```
systemctl --user enable --now syncthing.service
```

2. Get Device ID
```
syncthing device-id
```

3. Save Device ID

4. MacOS:
```
ssh -N \
  -L 18384:127.0.0.1:8384 \
  hermes@165.227.131.96
```

5. Open `http://127.0.0.1:18384`

6. Actions → Settings → General
```
Device Name: vps
Usage Reporting: Disabled
```

7. Actions → Settings → GUI
```
GUI Authentication User: alex
GUI Authentication Password: ...
Use HTTPS for GUI: Disabled
```

# Set Up Obsidian (`hermes` user)
1. Create structure
```
mkdir -p \
  "/srv/hermes/data/vault/00 Main" \
  "/srv/hermes/data/vault/01 Inbox" \
  "/srv/hermes/data/vault/10 Self" \
  "/srv/hermes/data/vault/20 Areas" \
  "/srv/hermes/data/vault/30 Action" \
  "/srv/hermes/data/vault/40 Projects" \
  "/srv/hermes/data/vault/50 Resources" \
  "/srv/hermes/data/vault/60 Knowledge" \
  "/srv/hermes/data/vault/70 World" \
  "/srv/hermes/data/vault/80 Memory" \
  "/srv/hermes/data/vault/90 Archive" \
  "/srv/hermes/data/vault/99 System/Templates"
```

2. Main page
```
cat > "/srv/hermes/data/vault/00 Main/Dashboard.md" <<'EOF'
---
type: dashboard
status: active
created: 2026-08-14
---

# Dashboard

## Navigation

- [[01 Inbox]]
- [[10 Self]]
- [[20 Areas]]
- [[30 Action]]
- [[40 Projects]]
- [[50 Resources]]
- [[60 Knowledge]]
- [[70 World]]
- [[80 Memory]]
- [[90 Archive]]
EOF
```

3. Template
```
cat > "/srv/hermes/data/vault/_System/Templates/Note.md" <<'EOF'
---
type: note
status: inbox
created:
updated:
source:
tags: []
---

# Title

## Суть

## Контекст

## Результат

## TODO

## Открытые вопросы

## Связи
EOF
```

4. Ignore syncing
```
cat > /srv/hermes/data/vault/.stignore <<'EOF'
# Obsidian device-specific configuration
(?d).obsidian

# Local trash and OS metadata
(?d).trash
(?d).DS_Store
(?d)Thumbs.db

# Local Syncthing file versions
(?d).stversions
EOF
```

5. `http://127.0.0.1:18384`: Add Folder:
5.1. `General`:
```
Folder Label: Main
Folder ID: main
Folder Path: /srv/hermes/data/vault
```

5.2. `File Versioning`:
```
File Versioning: Staggered File Versioning
Maximum Age: 30 days
```

5.3. `Advanced`:
```
Watch for Changes: Enabled
Full Rescan Interval: 3600
Folder Type: Send & Receive
Ignore Permissions: Enabled
```

6. Install Mac Sync
```
brew install --cask syncthing-app
```

7. Open `Syncthing`

8. Open `http://127.0.0.1:8384`

9. Actions → Settings → General
```
Device Name: mac
```

10. Actions → Show ID

11. Add Remote Device:
11.1 General
```
Device ID: <VPS Sync ID>
Device Name: vps
```
11.2. Advanced
```
Addresses: tcp://<VPS IP>:22000, quic://<VPS IP>:22000, dynamic
```

12. Open `http://127.0.0.1:18384`:

13. Add Device -> Save

14. Folders -> Main -> Edit -> Sharing:
```
mac: Enabled
```

15. Open `http://127.0.0.1:8384`

16. New Folder -> Add:
```
Folder Label: Alex Knowledge
Folder ID: alex-knowledge
Folder Path: /Users/<User>/Documents/Obsidian/main
Folder Type: Send & Receive
```

17. Open `Obsidian`

18. Open folder as vault
```
/Users/<User>/Documents/Obsidian/main
```

# iPhone / iPad
1. Open `Obsidian`

2. Создать хранилище
`Main`

3. Пропустить синхронизацию

4. Open `VaultSync`

5. Connect Obsidian Folder
`Main`

6. Add your computer or server
```
Device ID: <VPS Sync ID>
Name: vps
```

7. Open `http://127.0.0.1:18384`

8. New Device
```
Device Name: iphone
```

9. Folders -> Main -> Edit -> Sharing:
```
iphone: Enabled
```

10. `VaultSync`: Open VaultSync

# Git (`hermes` user)
1. `cd /srv/hermes/data`

2. `git init -b main`

3.
```
git config --global user.name "..."
git config --global user.email "..."
git config user.name "Life OS"
git config user.email "agent@vps.local"
```

4.
```
gh auth login
```
- GitHub.com
- SSH
- new SSH key
- without passphrase
- without title
- Login with a web browser

5. `github.com`: Create repo
- Private

6. `git remote add origin git@github.com:kosyachniy/brain.git`

7. GitIgnore
```
cat > /srv/hermes/data/.gitignore <<'EOF'
# Syncthing runtime
vault/.stfolder/
vault/.stversions/
vault/.syncthing.*.tmp

# Obsidian device-local state
vault/.obsidian/
vault/.trash/
vault/.DS_Store

# Secrets
.env
.env.*
!.env.example
*.pem
*.key
*.p12
*.pfx

# Databases / agent runtime
*.db
*.db-wal
*.db-shm
*.sqlite
*.sqlite3

# Runtime noise
*.log
*.lock
*.pid
*.tmp
*.sock

# Dependencies / caches
node_modules/
**/__pycache__/
**/.pytest_cache/
**/.mypy_cache/

# OS
.DS_Store
Thumbs.db
EOF
```

8. `mkdir -p files`

9. Commit
```
git add .
git commit -m "Pilot"
git push --set-upstream origin main
```

# Rules
1.
use uv, pnpm for scripts

