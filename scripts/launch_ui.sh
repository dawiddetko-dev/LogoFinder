#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed."
  exit 1
fi

if [[ ! -f .env ]]; then
  if [[ -f .env.example ]]; then
    cp .env.example .env
    echo "Created .env from .env.example"
    echo "Please update .env with your Azure values before first successful run."
  else
    echo "Error: .env not found and .env.example is missing."
    exit 1
  fi
fi

if [[ ! -d .venv ]]; then
  echo "Creating virtual environment in .venv"
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing/updating Python dependencies"
pip install -r requirements.txt

get_env_value() {
  local key="$1"
  awk -v target="$key" '
    BEGIN { FS = "=" }
    {
      if ($0 ~ /^[[:space:]]*#/ || $0 ~ /^[[:space:]]*$/) {
        next
      }

      line = $0
      split(line, parts, "=")
      k = parts[1]
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", k)

      if (k == target) {
        sub(/^[^=]*=/, "", line)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", line)

        if ((line ~ /^".*"$/) || (line ~ /^\047.*\047$/)) {
          line = substr(line, 2, length(line) - 2)
        }

        print line
        exit
      }
    }
  ' .env
}

check_required() {
  local missing=()
  for var_name in "$@"; do
    local value
    value="$(get_env_value "$var_name")"
    if [[ -z "$value" ]]; then
      missing+=("$var_name")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    echo "Error: Missing required .env variables:"
    printf ' - %s\n' "${missing[@]}"
    exit 1
  fi
}

check_not_placeholder() {
  local invalid=()
  for var_name in "$@"; do
    local value
    value="$(get_env_value "$var_name")"
    if printf '%s' "$value" | grep -Eq '<[^>]+>'; then
      invalid+=("$var_name")
    fi
  done

  if [[ ${#invalid[@]} -gt 0 ]]; then
    echo "Error: Placeholder values detected in .env:"
    printf ' - %s\n' "${invalid[@]}"
    echo "Update these values with real Azure endpoints/keys and run again."
    exit 1
  fi
}

check_required CONTENT_UNDERSTANDING_ENDPOINT CONTENT_UNDERSTANDING_API_KEY CONTENT_UNDERSTANDING_ANALYZER_ID
check_not_placeholder CONTENT_UNDERSTANDING_ENDPOINT

echo "Starting UI"
PYTHONPATH=src streamlit run ui/app.py
