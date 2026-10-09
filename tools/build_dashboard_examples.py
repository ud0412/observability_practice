"""Author the reference classic-dashboard JSON; never installs/provisions it."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def variable(name, query, current):
    return {"name": name, "type": "query", "datasource": {"type": "prometheus", "uid": "mimir"},
            "query": query, "refresh": 1, "current": {"text": current, "value": current},
            "multi": False, "includeAll": False}


def panel(index, title, query, kind="timeseries", unit="short", datasource="mimir"):
    type_name = "loki" if datasource == "loki" else "prometheus"
    result = {"id": index, "title": title, "type": kind,
              "datasource": {"type": type_name, "uid": datasource},
              "gridPos": {"x": 12 * ((index - 1) % 2), "y": 8 * ((index - 1) // 2), "w": 12, "h": 8},
              "targets": [{"refId": "A", "expr": query, "datasource": {"type": type_name, "uid": datasource}}],
              "fieldConfig": {"defaults": {"unit": unit}, "overrides": []}, "options": {}}
    if kind == "logs":
        result["options"] = {"showTime": True, "showLabels": False, "wrapLogMessage": True, "sortOrder": "Descending"}
    return result


def save(file, uid, title, variables, panels):
    file.parent.mkdir(parents=True, exist_ok=True)
    dashboard = {"id": None, "uid": uid, "title": title, "schemaVersion": 41, "version": 1,
                 "tags": ["practice"], "timezone": "browser", "editable": True, "refresh": "30s",
                 "time": {"from": "now-15m", "to": "now"}, "templating": {"list": variables}, "panels": panels}
    file.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


infra_filter = 'cluster="$cluster",node=~"$node"'
save(ROOT / "infrastructure/grafana/dashboards/infrastructure.json", "lab-infra-example", "Lab Infrastructure Example", [
    variable("cluster", "label_values(node_cpu_seconds_total, cluster)", "observability-lab"),
    variable("node", 'label_values(node_cpu_seconds_total{cluster="$cluster"}, node)', "observability-lab-worker")], [
    panel(1, "CPU usage", f'100 * (1 - avg by(node)(rate(node_cpu_seconds_total{{{infra_filter},mode="idle"}}[5m])))', unit="percent"),
    panel(2, "Memory usage", f'100 * (1 - node_memory_MemAvailable_bytes{{{infra_filter}}}/node_memory_MemTotal_bytes{{{infra_filter}}})', "gauge", "percent"),
    panel(3, "Pod CPU", f'sum by(namespace,pod)(rate(container_cpu_usage_seconds_total{{{infra_filter},container!="",container!="POD"}}[5m]))'),
    panel(4, "Pod memory", f'sum by(namespace,pod)(container_memory_working_set_bytes{{{infra_filter},container!="",container!="POD"}})', unit="bytes"),
    panel(5, "Node filesystem usage", f'100 * (1 - node_filesystem_avail_bytes{{{infra_filter},fstype!~"tmpfs|overlay"}}/node_filesystem_size_bytes{{{infra_filter},fstype!~"tmpfs|overlay"}})', unit="percent"),
    panel(6, "Infrastructure logs", '{cluster="$cluster",node=~"$node",namespace="observability"}', "logs", datasource="loki")])

app_filter = 'service_name=~"$service_name",http_route="/test"'
counter = "http_server_request_duration_seconds_count"
save(ROOT / "samples/observability/dashboards/services.json", "lab-services-example", "Lab Services Example", [
    variable("service_name", f"label_values({counter}, service_name)", "sample-spring-boot")], [
    panel(1, "Request rate", f'sum by(service_name)(rate({counter}{{{app_filter}}}[5m]))', unit="reqps"),
    panel(2, "Error percentage", f'100 * (sum(rate({counter}{{{app_filter},http_response_status_code=~"5.."}}[5m])) or vector(0)) / sum(rate({counter}{{{app_filter}}}[5m]))', "stat", "percent"),
    panel(3, "p95 response time", f'histogram_quantile(0.95,sum by(le,service_name)(rate(http_server_request_duration_seconds_bucket{{{app_filter}}}[5m])))', unit="s"),
    panel(4, "JVM memory used (Java service)", 'sum(jvm_memory_used_bytes{service_name=~"$service_name"})', unit="bytes"),
    panel(5, "Server logs → trace", '{namespace="sample-app",service_name=~"$service_name"} | json', "logs", datasource="loki")])
