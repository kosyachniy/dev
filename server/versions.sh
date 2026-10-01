#!/usr/bin/env bash

set -uo pipefail

# ============================================================
# CONFIG
# ============================================================

HERMES_USER="hermes"
HERMES_HOME="/home/hermes"
HERMES_BIN="${HERMES_HOME}/.local/bin/hermes"

DATA_DIR="/srv/hermes/data"
VAULT_DIR="${DATA_DIR}/vault"
WORKSPACE_DIR="${DATA_DIR}/workspace"

SEARXNG_URL="http://127.0.0.1:8080"

if id "$HERMES_USER" >/dev/null 2>&1; then
    HERMES_UID="$(id -u "$HERMES_USER")"
else
    HERMES_UID=""
fi


# ============================================================
# HELPERS
# ============================================================

line() {
    printf '%s\n' "========================================"
}

section() {
    echo
    line
    echo " $1"
    line
}

human_bytes() {
    numfmt \
        --to=iec \
        --suffix=B \
        "$1" 2>/dev/null \
        || echo "$1"
}

check() {
    local name="$1"
    local binary="$2"
    shift 2

    printf "%-26s " "$name"

    if command -v "$binary" >/dev/null 2>&1; then
        "$binary" "$@" 2>&1 | head -1
    else
        echo "NOT INSTALLED"
    fi
}

as_hermes() {
    if [ -z "$HERMES_UID" ]; then
        return 127
    fi

    if [ "$(id -un)" = "$HERMES_USER" ]; then
        "$@"
        return
    fi

    if [ "$(id -u)" -eq 0 ]; then
        runuser \
            -u "$HERMES_USER" \
            -- env \
            HOME="$HERMES_HOME" \
            USER="$HERMES_USER" \
            LOGNAME="$HERMES_USER" \
            PATH="${HERMES_HOME}/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
            XDG_RUNTIME_DIR="/run/user/${HERMES_UID}" \
            DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/${HERMES_UID}/bus" \
            "$@"
        return
    fi

    return 126
}

user_service_state() {
    local service="$1"

    if as_hermes \
        systemctl --user is-active "$service" \
        >/dev/null 2>&1; then

        echo "ACTIVE"
        return
    fi

    if as_hermes \
        systemctl --user is-enabled "$service" \
        >/dev/null 2>&1; then

        echo "INACTIVE (enabled)"
        return
    fi

    echo "INACTIVE"
}

system_service_state() {
    local service="$1"

    if systemctl is-active "$service" >/dev/null 2>&1; then
        echo "ACTIVE"
    elif systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo "INACTIVE (enabled)"
    else
        echo "INACTIVE"
    fi
}


# ============================================================
# PRELOAD HERMES / UV INFO
# ============================================================

HERMES_DOCTOR=""

if [ -x "$HERMES_BIN" ]; then
    HERMES_DOCTOR="$(
        as_hermes \
            env NO_COLOR=1 \
            "$HERMES_BIN" doctor \
            2>&1 \
            || true
    )"
fi

UV_TOOLS=""

if command -v uv >/dev/null 2>&1; then
    UV_TOOLS="$(
        as_hermes uv tool list \
            2>/dev/null \
            || true
    )"
fi


# ============================================================
# SYSTEM
# ============================================================

line
echo " SYSTEM"
line

if [ -f /etc/os-release ]; then
    . /etc/os-release
    printf "%-18s %s\n" \
        "OS:" \
        "${PRETTY_NAME:-unknown}"
fi

printf "%-18s %s\n" \
    "Kernel:" \
    "$(uname -r)"

printf "%-18s %s\n" \
    "Architecture:" \
    "$(uname -m)"

printf "%-18s %s\n" \
    "Hostname:" \
    "$(hostname)"

