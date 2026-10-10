#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
bash "$WSL_KUBERNETES_REPO/scripts/preflight.sh"
"$PYTHON_BIN" -c 'import yaml'
bash "$WSL_KUBERNETES_REPO/scripts/verify-foundation.sh" --check
echo 'Ready to add Observability to the prerequisite cluster.'
