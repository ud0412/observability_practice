#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
# Full teardown, including the prerequisite cluster, through its sole owner.
exec bash "$WSL_KUBERNETES_REPO/scripts/destroy-infrastructure.sh"