if command -v timedatectl >/dev/null 2>&1; then
    TIMEZONE="$(
        timedatectl show \
            -p Timezone \
            --value \
            2>/dev/null \
            || true
    )"

    printf "%-18s %s\n" \
        "Timezone:" \
        "${TIMEZONE:-unknown}"
fi

EFFECTIVE_LANG="$(
    locale 2>/dev/null \
        | awk -F= '/^LANG=/ {
            gsub(/"/, "", $2)
            print $2
        }'
)"

EFFECTIVE_CTYPE="$(
    locale 2>/dev/null \
        | awk -F= '/^LC_CTYPE=/ {
            gsub(/"/, "", $2)
            print $2
        }'
)"

CHARMAP="$(
    locale charmap 2>/dev/null \
        || true
)"

printf "%-18s %s\n" \
    "LANG:" \
    "${EFFECTIVE_LANG:-unset}"

printf "%-18s %s\n" \
    "LC_CTYPE:" \
    "${EFFECTIVE_CTYPE:-unset}"

printf "%-18s %s\n" \
    "Charset:" \
    "${CHARMAP:-unknown}"

if [ -f /var/run/reboot-required ]; then
    printf "%-18s %s\n" \
        "Reboot:" \
        "REQUIRED"
else
    printf "%-18s %s\n" \
        "Reboot:" \
        "not required"
fi

LATEST_KERNEL="$(
    find /boot \
        -maxdepth 1 \
        -type f \
        -name 'vmlinuz-*' \
        -printf '%f\n' \
        2>/dev/null \
        | sed 's/^vmlinuz-//' \
        | sort -V \
        | tail -1
)"

if [ -n "$LATEST_KERNEL" ]; then
    printf "%-18s %s\n" \
        "Latest kernel:" \
        "$LATEST_KERNEL"

    if [ "$(uname -r)" = "$LATEST_KERNEL" ]; then
        printf "%-18s %s\n" \
            "Kernel status:" \
            "CURRENT"
    else
        printf "%-18s %s\n" \
            "Kernel status:" \
            "OLD KERNEL RUNNING"
    fi
fi


# ============================================================
# CURRENT USER
# ============================================================

section "CURRENT USER"

printf "%-22s %s\n" \
    "User:" \
    "$(id -un)"

printf "%-22s %s\n" \
    "UID:" \
    "$(id -u)"

printf "%-22s %s (%s)\n" \
    "Primary group:" \
    "$(id -gn)" \
    "$(id -g)"

printf "%-22s %s\n" \
    "Groups:" \
    "$(id -Gn | tr ' ' ',')"

if [ "$(id -u)" -eq 0 ]; then
    printf "%-22s %s\n" "Root:" "YES"
else
    printf "%-22s %s\n" "Root:" "NO"
fi

if id -nG 2>/dev/null | grep -qw sudo; then
    printf "%-22s %s\n" \
        "Sudo group:" \
        "YES"
else
    printf "%-22s %s\n" \
        "Sudo group:" \
        "NO"
fi

if command -v sudo >/dev/null 2>&1 \
    && sudo -n true >/dev/null 2>&1; then

    printf "%-22s %s\n" \
        "Passwordless sudo:" \
        "YES"
else
    printf "%-22s %s\n" \
        "Passwordless sudo:" \
        "NO"
fi


# ============================================================
# VPS RESOURCES
# ============================================================

section "VPS RESOURCES"

CPU_MODEL="$(
    lscpu 2>/dev/null \
        | awk -F: '/Model name/ {
            gsub(/^[ \t]+/, "", $2)
            print $2
            exit
        }'
)"

printf "%-22s %s\n" \
    "CPU model:" \
    "${CPU_MODEL:-unknown}"

printf "%-22s %s\n" \
    "Logical CPUs:" \
    "$(nproc 2>/dev/null || echo unknown)"

PHYSICAL_CORES="$(
    lscpu -p=CORE,SOCKET 2>/dev/null \
        | grep -v '^#' \
        | sort -u \
        | wc -l
)"

