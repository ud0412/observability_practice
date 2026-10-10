#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
OBSERVABILITY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
WSL_KUBERNETES_REPO="$(python3 "$OBSERVABILITY_ROOT/scripts/lib/foundation.py")"
export WSL_KUBERNETES_REPO
source "$WSL_KUBERNETES_REPO/scripts/lib/common.sh"
LAB_ROOT="$OBSERVABILITY_ROOT"
source "$LAB_ROOT/config/versions.env"
[[ ! -f "$LAB_ROOT/config/lab.env" ]] || source "$LAB_ROOT/config/lab.env"
[[ ${LAB_NAME:-} == observability-lab ]] || {
	echo 'Only observability-lab is supported' >&2
	exit 1
}
export GRAFANA_PORT="${GRAFANA_PORT:-8080}"
if [[ ! $GRAFANA_PORT =~ ^[0-9]+$ ]] || ((GRAFANA_PORT < 1024 || GRAFANA_PORT > 65535)); then
	echo 'Invalid Grafana port' >&2
	exit 1
fi
PYTHON_BIN="${PYTHON_BIN:-$LAB_ROOT/.venv/bin/python}"
[[ ! -x "$LAB_ROOT/.venv/bin/python" ]] || PYTHON_BIN="$LAB_ROOT/.venv/bin/python"
