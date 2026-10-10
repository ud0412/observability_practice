#!/usr/bin/env bash
source "$(dirname "$0")/lib/common.sh"
exec bash "$WSL_KUBERNETES_REPO/scripts/install-tools.sh"