CPU_SOCKETS="$(
    lscpu -p=SOCKET 2>/dev/null \
        | grep -v '^#' \
        | sort -u \
        | wc -l
)"

printf "%-22s %s\n" \
    "Physical cores:" \
    "$PHYSICAL_CORES"

printf "%-22s %s\n" \
    "CPU sockets:" \
    "$CPU_SOCKETS"

RAM_TOTAL="$(
    free -b \
        | awk '/^Mem:/ {print $2}'
)"

RAM_USED="$(
    free -b \
        | awk '/^Mem:/ {print $3}'
)"

RAM_AVAILABLE="$(
    free -b \
        | awk '/^Mem:/ {print $7}'
)"

SWAP_TOTAL="$(
    free -b \
        | awk '/^Swap:/ {print $2}'
)"

SWAP_USED="$(
    free -b \
        | awk '/^Swap:/ {print $3}'
)"

printf "%-22s %s\n" \
    "RAM total:" \
    "$(human_bytes "$RAM_TOTAL")"

printf "%-22s %s\n" \
    "RAM used:" \
    "$(human_bytes "$RAM_USED")"

printf "%-22s %s\n" \
    "RAM available:" \
    "$(human_bytes "$RAM_AVAILABLE")"

printf "%-22s %s\n" \
    "Swap total:" \
    "$(human_bytes "$SWAP_TOTAL")"

printf "%-22s %s\n" \
    "Swap used:" \
    "$(human_bytes "$SWAP_USED")"

DISK_TOTAL="$(
    df -B1 / \
        | awk 'NR==2 {print $2}'
)"

DISK_USED="$(
    df -B1 / \
        | awk 'NR==2 {print $3}'
)"

DISK_AVAILABLE="$(
    df -B1 / \
        | awk 'NR==2 {print $4}'
)"

printf "%-22s %s\n" \
    "Disk / total:" \
    "$(human_bytes "$DISK_TOTAL")"

printf "%-22s %s\n" \
    "Disk / used:" \
    "$(human_bytes "$DISK_USED")"

printf "%-22s %s\n" \
    "Disk / available:" \
    "$(human_bytes "$DISK_AVAILABLE")"


# ============================================================
# RUNTIMES & PACKAGE MANAGERS
# ============================================================

section "RUNTIMES & PACKAGE MANAGERS"

check "Python" python3 --version
check "uv" uv --version

echo

check "Node.js" node --version
check "npm" npm --version
check "npx" npx --version
check "pnpm" pnpm --version
check "Corepack" corepack --version


# ============================================================
# IMPORTANT TOOLS
# ============================================================

section "IMPORTANT TOOLS"

check "Git" git --version
check "GitHub CLI" gh --version

echo

printf "%-26s " "Hermes"

if [ -x "$HERMES_BIN" ]; then
    as_hermes \
        "$HERMES_BIN" --version \
        2>&1 \
        | head -1
else
    echo "NOT INSTALLED"
fi

check "Syncthing" \
    syncthing \
    --version

check "FFmpeg" \
    ffmpeg \
    -version

printf "%-26s " "Browser Use"

BROWSER_USE_VERSION="$(
    printf '%s\n' "$UV_TOOLS" \
        | awk '$1 == "browser-use" {
            print $1 " " $2
            exit
        }'
)"

if [ -n "$BROWSER_USE_VERSION" ]; then
    echo "$BROWSER_USE_VERSION"
else
    echo "NOT INSTALLED"
fi

echo

check "curl" curl --version
check "wget" wget --version
check "jq" jq --version
check "ripgrep" rg --version
check "SQLite" sqlite3 --version

echo

check "GCC" gcc --version
check "Make" make --version
check "rsync" rsync --version
check "SSH" ssh -V

echo

check "nginx" nginx -v
check "tmux" tmux -V
check "mkcert" mkcert --version

echo

