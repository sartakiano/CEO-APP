#!/usr/bin/env bash
# Instalador para VPS con IP fija autorizada por los ERP.
# Uso: sudo bash deploy/install.sh
set -euo pipefail

APP_DIR="/opt/ceo-app"
APP_USER="ceoapp"
REPO_SRC="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Creando usuario $APP_USER (si no existe)"
id -u "$APP_USER" >/dev/null 2>&1 || useradd --system --home "$APP_DIR" --shell /bin/bash "$APP_USER"

echo "==> Copiando codigo a $APP_DIR"
mkdir -p "$APP_DIR"
rsync -a --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude 'data/history/*' \
  "$REPO_SRC/" "$APP_DIR/"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

echo "==> Creando virtualenv"
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/.venv"
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

echo "==> Log file"
touch /var/log/ceo-app.log
chown "$APP_USER:$APP_USER" /var/log/ceo-app.log

echo "==> Instalando unidades systemd"
install -m 0644 "$REPO_SRC/deploy/ceo-app.service" /etc/systemd/system/ceo-app.service
install -m 0644 "$REPO_SRC/deploy/ceo-app.timer"   /etc/systemd/system/ceo-app.timer
systemctl daemon-reload
systemctl enable --now ceo-app.timer

echo
echo "Listo. Siguientes pasos manuales:"
echo "  1) Edita $APP_DIR/.env con las credenciales reales (cp .env.example .env primero)."
echo "  2) Prueba una corrida manual:  sudo systemctl start ceo-app.service && tail -f /var/log/ceo-app.log"
echo "  3) Verifica el timer:          systemctl list-timers ceo-app.timer"
