import asyncio
from datetime import datetime, timezone
import json
import logging
import os
from fastapi import FastAPI, HTTPException


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "service_name": "sample-fastapi",
            "message": record.getMessage(),
            "trace_id": getattr(record, "otelTraceID", ""),
            "span_id": getattr(record, "otelSpanID", ""),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


handler = logging.StreamHandler(__import__("sys").stdout)
handler.setFormatter(JsonFormatter())
logger = logging.getLogger("sample-fastapi")
logger.handlers = [handler]
logger.setLevel(logging.INFO)
logger.propagate = False
app = FastAPI()


@app.get("/test")
async def test_endpoint():
    logger.info("test request started")
    delay = int(os.environ.get("TEST_DELAY_MS", "0"))
    if delay:
        await asyncio.sleep(delay / 1000)
    if os.environ.get("TEST_FAILURE_MODE", "none") == "http500":
        logger.error("test request failed: deliberate HTTP 500")
        raise HTTPException(status_code=500, detail="deliberate lab failure")
    logger.info("test request completed")
    return {"service": "sample-fastapi", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