check "Docker" docker --version

printf "%-26s " "Docker Compose"

if command -v docker >/dev/null 2>&1; then
    docker compose version \
        2>&1 \
        | head -1
else
    echo "NOT INSTALLED"
fi


# ============================================================
# SERVICES
# ============================================================

section "SERVICES"

printf "%-26s %s\n" \
    "Syncthing (user)" \
    "$(user_service_state syncthing.service)"

printf "%-26s %s\n" \
    "Hermes Gateway" \
    "$(user_service_state hermes-gateway.service)"

printf "%-26s %s\n" \
    "Docker daemon" \
    "$(system_service_state docker.service)"

printf "%-26s %s\n" \
    "nginx" \
    "$(system_service_state nginx.service)"

printf "%-26s " \
    "Docker access (user)"

if docker info >/dev/null 2>&1; then
    echo "YES"
else
    echo "NO"
fi


# ============================================================
# AI / KNOWLEDGE SERVICES
# ============================================================

section "AI / KNOWLEDGE SERVICES"

printf "%-26s " "SearXNG"

if curl \
    --connect-timeout 2 \
    --max-time 4 \
    -fsS \
    -o /dev/null \
    "${SEARXNG_URL}/" \
    2>/dev/null; then

    echo "UP — ${SEARXNG_URL}"
else
    echo "DOWN / NOT CONFIGURED"
fi


printf "%-26s " "SearXNG JSON API"

if curl \
    --connect-timeout 2 \
    --max-time 10 \
    -fsS \
    "${SEARXNG_URL}/search?q=test&format=json" \
    2>/dev/null \
    | jq -e '.results' \
    >/dev/null 2>&1; then

    echo "OK"
else
    echo "FAILED / unavailable"
fi


printf "%-26s " "Hermes vault"

if [ -d "$VAULT_DIR" ]; then
    VAULT_SIZE="$(
        du -sh "$VAULT_DIR" \
            2>/dev/null \
            | awk '{print $1}'
    )"

    VAULT_FILES="$(
        find "$VAULT_DIR" \
            -type f \
            2>/dev/null \
            | wc -l
    )"

    echo "OK — ${VAULT_SIZE:-?}, ${VAULT_FILES} files"
else
    echo "NOT FOUND"
fi


printf "%-26s " "Vault files >50MB"

if [ -d "$VAULT_DIR" ]; then
    LARGE_FILES="$(
        find "$VAULT_DIR" \
            -type f \
            -size +50M \
            2>/dev/null \
            | wc -l
    )"

    echo "$LARGE_FILES"
else
    echo "N/A"
fi


printf "%-26s " "Largest vault file"

if [ -d "$VAULT_DIR" ]; then
    LARGEST="$(
        find "$VAULT_DIR" \
            -type f \
            -printf '%s\t%p\n' \
            2>/dev/null \
            | sort -nr \
            | head -1
    )"

    if [ -n "$LARGEST" ]; then
        LARGEST_SIZE="$(
            printf '%s\n' "$LARGEST" \
                | cut -f1
        )"

        LARGEST_PATH="$(
            printf '%s\n' "$LARGEST" \
                | cut -f2-
        )"

        echo "$(human_bytes "$LARGEST_SIZE") — $LARGEST_PATH"
    else
        echo "N/A"
    fi
else
    echo "N/A"
fi


# ============================================================
# BRAIN GIT
# ============================================================

section "BRAIN GIT"

