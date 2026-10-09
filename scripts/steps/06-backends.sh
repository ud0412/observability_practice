#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
owned_nodes
for backend in mimir loki tempo; do
	apply "$backend"
	ready observability "$backend"
done
