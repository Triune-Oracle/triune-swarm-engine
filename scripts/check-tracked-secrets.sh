#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

violations=()
shopt -s nocasematch

while IFS= read -r -d '' file; do
  case "$file" in
    .env|.env.*|*.env|*.pem|*.key|*.p12|*.pfx|*.jks|*id_rsa*|*secret*.env|*secrets*.json)
      if [[ "$file" != ".env.example" ]]; then
        violations+=("$file")
      fi
      ;;
  esac
done < <(git ls-files -z)

if [[ ${#violations[@]} -gt 0 ]]; then
  echo "❌ Secret guard failed: tracked secret-like files detected:"
  printf ' - %s\n' "${violations[@]}"
  exit 1
fi

echo "✅ Secret guard passed: no tracked secret-like files detected."
