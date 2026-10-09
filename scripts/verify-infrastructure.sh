#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
owned_state
owned_nodes
k wait --for=condition=Ready nodes --all --timeout=120s
for name in mimir loki tempo alloy-central grafana; do ready observability "$name"; done
ready storage seaweedfs
k -n observability rollout status daemonset/alloy-node --timeout=120s
k get pvc -A -o json | "$PYTHON_BIN" -c 'import json,sys; p=[x for x in json.load(sys.stdin)["items"] if x["metadata"]["namespace"] in ("storage","observability")]; assert len(p)==6 and all(x.get("status",{}).get("phase")=="Bound" for x in p), "Required PVCs are not Bound"'
k -n observability get httproute grafana -o json | "$PYTHON_BIN" -c 'import json,sys; d=json.load(sys.stdin); c=[c for p in d.get("status",{}).get("parents",[]) for c in p.get("conditions",[])]; assert any(x["type"]=="Accepted" and x["status"]=="True" for x in c) and any(x["type"]=="ResolvedRefs" and x["status"]=="True" for x in c), "Route is not accepted/resolved"'
echo 'Infrastructure readiness passed. S3 writes, telemetry queries and Pod recovery are separate documented acceptance checks.'
