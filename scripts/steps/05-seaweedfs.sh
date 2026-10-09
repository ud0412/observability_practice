#!/usr/bin/env bash
source "$(dirname "$0")/../lib/common.sh"
owned_state
owned_nodes
apply seaweedfs
ready storage seaweedfs
