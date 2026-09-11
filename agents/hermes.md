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
sudo apt install -y tmux make nginx git gh htop ripgrep jq nodejs npm mkcert ca-certificates curl wget openssl python3 unzip zip xz-utils build-essential sqlite3 rsync openssh-client util-linux ffmpeg
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

10. AutoCommit script
```
cat > ~/.local/bin/git-autocommit <<'EOF'
#!/usr/bin/env bash

set -Eeuo pipefail

REPO="/srv/hermes/data"
LOCK="$HOME/.cache/hermes-data-git.lock"

mkdir -p "$HOME/.cache"

exec 9>"$LOCK"
flock -n 9 || exit 0

cd "$REPO"

# Не коммитим файлы прямо во время активной записи.
if find vault workspace \
  -type f \
  -mmin -1 \
  -print -quit \
  | grep -q .; then
  exit 0
fi

git add -A -- \
  vault \
  workspace \
  .gitignore

if ! git diff --cached --quiet; then
  git commit \
    -m "auto: $(date -u +'%Y-%m-%dT%H:%M:%SZ')"
fi

# Push выполняется только если remote уже настроен.
if git remote get-url origin >/dev/null 2>&1; then
  for attempt in 1 2 3; do
    if git push origin main; then
      exit 0
    fi

    sleep $((attempt * 10))
  done

  exit 1
fi
EOF

chmod 700 \
  ~/.local/bin/git-autocommit
```

11. AutoCommit service
```
cat > ~/.config/systemd/user/git-autocommit.service <<'EOF'
[Unit]
Description=Auto-commit Hermes knowledge base

[Service]
Type=oneshot
ExecStart=/home/hermes/.local/bin/git-autocommit

UMask=0077
NoNewPrivileges=true
EOF
```

12. AutoCommit timer
```
cat > ~/.config/systemd/user/git-autocommit.timer <<'EOF'
[Unit]
Description=Git autocommit every five minutes

[Timer]
OnBootSec=3min
OnUnitActiveSec=5min
RandomizedDelaySec=30
Persistent=true

[Install]
WantedBy=timers.target
EOF
```

13. AutoCommit run
```
systemctl --user daemon-reload

systemctl --user enable --now \
  git-autocommit.timer
```

14. AutoCommit test
```
systemctl --user start \
  git-autocommit.service

journalctl --user \
  -u git-autocommit.service \
  -n 100 \
  --no-pager
```

# Set Up Hermes

1. Create bot
@BotFather

2. Write message to bot

3. Install
```
curl -fsSL \
  https://hermes-agent.nousresearch.com/install.sh \
  | bash -s -- --skip-browser
```

4. Restart
```
source ~/.profile
hash -r
```

# Browser (`root` user)

1. Install
```
npx playwright install-deps chromium
```

2.
```
sudo -iu hermes
```

3.
```
cd /home/hermes/.hermes/hermes-agent
npx playwright install chromium
```

4.
```
exit
```

5. Docker
```
apt update

apt install -y \
  docker.io \
  docker-compose-v2

systemctl enable --now docker
```

6.
```
mkdir -p /opt/searxng/core-config
cd /opt/searxng
```

7.
```
curl -fsSLO \
  https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml

curl -fsSLO \
  https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example

cp .env.example .env
```

8.
```
cat >> /opt/searxng/.env <<'EOF'

SEARXNG_HOST=127.0.0.1
SEARXNG_PORT=8080
EOF
```

9. Turn on JSON API
```
cat > /opt/searxng/core-config/settings.yml <<'EOF'
use_default_settings: true

general:
  debug: false
  instance_name: "Hermes SearXNG"

search:
  safe_search: 0
  formats:
    - html
    - json

server:
  limiter: false
  image_proxy: true

valkey:
  url: valkey://valkey:6379/0
EOF
```

10.
```
SECRET="$(openssl rand -hex 32)"
echo "$SECRET"
```

11.
```
cat > /opt/searxng/core-config/settings.yml <<EOF
use_default_settings: true

general:
  debug: false
  instance_name: "Hermes SearXNG"

search:
  safe_search: 0
  formats:
    - html
    - json

server:
  secret_key: "$SECRET"
  limiter: false
  image_proxy: true

valkey:
  url: valkey://valkey:6379/0
EOF
```

12.
```
cd /opt/searxng

docker compose pull
docker compose up -d
```

13.
```
sudo -iu hermes
```

14.
```
hermes config set web.backend searxng
hermes config set web.search_backend searxng
hermes config set web.extract_backend firecrawl
hermes config set web.keyless_fallback true
hermes config set web.keyless_rescue true
hermes config set web.provider_tier.exa free
hermes config set web.provider_tier.parallel free
hermes config set web.provider_tier.firecrawl free
```

# Set Up LLM (`hermes` user)

1.
```
mkdir -p ~/.hermes

touch ~/.hermes/.env
chmod 600 ~/.hermes/.env
```

2.
```
sed -i \
  '/^OBSIDIAN_VAULT_PATH=/d' \
  ~/.hermes/.env
```

3.
```
echo \
  'OBSIDIAN_VAULT_PATH=/srv/hermes/data/vault' \
  >> ~/.hermes/.env
```

4.
```
hermes config set \
  terminal.backend local

hermes config set \
  terminal.cwd /srv/hermes/data/workspace
```

5.
```
hermes config set \
  approvals.mode smart

hermes config set \
  approvals.cron_mode deny

hermes config set \
  memory.write_approval true

hermes config set \
  skills.write_approval true
```

6.
```
cat > /srv/hermes/data/workspace/AGENTS.md <<'EOF'
# Alex Personal AI Workspace

## Canonical knowledge base

The canonical human-readable knowledge base is:

`/srv/hermes/data/vault`

This is an Obsidian-compatible Markdown vault synchronized by Syncthing.

Hermes reads and writes the files directly.
Syncthing is only the transport layer between devices.

## Before answering

Search the vault before answering questions about:

- Alex's projects
- previous decisions
- architecture
- research
- plans
- people
- meetings
- comparisons
- personal systems

## Capturing knowledge

New unsorted knowledge goes to:

`/srv/hermes/data/vault/01 Inbox`

Before creating a durable note:

1. Search for an existing relevant note.
2. Update it only when it is clearly canonical.
3. Otherwise create a new note in `01 Inbox`.
4. Use ordinary Markdown.
5. Use descriptive human-readable filenames.
6. Add YAML frontmatter for durable notes.
7. Add relevant `[[wikilinks]]`.
8. Preserve dates and source information.
9. Never invent missing facts or sources.

## Editing policy

Allowed normally:

- create a new note
- append a dated section
- add links
- fix obvious formatting

Require explicit approval before:

- deleting notes
- moving or renaming established notes
- merging notes
- rewriting large sections
- changing an established decision
- modifying more than 10 existing notes

## Conflict safety

Before modifying an existing note:

1. Read its current content.
2. Check whether a `.sync-conflict-*` copy exists.
3. Avoid writing over a note that was modified very recently.
4. Prefer a new Inbox note when uncertain.

## Secrets

Never store in the vault:

- passwords
- API keys
- Telegram bot tokens
- cookies
- auth headers
- private keys
- recovery codes
- raw secret-bearing configs

## Git

The VPS is the only Git writer.

Never:

- force push
- rewrite published history
- edit `.git` directly
EOF
```

# Holographic

1. Select
```
hermes memory setup
```
- Holographic

#


# Rules
1.
use uv, pnpm for scripts

