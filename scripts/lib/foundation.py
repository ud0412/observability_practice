"""Resolve the checked prerequisite checkout; no network or cluster operations."""
import json
import os
from pathlib import Path

def foundation_root():
    root = Path(__file__).resolve().parents[2]
    path = Path(os.environ.get("WSL_KUBERNETES_REPO", str(root.parent / "wsl_kubernetes_practice"))).expanduser().resolve()
    contract = path / "config/contract.json"
    if not contract.is_file():
        raise ValueError("Clone wsl_kubernetes_practice beside this repo, or set WSL_KUBERNETES_REPO to its absolute path.")
    data = json.loads(contract.read_text())
    if data != {"schema": 1, "cluster": "observability-lab", "context": "kind-observability-lab", "mount": "/var/local/observability"}:
        raise ValueError("Unsupported wsl_kubernetes_practice contract")
    for name in ("scripts/lib/state.py", "scripts/lib/common.sh", "scripts/verify-foundation.sh", "scripts/destroy-infrastructure.sh"):
        if not (path / name).is_file(): raise ValueError("Incomplete prerequisite checkout: " + name)
    def versions(file):
        return dict(line.split("=", 1) for line in file.read_text(encoding="utf-8").splitlines()
                    if line and not line.startswith("#"))
    expected = versions(root / "config/versions.env")
    installed = versions(path / "config/versions.env")
    for key in ("KIND_VERSION", "KUBERNETES_VERSION", "KIND_NODE_IMAGE", "HELM_VERSION",
                "CILIUM_VERSION", "ENVOY_GATEWAY_VERSION", "GATEWAY_API_VERSION"):
        if installed.get(key) != expected.get(key):
            raise ValueError("Prerequisite version mismatch: " + key + "; use the compatible foundation revision")
    return path

if __name__ == "__main__":
    try: print(foundation_root())
    except (ValueError, OSError) as error: raise SystemExit(str(error))
