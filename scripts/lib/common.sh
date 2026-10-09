#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
LAB_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
source "$LAB_ROOT/config/versions.env"
[[ ! -f "$LAB_ROOT/config/lab.env" ]] || source "$LAB_ROOT/config/lab.env"
[[ ${LAB_NAME:-observability-lab} == observability-lab ]] || {
	echo 'Only observability-lab is supported' >&2
	exit 1
}
export LAB_NAME=observability-lab GRAFANA_PORT="${GRAFANA_PORT:-8080}"
if [[ ! $GRAFANA_PORT =~ ^[0-9]+$ ]] || ((GRAFANA_PORT < 1024 || GRAFANA_PORT > 65535)); then
	echo 'Invalid Grafana port' >&2
	exit 1
fi
PYTHON_BIN="${PYTHON_BIN:-$LAB_ROOT/.venv/bin/python}"
[[ -x $PYTHON_BIN ]] || PYTHON_BIN=python3
LAB_STATE_DIR="$($PYTHON_BIN "$LAB_ROOT/scripts/lib/state.py" path)"
export LAB_STATE_DIR KUBECONFIG="$LAB_STATE_DIR/kubeconfig"
export KIND_EXPERIMENTAL_PROVIDER=docker
k() { kubectl --kubeconfig "$KUBECONFIG" --context "kind-$LAB_NAME" "$@"; }
owned_state() { "$PYTHON_BIN" "$LAB_ROOT/scripts/lib/state.py" check; }
ready() { k -n "$1" rollout status "deployment/$2" --timeout=450s; }
apply() { k apply -f "$LAB_STATE_DIR/rendered/$1.yaml"; }
# Before touching a cluster, check every node's kind label and exact owned bind mount.
owned_nodes() {
	local id role mount expected label nodes
	nodes=$(docker ps -aq --filter "label=io.x-k8s.kind.cluster=$LAB_NAME")
	while IFS= read -r id; do
		[[ -n $id ]] || continue
		label="$(docker inspect -f '{{index .Config.Labels "io.x-k8s.kind.cluster"}}' "$id")"
		[[ $label == "$LAB_NAME" ]] || return 1
		role="$(docker inspect -f '{{index .Config.Labels "io.x-k8s.kind.role"}}' "$id")"
		[[ $role == worker || $role == control-plane ]] || return 1
		expected="$LAB_STATE_DIR/nodes/$role"
		mount="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/var/local/observability"}}{{.Source}}{{end}}{{end}}' "$id")"
		[[ $mount == "$expected" ]] || {
			echo "Cluster ownership mismatch: $id" >&2
			return 1
		}
	done <<<"$nodes"
}
