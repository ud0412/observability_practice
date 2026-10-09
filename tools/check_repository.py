"""Portable source checks; no infrastructure deployment or secret-file reads."""
import json
from pathlib import Path
import re
import sys
import yaml

root = Path(__file__).resolve().parents[1]
errors = []
for file in list((root / "docs").glob("*.md")) + [root / "README.md", root / "samples/README.md"]:
    text = file.read_text(encoding="utf-8")
    if len(re.findall(r"^```", text, re.M)) % 2:
        errors.append(str(file) + ": unbalanced fence")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http:", "https:", "#")):
            continue
        resolved = file.parent / target.split("#")[0]
        if not resolved.exists(): errors.append(str(file) + ": missing " + target)
for folder in (root / "infrastructure", root / "samples/kubernetes"):
    for file in folder.rglob("*.yaml"):
        list(yaml.safe_load_all(file.read_text(encoding="utf-8")))
for folder in (root / "infrastructure/grafana/dashboards", root / "samples/observability/dashboards"):
    for file in folder.glob("*.json"):
        dashboard = json.loads(file.read_text(encoding="utf-8"))
        assert dashboard["uid"] and dashboard["panels"]
ignore = (root / ".gitignore").read_text().splitlines()
assert ".github_key" in ignore and "Plan.md" in ignore
frontend = (root / "samples/frontend/package.json").read_text()
assert not re.search(r"opentelemetry|faro", frontend, re.I)
for file in (root / "scripts").rglob("*.sh"):
    if file.name in ("setup-infrastructure.sh", "lab.sh") or file.parent.name == "steps":
        assert "samples/" not in file.read_text(), "Infrastructure entrypoint references samples"
if errors:
    sys.exit("\n".join(errors))
print("Markdown links, YAML, dashboard JSON, ignore rules and scope checks passed")
