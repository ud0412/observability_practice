#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
owned_nodes
apply alloy
ready observability alloy-central
k -n observability rollout status daemonset/alloy-node --timeout=300s