if git \
    -C "$DATA_DIR" \
    rev-parse \
    --is-inside-work-tree \
    >/dev/null 2>&1; then

    BRAIN_BRANCH="$(
        git -C "$DATA_DIR" \
            branch --show-current \
            2>/dev/null
    )"

    BRAIN_CHANGES="$(
        git -C "$DATA_DIR" \
            status --porcelain \
            2>/dev/null \
            | wc -l
    )"

    GIT_SIZE="$(
        du -sh "${DATA_DIR}/.git" \
            2>/dev/null \
            | awk '{print $1}'
    )"

    GIT_NAME="$(
        git -C "$DATA_DIR" \
            config --get user.name \
            2>/dev/null \
            || true
    )"

    GIT_EMAIL="$(
        git -C "$DATA_DIR" \
            config --get user.email \
            2>/dev/null \
            || true
    )"

    QUOTE_PATH="$(
        git -C "$DATA_DIR" \
            config --get core.quotepath \
            2>/dev/null \
            || true
    )"

    printf "%-26s %s\n" \
        "Repository:" \
        "OK"

    printf "%-26s %s\n" \
        "Branch:" \
        "${BRAIN_BRANCH:-detached}"

    printf "%-26s %s\n" \
        "Uncommitted changes:" \
        "$BRAIN_CHANGES"

    printf "%-26s %s\n" \
        ".git size:" \
        "${GIT_SIZE:-unknown}"

    printf "%-26s %s\n" \
        "Commit author:" \
        "${GIT_NAME:-unset}"

    printf "%-26s %s\n" \
        "Commit email:" \
        "${GIT_EMAIL:-unset}"

    printf "%-26s %s\n" \
        "core.quotePath:" \
        "${QUOTE_PATH:-default}"
else
    echo "Brain Git repository is NOT INITIALIZED"
fi


# ============================================================
# HERMES DETAILS
# ============================================================

section "HERMES"

if [ -x "$HERMES_BIN" ]; then

    printf "%-26s %s\n" \
        "Binary:" \
        "$HERMES_BIN"

    printf "%-26s " "Version:"

    as_hermes \
        "$HERMES_BIN" --version \
        2>/dev/null \
        | head -1

    printf "%-26s " "Memory provider:"

    MEMORY_PROVIDER="$(
        as_hermes \
            "$HERMES_BIN" \
            config get memory.provider \
            2>/dev/null \
            | tail -1
    )"

    echo "${MEMORY_PROVIDER:-built-in/unknown}"


    printf "%-26s " "OpenAI Codex auth:"

    if printf '%s\n' "$HERMES_DOCTOR" \
        | grep -Eqi \
            'OpenAI Codex auth.*logged in'; then

        echo "LOGGED IN"
    else
        echo "NOT DETECTED"
    fi


    printf "%-26s " "Vault path:"

    if [ -f "${HERMES_HOME}/.hermes/.env" ]; then

        VAULT_PATH="$(
            grep '^OBSIDIAN_VAULT_PATH=' \
                "${HERMES_HOME}/.hermes/.env" \
                2>/dev/null \
                | tail -1 \
                | cut -d= -f2-
        )"

        echo "${VAULT_PATH:-NOT CONFIGURED}"
    else
        echo "NOT CONFIGURED"
    fi


    printf "%-26s " "Telegram allowlist:"

    if [ -f "${HERMES_HOME}/.hermes/.env" ]; then

        TELEGRAM_USERS="$(
            grep '^TELEGRAM_ALLOWED_USERS=' \
                "${HERMES_HOME}/.hermes/.env" \
                2>/dev/null \
                | tail -1 \
                | cut -d= -f2-
        )"

        if [ -n "$TELEGRAM_USERS" ]; then
            echo "CONFIGURED"
        else
            echo "NOT CONFIGURED"
        fi
    else
        echo "NOT CONFIGURED"
    fi


    printf "%-26s " "Doctor advisories:"

    DOCTOR_ISSUES="$(
        printf '%s\n' "$HERMES_DOCTOR" \
            | sed -n \
                's/.*Found \([0-9][0-9]*\) issue(s).*/\1/p' \
            | tail -1
    )"

    if [ -n "$DOCTOR_ISSUES" ]; then
        echo "$DOCTOR_ISSUES"
    else
        echo "0 / not reported"
    fi

