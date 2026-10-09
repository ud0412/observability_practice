#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
owned_nodes
helm repo add cilium https://helm.cilium.io --force-update
helm repo update cilium
helm upgrade --install cilium cilium/cilium --version "$CILIUM_VERSION" --namespace kube-system --kube-context "kind-$LAB_NAME" --kubeconfig "$KUBECONFIG" -f "$LAB_ROOT/infrastructure/cilium/values.yaml" --wait --timeout 10m
k wait --for=condition=Ready nodes --all --timeout=300s
k -n kube-system rollout status daemonset/cilium --timeout=300s
