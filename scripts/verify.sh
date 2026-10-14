#!/usr/bin/env bash
set -euo pipefail

# This file is intentionally project-specific and may be adapted for the app.
if [[ -f package.json ]]; then
  if [[ -f package-lock.json ]]; then
    npm ci --ignore-scripts
  else
    npm install --ignore-scripts
  fi
  npm test
elif [[ -f Cargo.toml ]]; then
  cargo test
elif [[ -f go.mod ]]; then
  go test ./...
elif [[ -f pyproject.toml || -f pytest.ini ]]; then
  python3 -m pip install pytest
  python3 -m pytest -q
elif [[ -d tests ]] && find tests -type f -name 'test*.py' | grep -q .; then
  python3 -m unittest discover -s tests -p 'test*.py' -v
else
  echo "No automatic tests detected. Add project tests and adapt scripts/verify.sh." >&2
  exit 2
fi
