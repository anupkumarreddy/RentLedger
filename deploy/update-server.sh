#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script with sudo." >&2
    exit 1
fi

app_root="${RENTLEDGER_APP_ROOT:-/srv/apps/rentledger/current}"
venv_root="${RENTLEDGER_VENV_ROOT:-/srv/apps/rentledger/venv}"
env_file="${RENTLEDGER_ENV_FILE:-/etc/rentledger/rentledger.env}"

runuser -u rentledger -- git -C "$app_root" pull --ff-only origin main
runuser -u rentledger -- "$venv_root/bin/pip" install -r "$app_root/requirements.txt"

runuser -u rentledger -- bash -c "
    set -a
    source '$env_file'
    set +a
    cd '$app_root'
    '$venv_root/bin/python' manage.py migrate --noinput
    '$venv_root/bin/python' manage.py collectstatic --noinput
    '$venv_root/bin/python' manage.py check
"

install -m 0644 -o root -g root "$app_root/deploy/rentledger.service" /etc/systemd/system/rentledger.service
systemctl daemon-reload
nginx -t
systemctl restart rentledger
systemctl reload nginx

server_host="$(awk -F= '$1 == "DJANGO_ALLOWED_HOSTS" { split($2, hosts, ","); print hosts[1] }' "$env_file")"
curl --fail --silent --show-error --head -H "Host: $server_host" http://127.0.0.1/ >/dev/null
echo "RentLedger updated successfully."