else
    echo "Hermes is not installed for user '${HERMES_USER}'."
fi


# ============================================================
# UV TOOLS
# ============================================================

section "UV TOOLS"

if [ -n "$UV_TOOLS" ]; then
    echo "$UV_TOOLS"
else
    echo "No uv tools installed for ${HERMES_USER}"
fi


# ============================================================
# GLOBAL NPM PACKAGES
# ============================================================

section "GLOBAL NPM PACKAGES"

if command -v npm >/dev/null 2>&1; then
    npm list -g \
        --depth=0 \
        2>/dev/null \
        || true
else
    echo "npm NOT INSTALLED"
fi


# ============================================================
# MANUAL APT PACKAGES
# ============================================================

section "MANUAL APT PACKAGES"

MANUAL_COUNT=0

while read -r pkg; do
    [ -z "$pkg" ] && continue

    # Avoid duplicate Python implementation/library noise.
    case "$pkg" in
        python|python-*|python3|python3-*|libpython*)
            continue
            ;;
    esac

    if dpkg-query \
        -W \
        -f='${binary:Package}\t${Version}\n' \
        "$pkg" \
        2>/dev/null; then

        MANUAL_COUNT=$((MANUAL_COUNT + 1))
    fi

done < <(
    apt-mark showmanual \
        2>/dev/null \
        | sort
)

echo

printf "Manual packages shown: %s\n" \
    "$MANUAL_COUNT"

TOTAL_PACKAGES="$(
    dpkg-query \
        -W \
        -f='${binary:Package}\n' \
        2>/dev/null \
        | wc -l
)"

printf "Total installed APT packages: %s\n" \
    "$TOTAL_PACKAGES"


# ============================================================
# APT INSTALL HISTORY
# ============================================================

section "APT INSTALL COMMAND HISTORY"

if compgen -G "/var/log/apt/history.log*" >/dev/null; then

    zgrep -h '^Commandline:' \
        /var/log/apt/history.log* \
        2>/dev/null \
        | sed 's/^Commandline: //' \
        | grep -v '^/usr/bin/unattended-upgrade$' \
        | tail -50 \
        || true

else
    echo "No APT history found."
fi


# ============================================================
# SNAP
# ============================================================

section "SNAP PACKAGES"

if command -v snap >/dev/null 2>&1; then

    SNAP_OUTPUT="$(
        snap list \
            2>/dev/null \
            || true
    )"

    if [ -n "$SNAP_OUTPUT" ]; then
        echo "$SNAP_OUTPUT"
    else
        echo "No snaps installed"
    fi

else
    echo "snap NOT INSTALLED"
fi


# ============================================================
# IMPORTANT LISTENERS
# ============================================================

section "IMPORTANT LISTENERS"

listener_tcp() {
    local port="$1"

    ss -H -lnt \
        2>/dev/null \
        | awk -v p=":${port}$" \
            '$4 ~ p {print $4}' \
        | paste -sd ',' -
}

listener_udp() {
    local port="$1"

    ss -H -lnu \
        2>/dev/null \
        | awk -v p=":${port}$" \
            '$5 ~ p {print $5}' \
        | paste -sd ',' -
}

printf "%-26s %s\n" \
    "Syncthing GUI:" \
    "$(listener_tcp 8384)"

printf "%-26s %s\n" \
    "Syncthing TCP:" \
    "$(listener_tcp 22000)"

printf "%-26s %s\n" \
    "Syncthing QUIC/UDP:" \
    "$(listener_udp 22000)"

printf "%-26s %s\n" \
    "Syncthing discovery:" \
    "$(listener_udp 21027)"

printf "%-26s %s\n" \
    "SearXNG:" \
    "$(listener_tcp 8080)"

printf "%-26s %s\n" \
    "nginx HTTP:" \
    "$(listener_tcp 80)"

printf "%-26s %s\n" \
    "nginx HTTPS:" \
    "$(listener_tcp 443)"


