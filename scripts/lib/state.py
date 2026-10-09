"""Owned WSL state; no Kubernetes/Docker operations in this module."""
import json
import os
from pathlib import Path
import secrets
import shutil
import sys
import uuid

LAB_NAME = "observability-lab"


def state_path():
    home = Path.home()
    if os.name == "posix" and os.geteuid() == 0 and os.environ.get("SUDO_UID"):
        import pwd
        home = Path(pwd.getpwuid(int(os.environ["SUDO_UID"])).pw_dir)
    parent = home / ".local/share/observability-practice"
    path = Path(os.environ.get("LAB_STATE_DIR", str(parent / LAB_NAME))).expanduser()
    if not path.is_absolute() or path.name != LAB_NAME or path.parent != parent:
        raise ValueError("LAB_STATE_DIR must be the observability-lab directory under ~/.local/share/observability-practice")
    # Refuse aliases and links before mkdir or recursive deletion.
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError("State path contains a symlink")
    if path.resolve() != path:
        raise ValueError("State path is not canonical")
    return path


def check_owner(path):
    marker = path / "owner.json"
    if marker.is_symlink() or not marker.is_file():
        raise ValueError("Existing state has no valid ownership marker")
    owner = json.loads(marker.read_text())
    if owner.get("schema") != 1 or owner.get("lab") != LAB_NAME or owner.get("path") != str(path):
        raise ValueError("Ownership marker does not match this lab")
    uuid.UUID(owner["id"])
    # Don't follow any descendant symlink during runtime writes or deletion.
    for item in path.rglob("*"):
        if item.is_symlink():
            raise ValueError("State contains a symlink: " + str(item))
    return owner


def prepare():
    path = state_path()
    if path.exists():
        check_owner(path)
    else:
        path.mkdir(parents=True, mode=0o700)
        owner = {"schema": 1, "lab": LAB_NAME, "path": str(path), "id": str(uuid.uuid4())}
        (path / "owner.json").write_text(json.dumps(owner))
    for name in ["rendered", "exports", "logs", "tmp", "nodes/control-plane/alloy-node", "nodes/worker/alloy-node"]:
        (path / name).mkdir(parents=True, exist_ok=True)
    for name in ["seaweedfs", "mimir", "loki", "tempo", "alloy-central", "grafana"]:
        (path / "nodes/worker" / name).mkdir(exist_ok=True)
    credentials = path / "credentials.json"
    if not credentials.exists():
        credentials.write_text(json.dumps({
            "S3_ACCESS_KEY": "lab-" + secrets.token_hex(8),
            "S3_SECRET_KEY": secrets.token_hex(24),
            "GRAFANA_PASSWORD": secrets.token_urlsafe(24),
        }))
        credentials.chmod(0o600)
    return path


def destroy_data():
    path = state_path()
    if not path.exists():
        return
    check_owner(path)
    # Cluster ownership and absence must have been verified by the shell caller.
    # Keep the marker if a child cannot be deleted, so a privileged retry is possible.
    for child in path.iterdir():
        if child.name == "owner.json":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    (path / "owner.json").unlink()
    path.rmdir()
    if path.exists():
        raise RuntimeError("State directory remains")


if __name__ == "__main__":
    try:
        command = sys.argv[1]
        if command == "path":
            print(state_path())
        elif command == "prepare":
            print(prepare())
        elif command == "check":
            check_owner(state_path())
        elif command == "destroy-data":
            destroy_data()
        else:
            raise ValueError("Unknown state command")
    except (ValueError, OSError, KeyError) as error:
        sys.exit(str(error))
