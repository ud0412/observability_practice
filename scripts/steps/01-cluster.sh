#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
if kind get clusters | grep -qx "$LAB_NAME"; then
	owned_nodes
	kind export kubeconfig --name "$LAB_NAME" --kubeconfig "$KUBECONFIG"
else
	kind create cluster --name "$LAB_NAME" --config "$LAB_STATE_DIR/rendered/kind.yaml" --kubeconfig "$KUBECONFIG"
fi
# Cluster creation precedes CNI; nodes can be NotReady at this stage.
owned_nodes
