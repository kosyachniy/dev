#!/usr/bin/env bash

set -u

line() {
    echo "========================================"
}

check() {
    local name="$1"
    local binary="$2"
    shift 2

    printf "%-22s " "$name"

    if command -v "$binary" >/dev/null 2>&1; then
        "$binary" "$@" 2>&1 | head -1
    else
        echo "NOT INSTALLED"
    fi
}

human_bytes() {
    numfmt --to=iec --suffix=B "$1" 2>/dev/null || echo "$1 bytes"
}

# ============================================================
# SYSTEM
# ============================================================

line
echo " SYSTEM"
line

if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS:             ${PRETTY_NAME}"
fi

echo "Kernel:         $(uname -r)"
echo "Architecture:   $(uname -m)"
echo "Hostname:       $(hostname)"

if command -v timedatectl >/dev/null 2>&1; then
    timezone="$(timedatectl show -p Timezone --value 2>/dev/null || true)"
    [ -n "$timezone" ] && echo "Timezone:       $timezone"
fi

echo

# ============================================================
# CURRENT USER
# ============================================================

line
echo " CURRENT USER"
line

CURRENT_USER="$(id -un)"
CURRENT_UID="$(id -u)"
CURRENT_GID="$(id -g)"
CURRENT_GROUP="$(id -gn)"
GROUPS="$(id -nG)"

echo "User:           $CURRENT_USER"
echo "UID:            $CURRENT_UID"
echo "Primary group:  $CURRENT_GROUP ($CURRENT_GID)"
echo "Groups:         $GROUPS"

if [ "$CURRENT_UID" -eq 0 ]; then
    echo "Root:           YES"
else
    echo "Root:           NO"
fi

if command -v sudo >/dev/null 2>&1; then
    if sudo -n true >/dev/null 2>&1; then
        echo "Passwordless sudo: YES"
    elif id -nG | tr ' ' '\n' | grep -qx sudo; then
        echo "Sudo group:     YES"
        echo "Passwordless sudo: NO"
    else
        echo "Sudo group:     NO"
        echo "Passwordless sudo: NO"
    fi
else
    echo "sudo:           NOT INSTALLED"
fi

echo

# ============================================================
# HARDWARE / VPS RESOURCES
# ============================================================

line
echo " VPS RESOURCES"
line

CPU_MODEL="$(lscpu 2>/dev/null | sed -n 's/^Model name:[[:space:]]*//p' | head -1)"
CPU_LOGICAL="$(nproc)"
CPU_CORES="$(lscpu 2>/dev/null | awk -F: '/^Core\(s\) per socket:/ {gsub(/ /,"",$2); cores=$2} /^Socket\(s\):/ {gsub(/ /,"",$2); sockets=$2} END {if (cores && sockets) print cores*sockets}')"
CPU_SOCKETS="$(lscpu 2>/dev/null | awk -F: '/^Socket\(s\):/ {gsub(/ /,"",$2); print $2}')"

echo "CPU model:      ${CPU_MODEL:-unknown}"
echo "Logical CPUs:   ${CPU_LOGICAL}"

[ -n "${CPU_CORES:-}" ] &&
    echo "Physical cores: ${CPU_CORES}"

[ -n "${CPU_SOCKETS:-}" ] &&
    echo "CPU sockets:    ${CPU_SOCKETS}"

CPU_MAX_MHZ="$(lscpu 2>/dev/null | sed -n 's/^CPU max MHz:[[:space:]]*//p' | head -1)"

if [ -n "$CPU_MAX_MHZ" ]; then
    echo "CPU max MHz:    $CPU_MAX_MHZ"
fi

TOTAL_RAM_KB="$(awk '/MemTotal:/ {print $2}' /proc/meminfo)"
TOTAL_RAM_BYTES=$((TOTAL_RAM_KB * 1024))

echo "RAM total:      $(human_bytes "$TOTAL_RAM_BYTES")"

SWAP_TOTAL_KB="$(awk '/SwapTotal:/ {print $2}' /proc/meminfo)"
SWAP_TOTAL_BYTES=$((SWAP_TOTAL_KB * 1024))

echo "Swap total:     $(human_bytes "$SWAP_TOTAL_BYTES")"

ROOT_TOTAL_BYTES="$(df -B1 --output=size / | tail -1 | tr -d ' ')"
echo "Disk / total:   $(human_bytes "$ROOT_TOTAL_BYTES")"

echo

# ============================================================
# IMPORTANT RUNTIMES / PACKAGE MANAGERS
# ============================================================

line
echo " IMPORTANT RUNTIMES & TOOLS"
line

check "Python"       python3   --version
check "uv"           uv        --version

echo

check "Node.js"      node      --version
check "npm"          npm       --version
check "npx"          npx       --version
check "pnpm"         pnpm      --version
check "Corepack"     corepack  --version

echo

check "Git"          git       --version
check "GitHub CLI"   gh        --version

echo

# Tools installed outside normal APT package visibility
check "Obsidian CLI" ob        --version
check "Hermes"       hermes    version
check "Syncthing" syncthing --version
check "FFmpeg" ffmpeg -version
check "Docker"       docker    --version
check "Docker Compose" docker  compose version

echo

# ============================================================
# MANUALLY INSTALLED / MARKED APT PACKAGES
# ============================================================

line
echo " MANUAL APT PACKAGES"
line

while read -r pkg; do
    # Python runtime is shown once above.
    # Internal Python packages/libraries are noise here.
    case "$pkg" in
        python|python-*|python3|python3-*|libpython*)
            continue
            ;;
    esac

    dpkg-query -W \
        -f='${binary:Package}\t${Version}\n' \
        "$pkg" 2>/dev/null

done < <(apt-mark showmanual | sort)

echo

# ============================================================
# ACTUAL APT COMMAND HISTORY
# ============================================================

line
echo " APT INSTALL COMMAND HISTORY"
line

APT_HISTORY="$(
    zgrep -h '^Commandline:' /var/log/apt/history.log* 2>/dev/null \
    | grep -E '(^| )(apt|apt-get)( |$)' \
    | grep -E ' install( |$)' \
    || true
)"

if [ -n "$APT_HISTORY" ]; then
    echo "$APT_HISTORY"
else
    echo "No apt install commands found in available history"
fi

echo

# ============================================================
# UV TOOLS
# ============================================================

line
echo " UV TOOLS"
line

if command -v uv >/dev/null 2>&1; then
    UV_TOOLS="$(uv tool list 2>/dev/null || true)"

    if [ -n "$UV_TOOLS" ]; then
        echo "$UV_TOOLS"
    else
        echo "No uv tools installed"
    fi
else
    echo "uv NOT INSTALLED"
fi

echo

# ============================================================
# GLOBAL NPM PACKAGES
# ============================================================

line
echo " GLOBAL NPM PACKAGES"
line

if command -v npm >/dev/null 2>&1; then
    npm list -g --depth=0 2>/dev/null || true
else
    echo "npm NOT INSTALLED"
fi

echo

# ============================================================
# SNAP
# ============================================================

line
echo " SNAP PACKAGES"
line

if command -v snap >/dev/null 2>&1; then
    SNAP_LIST="$(snap list 2>/dev/null || true)"

    if [ -n "$SNAP_LIST" ]; then
        echo "$SNAP_LIST"
    else
        echo "No snaps installed"
    fi
else
    echo "snap NOT INSTALLED"
fi
