#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
owned_nodes
apply grafana
ready observability grafana
apply grafana-route
