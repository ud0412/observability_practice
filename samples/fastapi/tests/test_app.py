import json
import logging
from fastapi.testclient import TestClient
from app.main import app, JsonFormatter


def test_success(monkeypatch):
    monkeypatch.setenv("TEST_DELAY_MS", "0")
    monkeypatch.setenv("TEST_FAILURE_MODE", "none")
    assert TestClient(app).get("/test").json()["status"] == "ok"


def test_failure(monkeypatch):
    monkeypatch.setenv("TEST_FAILURE_MODE", "http500")
    assert TestClient(app).get("/test").status_code == 500


def test_json_context_and_startup_fallback():
    record = logging.LogRecord("sample", logging.INFO, "", 0, "message", (), None)
    assert json.loads(JsonFormatter().format(record))["trace_id"] == ""
    record.otelTraceID = "8d29c1732e4a4c4795d1cd83e6e490ab"
    record.otelSpanID = "19ae342f8641a91c"
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["trace_id"] == record.otelTraceID
    assert parsed["span_id"] == record.otelSpanID
