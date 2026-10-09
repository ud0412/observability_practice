"""Lock installed FastAPI runtime dependencies after installing requirements.txt."""
import importlib.metadata as metadata
from pathlib import Path
from packaging.requirements import Requirement

root = Path(__file__).resolve().parents[1]
pending = [Requirement(line).name for line in (root / "samples/fastapi/requirements.txt").read_text().splitlines() if line]
seen = {}
while pending:
    distribution = metadata.distribution(pending.pop())
    name = distribution.metadata["Name"]
    if name.lower() in seen:
        continue
    seen[name.lower()] = (name, distribution.version)
    for dependency in distribution.requires or []:
        requirement = Requirement(dependency)
        if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
            pending.append(requirement.name)
destination = root / "samples/fastapi/requirements.lock"
destination.write_text("\n".join(name + "==" + version for _, (name, version) in sorted(seen.items())) + "\n", encoding="utf-8")
print("Locked", len(seen), "runtime distributions")
