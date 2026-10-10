"""Compatibility facade: ownership and deletion live in wsl_kubernetes_practice."""
import importlib.util
import runpy
import sys
from foundation import foundation_root
file = foundation_root() / "scripts/lib/state.py"
if __name__ == "__main__":
    runpy.run_path(str(file), run_name="__main__")
else:
    spec = importlib.util.spec_from_file_location("foundation_state", file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    sys.modules[__name__] = module
