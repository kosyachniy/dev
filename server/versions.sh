#!/usr/bin/env bash

set -u

line() {
    echo "========================================"
}

check() {
    local name="$1"
    local binary="$2"
    shift 2

    printf "%-20s " "$name"

    if command -v "$binary" >/dev/null 2>&1; then
        "$binary" "$@" 2>&1 | head -1
    else
        echo "NOT INSTALLED"
    fi
}

line
echo " SYSTEM"
line

if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "OS:           ${PRETTY_NAME}"
fi

echo "Kernel:       $(uname -r)"
echo "Architecture: $(dpkg --print-architecture)"
echo "Hostname:     $(hostname)"

if command -v timedatectl >/dev/null 2>&1; then
    timezone="$(timedatectl show -p Timezone --value 2>/dev/null || true)"
    [ -n "$timezone" ] && echo "Timezone:     $timezone"
fi

echo

line
echo " RUNTIMES & PACKAGE MANAGERS"
line

check "Python"      python3       --version
check "uv"          uv            --version

echo

check "Node.js"     node          --version
check "npm"         npm           --version
check "npx"         npx           --version
check "pnpm"        pnpm          --version
check "Corepack"    corepack      --version

echo

line
echo " MAIN SOFTWARE"
line

check "Git"             git        --version
check "GitHub CLI"      gh         --version
check "curl"            curl       --version
check "wget"            wget       --version
check "jq"              jq         --version
check "ripgrep"         rg         --version
check "SQLite"          sqlite3    --version
check "GCC"             gcc        --version
check "Make"            make       --version
check "rsync"           rsync      --version
check "SSH"             ssh        -V
check "nginx"           nginx      -v
check "tmux"            tmux       -V
check "mkcert"          mkcert     --version
check "Docker"          docker     --version
check "Docker Compose"  docker     compose version

echo

line
echo " UV TOOLS"
line

if command -v uv >/dev/null 2>&1; then
    tools="$(uv tool list 2>/dev/null || true)"

    if [ -n "$tools" ]; then
        echo "$tools"
    else
        echo "No uv tools installed"
    fi
else
    echo "uv NOT INSTALLED"
fi

echo

line
echo " MANUALLY INSTALLED APT PACKAGES"
line

while read -r pkg; do
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

line
echo " GLOBAL NPM PACKAGES"
line

if command -v npm >/dev/null 2>&1; then
    npm list -g --depth=0 2>/dev/null || true
else
    echo "npm NOT INSTALLED"
fi

echo

line
echo " SNAP PACKAGES"
line

if command -v snap >/dev/null 2>&1; then
    snaps="$(snap list 2>/dev/null || true)"

    if [ -n "$snaps" ]; then
        echo "$snaps"
    else
        echo "No snaps installed"
    fi
else
    echo "snap NOT INSTALLED"
fi
