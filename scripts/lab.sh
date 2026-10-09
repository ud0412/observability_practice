#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
command="${1:-help}"
case "$command" in
prepare)
	"$PYTHON_BIN" "$LAB_ROOT/scripts/lib/state.py" prepare >/dev/null
	"$PYTHON_BIN" "$LAB_ROOT/infrastructure/render.py"
	;;
up) bash "$LAB_ROOT/scripts/setup-infrastructure.sh" ;;
status)
	owned_state
	docker info >/dev/null
	owned_nodes
	k get nodes
	k get pods,pvc -A
	;;
access) bash "$LAB_ROOT/scripts/access-grafana.sh" ;;
verify) bash "$LAB_ROOT/scripts/verify-infrastructure.sh" ;;
destroy) bash "$LAB_ROOT/scripts/destroy-infrastructure.sh" ;;
*) echo 'Usage: bash scripts/lab.sh prepare|up|status|access|verify|destroy' ;;
esac
