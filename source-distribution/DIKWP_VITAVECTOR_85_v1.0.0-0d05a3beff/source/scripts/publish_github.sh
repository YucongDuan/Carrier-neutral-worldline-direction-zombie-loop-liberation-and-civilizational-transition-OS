#!/usr/bin/env bash
set -euo pipefail
OWNER=${1:?owner required}
REPO=${2:-DIKWP-VITAVECTOR-85}
python run.py selftest
python tools/static_audit.py
if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  git remote remove origin >/dev/null 2>&1 || true
  git remote add origin "https://github.com/$OWNER/$REPO.git"
else
  gh repo create "$OWNER/$REPO" --public --description "Carrier-neutral worldline direction and zombie-loop liberation OS" --source . --remote origin
fi
git add .
git commit -m "Release VITAVECTOR-85 v1.0.0" || true
git branch -M main
git push -u origin main
git tag -f v1.0.0
git push origin v1.0.0 --force
gh release create v1.0.0 --title "VITAVECTOR-85 v1.0.0" --notes-file CHANGELOG.md || true
