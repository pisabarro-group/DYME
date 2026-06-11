#!/usr/bin/env bash
#Triggers a frontend update from main repo

REPO_URL="https://github.com/pisabarro-group/DYME.git"
FRONTEND_DIR="/dyme_base/frontend"

echo "[INFO] Updating frontend from GitHub..."
git clone --depth 1 --filter=blob:none --sparse "$REPO_URL" /tmp/dyme_repo
git -C /tmp/dyme_repo sparse-checkout set frontend
cp -R /tmp/dyme_repo/frontend/. "$FRONTEND_DIR/"
rm -rf /tmp/dyme_repo
chown -R www-data:www-data "$FRONTEND_DIR"
echo "[INFO] Frontend updated."