# ============================================================
# QUICK HEALTH SUMMARY
# ============================================================

section "QUICK HEALTH SUMMARY"

CRITICAL=0
WARNINGS=0


if [ -x "$HERMES_BIN" ]; then
    echo "✓ Hermes installed"
else
    echo "✗ Hermes missing"
    CRITICAL=$((CRITICAL + 1))
fi


if as_hermes \
    systemctl --user is-active syncthing.service \
    >/dev/null 2>&1; then

    echo "✓ Syncthing running"
else
    echo "✗ Syncthing not running"
    CRITICAL=$((CRITICAL + 1))
fi


if as_hermes \
    systemctl --user is-active hermes-gateway.service \
    >/dev/null 2>&1; then

    echo "✓ Hermes Gateway running"
else
    echo "⚠ Hermes Gateway not running"
    WARNINGS=$((WARNINGS + 1))
fi


if curl \
    --connect-timeout 2 \
    --max-time 4 \
    -fsS \
    -o /dev/null \
    "${SEARXNG_URL}/" \
    2>/dev/null; then

    echo "✓ SearXNG reachable"
else
    echo "⚠ SearXNG unavailable"
    WARNINGS=$((WARNINGS + 1))
fi


if curl \
    --connect-timeout 2 \
    --max-time 10 \
    -fsS \
    "${SEARXNG_URL}/search?q=test&format=json" \
    2>/dev/null \
    | jq -e '.results' \
    >/dev/null 2>&1; then

    echo "✓ SearXNG JSON API working"
else
    echo "⚠ SearXNG JSON API unavailable"
    WARNINGS=$((WARNINGS + 1))
fi


if [ -d "$VAULT_DIR" ]; then
    echo "✓ Vault present"
else
    echo "✗ Vault missing"
    CRITICAL=$((CRITICAL + 1))
fi


if git \
    -C "$DATA_DIR" \
    rev-parse \
    --is-inside-work-tree \
    >/dev/null 2>&1; then

    echo "✓ Brain Git repository initialized"
else
    echo "⚠ Brain Git repository not initialized"
    WARNINGS=$((WARNINGS + 1))
fi


if printf '%s\n' "$HERMES_DOCTOR" \
    | grep -Eqi \
        'OpenAI Codex auth.*logged in'; then

    echo "✓ OpenAI Codex authenticated"
else
    echo "⚠ OpenAI Codex auth not detected"
    WARNINGS=$((WARNINGS + 1))
fi


if [ "$MEMORY_PROVIDER" = "holographic" ] 2>/dev/null; then
    echo "✓ Holographic memory active"
else
    echo "⚠ Holographic memory not active"
    WARNINGS=$((WARNINGS + 1))
fi


if [ -n "$BROWSER_USE_VERSION" ]; then
    echo "✓ Browser Use installed"
else
    echo "⚠ Browser Use not detected"
    WARNINGS=$((WARNINGS + 1))
fi


if [ "$SWAP_TOTAL" -gt 0 ]; then
    echo "✓ Swap configured"
else
    echo "⚠ Swap disabled"
    WARNINGS=$((WARNINGS + 1))
fi


if [ -f /var/run/reboot-required ]; then
    echo "⚠ Reboot required"
    WARNINGS=$((WARNINGS + 1))
fi


if [ -n "$LATEST_KERNEL" ] \
    && [ "$(uname -r)" != "$LATEST_KERNEL" ]; then

    echo "⚠ Newer kernel installed: $LATEST_KERNEL"
    WARNINGS=$((WARNINGS + 1))
fi


echo
echo "Critical issues: $CRITICAL"
echo "Warnings:        $WARNINGS"

if [ "$CRITICAL" -eq 0 ]; then
    echo
    echo "Overall status:  OK"
else
    echo
    echo "Overall status:  NEEDS ATTENTION"
fi
