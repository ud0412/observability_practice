#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
# Check Docker even when state is missing: never report success with orphaned nodes.
docker info >/dev/null
node_ids=$(docker ps -aq --filter "label=io.x-k8s.kind.cluster=$LAB_NAME")
if [[ ! -d $LAB_STATE_DIR ]]; then
	[[ -z $node_ids ]] || {
		echo 'Cluster remains but its ownership marker is missing; refusing deletion.' >&2
		exit 1
	}
	echo 'No lab cluster or managed data remains.'
	exit 0
fi
owned_state
owned_nodes
pidfile="$LAB_STATE_DIR/port-forward.pid"
if [[ -f $pidfile ]]; then
	pid=$(cat "$pidfile")
	[[ $pid =~ ^[0-9]+$ ]] || {
		echo 'Invalid recorded PID' >&2
		exit 1
	}
	if kill -0 "$pid" 2>/dev/null; then
		[[ -r /proc/$pid/cmdline ]] || {
			echo 'Cannot inspect access process' >&2
			exit 1
		}
		cmdline=$(tr '\0' ' ' <"/proc/$pid/cmdline")
		[[ $cmdline == *"$KUBECONFIG"* && $cmdline == *port-forward* ]] || {
			echo 'PID ownership mismatch; refusing to stop it.' >&2
			exit 1
		}
		kill "$pid"
		for attempt in {1..10}; do
			kill -0 "$pid" 2>/dev/null || break
			sleep 1
		done
		kill -0 "$pid" 2>/dev/null && {
			echo 'Access process remains' >&2
			exit 1
		}
	fi
fi
if [[ -n $node_ids ]]; then kind delete cluster --name "$LAB_NAME" --kubeconfig "$KUBECONFIG"; fi
[[ -z $(docker ps -aq --filter "label=io.x-k8s.kind.cluster=$LAB_NAME") ]] || {
	echo 'Lab node containers remain' >&2
	exit 1
}
# Root-owned files created inside local PVs need root deletion. Only the validated tree is removed.
"$PYTHON_BIN" "$LAB_ROOT/scripts/lib/state.py" check
if [[ -w $LAB_STATE_DIR/nodes/worker ]]; then
	if ! "$PYTHON_BIN" "$LAB_ROOT/scripts/lib/state.py" destroy-data; then
		sudo --preserve-env=LAB_STATE_DIR "$PYTHON_BIN" "$LAB_ROOT/scripts/lib/state.py" destroy-data
	fi
else
	sudo --preserve-env=LAB_STATE_DIR "$PYTHON_BIN" "$LAB_ROOT/scripts/lib/state.py" destroy-data
fi
[[ ! -e $LAB_STATE_DIR ]] || {
	echo 'Lab data remains' >&2
	exit 1
}
echo 'Destroyed lab cluster, telemetry, S3/WAL files, Grafana DB, exports and generated credentials.'
