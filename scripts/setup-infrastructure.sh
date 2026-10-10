#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
trap 'echo "Setup failed at line $LINENO. Inspect the failed component; rerun up after correction." >&2' ERR
bash "$LAB_ROOT/scripts/lab.sh" prepare
for stage in "$LAB_ROOT"/scripts/steps/*.sh; do
	echo "Running $(basename "$stage")"
	bash "$stage"
done
bash "$LAB_ROOT/scripts/verify-infrastructure.sh"
echo 'Infrastructure ready. Run: bash scripts/lab.sh access'
echo 'Grafana admin password: read credentials.json locally; do not publish it.'
