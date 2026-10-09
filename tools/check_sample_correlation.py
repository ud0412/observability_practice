"""Run source-level sample integration with a local OTLP test receiver.

Does not create a container, Kubernetes cluster, Grafana, or storage backend.
Run with the FastAPI test environment, a built jar, JDK and downloaded agent.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.request import Request, urlopen
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--agent", type=Path, required=True)
parser.add_argument("--jar", type=Path, default=ROOT / "samples/spring-boot/target/sample-spring-boot-1.0.0.jar")
args = parser.parse_args()
spans, metrics = [], []


class Receiver(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        if self.path == "/v1/traces":
            request = ExportTraceServiceRequest.FromString(body)
            for resource in request.resource_spans:
                service = next(a.value.string_value for a in resource.resource.attributes if a.key == "service.name")
                for scope in resource.scope_spans:
                    spans.extend((service, span) for span in scope.spans)
        elif self.path == "/v1/metrics":
            request = ExportMetricsServiceRequest.FromString(body)
            for resource in request.resource_metrics:
                service = next(a.value.string_value for a in resource.resource.attributes if a.key == "service.name")
                for scope in resource.scope_metrics:
                    metrics.extend((service, metric) for metric in scope.metrics)
        self.send_response(200)
        self.send_header("Content-Type", "application/x-protobuf")
        self.end_headers()
    def log_message(self, *_): pass


def port():
    with socket.socket() as handle:
        handle.bind(("127.0.0.1", 0))
        return handle.getsockname()[1]


def wait_health(url, process):
    for _ in range(300):
        if process.poll() is not None:
            raise RuntimeError("Sample exited before readiness")
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200: return
        except OSError: pass
        time.sleep(0.1)
    raise TimeoutError(url)


receiver = ThreadingHTTPServer(("127.0.0.1", 0), Receiver)
threading.Thread(target=receiver.serve_forever, daemon=True).start()
fast_port, spring_port = port(), port()
processes = []
with tempfile.TemporaryDirectory() as folder:
    handles = []
    try:
        common = os.environ.copy()
        common.update(OTEL_EXPORTER_OTLP_ENDPOINT=f"http://127.0.0.1:{receiver.server_port}",
                      OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf", OTEL_TRACES_EXPORTER="otlp",
                      OTEL_METRICS_EXPORTER="otlp", OTEL_LOGS_EXPORTER="none",
                      OTEL_TRACES_SAMPLER="parentbased_always_on", OTEL_METRIC_EXPORT_INTERVAL="1000",
                      OTEL_BSP_SCHEDULE_DELAY="100", OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE="cumulative")
        fast_env = dict(common, OTEL_SERVICE_NAME="sample-fastapi", OTEL_PYTHON_LOG_CORRELATION="true",
                        OTEL_PYTHON_LOG_AUTO_INSTRUMENTATION="false", OTEL_SEMCONV_STABILITY_OPT_IN="http",
                        TEST_DELAY_MS="0", TEST_FAILURE_MODE="none")
        fast_log = Path(folder) / "fastapi.log"
        java_log = Path(folder) / "spring.log"
        for command, cwd, env, logfile in [
            ([sys.executable, "-c",
              "from opentelemetry.instrumentation.auto_instrumentation import initialize; initialize(); "
              f"import uvicorn; uvicorn.run('app.main:app', host='127.0.0.1', port={fast_port})"],
             ROOT / "samples/fastapi", fast_env, fast_log),
            (["java", "-javaagent:" + str(args.agent.resolve()), "-jar", str(args.jar.resolve()),
              "--server.address=127.0.0.1", "--server.port=" + str(spring_port)], ROOT,
             dict(common, OTEL_SERVICE_NAME="sample-spring-boot", DOWNSTREAM_URL=f"http://127.0.0.1:{fast_port}/test"), java_log)]:
            handle = logfile.open("w", encoding="utf-8")
            handles.append(handle)
            processes.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=handle, stderr=subprocess.STDOUT,
                                              creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0))
        wait_health(f"http://127.0.0.1:{fast_port}/health", processes[0])
        wait_health(f"http://127.0.0.1:{spring_port}/health", processes[1])
        trace_id = "8d29c1732e4a4c4795d1cd83e6e490ab"
        request = Request(f"http://127.0.0.1:{spring_port}/test", headers={"traceparent": f"00-{trace_id}-19ae342f8641a91c-01"})
        with urlopen(request) as response: assert response.status == 200
        time.sleep(3)
        contexts = {}
        for service, logfile in [("sample-spring-boot", java_log), ("sample-fastapi", fast_log)]:
            lines = [json.loads(line) for line in logfile.read_text(encoding="utf-8").splitlines() if line.startswith("{")]
            matched = [line for line in lines if line.get("message", "").startswith("test request")]
            assert matched, f"No business JSON log for {service}"
            assert all(line.get("trace_id") == trace_id for line in matched), f"Missing log context: {service}"
            contexts[service] = matched[0]["span_id"]
        assert contexts["sample-spring-boot"] != contexts["sample-fastapi"]
        traced = [(service, span) for service, span in spans if span.trace_id.hex() == trace_id]
        assert {service for service, _ in traced} == {"sample-spring-boot", "sample-fastapi"}
        assert len(traced) >= 3
        span_ids = {span.span_id for _, span in traced}
        assert any(span.parent_span_id in span_ids for service, span in traced if service == "sample-fastapi")
        contract = {}
        for service in contexts:
            duration = [m for s, m in metrics if s == service and m.name == "http.server.request.duration"]
            assert duration, f"HTTP metric missing: {service}"
            histogram = duration[-1].histogram
            assert histogram.aggregation_temporality == 2, "Expected cumulative temporality"
            contract[service] = {"name": duration[-1].name, "unit": duration[-1].unit,
                                 "attribute_keys": sorted({a.key for dp in histogram.data_points for a in dp.attributes}),
                                 "temporality": "cumulative"}
        print(json.dumps({"log_context": "same trace_id, different span_id", "trace_spans": len(traced),
                          "http_metrics": contract}, indent=2))
    except Exception:
        for logfile in (fast_log, java_log):
            if logfile.exists():
                print(logfile.name + " tail:\n" + "\n".join(logfile.read_text(encoding="utf-8").splitlines()[-18:]), file=sys.stderr)
        raise
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
        for handle in handles: handle.close()
        receiver.shutdown()
        receiver.server_close()
