#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
[[ $(uname -s) == Linux ]] || {
	echo 'Run inside WSL Linux.' >&2
	exit 1
}
for command in docker kind kubectl helm curl; do command -v "$command" >/dev/null || {
	echo "Missing tool: $command" >&2
	exit 1
}; done
"$PYTHON_BIN" -c 'import yaml' || {
	echo 'Install requirements-tools.txt in .venv.' >&2
	exit 1
}
docker info >/dev/null
runtime_name=$(docker info --format '{{.Name}} {{.OperatingSystem}}')
if [[ $runtime_name == *docker-desktop* || $runtime_name == *"Docker Desktop"* ]]; then
	echo 'The ownership checks in this lab require Docker Engine inside WSL.' >&2
	exit 1
fi
[[ $(kind version) == *"v$KIND_VERSION"* ]] || {
	echo "Use kind $KIND_VERSION from versions.env" >&2
	exit 1
}
[[ $(helm version --short) == v"$HELM_VERSION"* ]] || {
	echo "Use Helm $HELM_VERSION" >&2
	exit 1
}
memory_kb=$(awk '/MemTotal/{print $2}' /proc/meminfo)
((memory_kb >= 11000000)) || {
	echo 'Allocate at least 12GB to WSL; 16GB recommended.' >&2
	exit 1
}
echo 'Prerequisites OK. No cluster was created.'
