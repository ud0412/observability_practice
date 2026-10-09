#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
owned_nodes
helm upgrade --install eg oci://docker.io/envoyproxy/gateway-helm --version "v$ENVOY_GATEWAY_VERSION" --namespace envoy-gateway-system --create-namespace --kube-context "kind-$LAB_NAME" --kubeconfig "$KUBECONFIG" -f "$LAB_ROOT/infrastructure/envoy-gateway/values.yaml" --wait --timeout 10m
k wait --for=condition=Established crd/gateways.gateway.networking.k8s.io --timeout=120s
apply gateway
k -n envoy-gateway-system wait --for=condition=Accepted gateway/lab --timeout=180s
