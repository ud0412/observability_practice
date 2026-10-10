import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prerequisite", ROOT / "scripts/lib/foundation.py")
prerequisite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prerequisite)


class IntegrationSourceTests(unittest.TestCase):
    def test_missing_or_incompatible_prerequisite_is_refused(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"WSL_KUBERNETES_REPO": temp}):
            with self.assertRaises(ValueError): prerequisite.foundation_root()
            path = Path(temp) / "config"
            path.mkdir()
            (path / "contract.json").write_text('{"schema": 99}')
            with self.assertRaises(ValueError): prerequisite.foundation_root()

    def test_trace_click_preserves_the_row_trace_id(self):
        url = (ROOT / "samples/observability/trace-explore-link.txt").read_text().strip()
        token = '${__data.fields["Trace ID"]}'
        self.assertIn(token, url)
        trace_id = "a" * 32
        state = json.loads(parse_qs(urlsplit(url.replace(token, trace_id)).query)["panes"][0])
        query = state["left"]["queries"][0]
        self.assertEqual("tempo", state["left"]["datasource"])
        self.assertEqual("traceql", query["queryType"])
        self.assertEqual(trace_id, query["query"])


if __name__ == "__main__": unittest.main()
