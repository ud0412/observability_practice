import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lib"))
import state
spec = importlib.util.spec_from_file_location("lab_render", ROOT / "infrastructure/render.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


class StateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name).resolve()
        self.home_patch = patch.object(Path, "home", return_value=self.home)
        self.home_patch.start()
        self.env_patch = patch.dict(os.environ, {}, clear=False)
        self.env_patch.start()
        os.environ.pop("LAB_STATE_DIR", None)
        os.environ.pop("SUDO_UID", None)

    def tearDown(self):
        self.env_patch.stop()
        self.home_patch.stop()
        self.temp.cleanup()

    def test_prepare_preserves_keys_and_data(self):
        path = state.prepare()
        old = (path / "credentials.json").read_bytes()
        (path / "exports/student.json").write_text("dashboard")
        state.prepare()
        self.assertEqual(old, (path / "credentials.json").read_bytes())
        self.assertEqual("dashboard", (path / "exports/student.json").read_text())

    def test_forbidden_paths(self):
        for path in (self.home, ROOT, self.home / "other", Path("relative")):
            os.environ["LAB_STATE_DIR"] = str(path)
            with self.assertRaises(ValueError): state.state_path()

    def test_unowned_directory_is_not_deleted(self):
        path = state.state_path()
        path.mkdir(parents=True)
        (path / "unrelated").write_text("keep")
        with self.assertRaises(ValueError): state.destroy_data()
        self.assertTrue((path / "unrelated").exists())

    def test_wrong_owner_is_not_deleted(self):
        path = state.prepare()
        marker = json.loads((path / "owner.json").read_text())
        marker["lab"] = "another-lab"
        (path / "owner.json").write_text(json.dumps(marker))
        with self.assertRaises(ValueError): state.destroy_data()
        self.assertTrue(path.exists())

    def test_destroy_all_and_repeat(self):
        path = state.prepare()
        (path / "nodes/worker/grafana/db").write_bytes(b"saved dashboard")
        state.destroy_data()
        self.assertFalse(path.exists())
        state.destroy_data()

    def test_failed_delete_keeps_marker(self):
        path = state.prepare()
        with patch.object(state.shutil, "rmtree", side_effect=PermissionError("test")):
            with self.assertRaises(PermissionError): state.destroy_data()
        self.assertTrue((path / "owner.json").exists())

    def test_symlink_escape(self):
        path = state.prepare()
        target = self.home / "outside"
        target.mkdir()
        try:
            (path / "exports/escape").symlink_to(target, target_is_directory=True)
        except OSError:
            self.skipTest("Host does not allow symlink creation")
        with self.assertRaises(ValueError): state.check_owner(path)
        (path / "exports/escape").unlink()

    def test_render_contract(self):
        path = state.prepare()
        renderer.render()
        files = list((path / "rendered").glob("*.yaml"))
        docs = [item for file in files for item in yaml.safe_load_all(file.read_text())]
        self.assertEqual(6, sum(d["kind"] == "PersistentVolumeClaim" for d in docs))
        self.assertFalse(any(d.get("metadata", {}).get("namespace") == "sample-app" for d in docs))
        for d in docs:
            if d["kind"] == "PersistentVolume":
                self.assertTrue(d["spec"]["local"]["path"].startswith("/var/local/observability/"))
            if d["kind"] == "Deployment":
                self.assertEqual("Recreate", d["spec"]["strategy"]["type"])
        kind = yaml.safe_load((path / "rendered/kind.yaml").read_text())
        self.assertTrue(kind["networking"]["disableDefaultCNI"])
        self.assertEqual(2, len(kind["nodes"]))


if __name__ == "__main__": unittest.main()
