#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
owned_state
owned_nodes
pidfile="$LAB_STATE_DIR/port-forward.pid"
if [[ -f $pidfile ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
	echo 'A recorded access process exists. Run destroy to stop it, or check status.' >&2
	exit 1
fi
service_name=$(k -n envoy-gateway-system get service -l gateway.envoyproxy.io/owning-gateway-name=lab,gateway.envoyproxy.io/owning-gateway-namespace=envoy-gateway-system -o jsonpath='{.items[0].metadata.name}')
[[ -n $service_name ]] || {
	echo 'Envoy data-plane Service is missing.' >&2
	exit 1
}
kubectl --kubeconfig "$KUBECONFIG" --context "kind-$LAB_NAME" -n envoy-gateway-system port-forward --address 127.0.0.1 "service/$service_name" "$GRAFANA_PORT:80" >"$LAB_STATE_DIR/logs/port-forward.log" 2>&1 &
pid=$!
echo "$pid" >"$pidfile"
for attempt in {1..30}; do
	kill -0 "$pid" 2>/dev/null || {
		echo 'Port-forward failed; inspect its log.' >&2
		exit 1
	}
	if curl -fsS "http://localhost:$GRAFANA_PORT/grafana/api/health" >/dev/null; then
		echo "Grafana: http://localhost:$GRAFANA_PORT/grafana/ (admin)"
		exit 0
	fi
	sleep 1
done
echo 'Gateway access timed out; inspect Route status and the port-forward log.' >&2
exit 1
