"""Author the reference classic-dashboard JSON; never installs/provisions it."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def variable(name, query, current):
    return {"name": name, "type": "query", "datasource": {"type": "prometheus", "uid": "mimir"},
            "query": query, "refresh": 1, "current": {"text": current, "value": current},
            "multi": False, "includeAll": False}


def panel(index, title, query, kind="timeseries", unit="short", datasource="mimir"):
    type_name = {"loki": "loki", "tempo": "tempo"}.get(datasource, "prometheus")
    result = {"id": index, "title": title, "type": kind,
              "datasource": {"type": type_name, "uid": datasource},
              "gridPos": {"x": 12 * ((index - 1) % 2), "y": 8 * ((index - 1) // 2), "w": 12, "h": 8},
              "targets": [{"refId": "A", "expr": query, "datasource": {"type": type_name, "uid": datasource}}],
              "fieldConfig": {"defaults": {"unit": unit}, "overrides": []}, "options": {}}
    if kind == "logs":
        result["options"] = {"showTime": True, "showLabels": False, "wrapLogMessage": True, "sortOrder": "Descending"}
    elif kind in ("gauge", "bargauge"):
        result["fieldConfig"]["defaults"].update({"min": 0, "max": 100, "decimals": 1,
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None},
                {"color": "yellow", "value": 70}, {"color": "red", "value": 90}]}})
        result["options"] = {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                             "orientation": "horizontal", "showThresholdLabels": True, "showThresholdMarkers": True}
    if kind in ("barchart", "table"):
        result["targets"][0].update({"instant": True, "range": False, "format": "table"})
    if datasource == "mimir": result["targets"][0]["legendFormat"] = "{{node}}" if "node_" in query else "{{service_name}}"
    return result


def save(file, uid, title, variables, panels):
    file.parent.mkdir(parents=True, exist_ok=True)
    dashboard = {"id": None, "uid": uid, "title": title, "schemaVersion": 41, "version": 1,
                 "tags": ["practice"], "timezone": "browser", "editable": True, "refresh": "30s",
                 "time": {"from": "now-15m", "to": "now"}, "templating": {"list": variables}, "panels": panels}
    file.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


infra_filter = 'node=~"${node:regex}"'
save(ROOT / "infrastructure/grafana/dashboards/infrastructure.json", "lab-infra-example", "Lab Infrastructure Example", [
    variable("node", 'label_values(node_cpu_seconds_total, node)', "observability-lab-worker")], [
    panel(1, "CPU usage", f'100 * (1 - avg by(node)(rate(node_cpu_seconds_total{{{infra_filter},mode="idle"}}[5m])))', unit="percent"),
    panel(2, "Memory usage", f'100 * (1 - node_memory_MemAvailable_bytes{{{infra_filter}}}/node_memory_MemTotal_bytes{{{infra_filter}}})', "gauge", "percent"),
    panel(3, "Pod CPU", f'sum by(namespace,pod)(rate(container_cpu_usage_seconds_total{{{infra_filter},container!="",container!="POD"}}[5m]))'),
    panel(4, "Pod memory", f'sum by(namespace,pod)(container_memory_working_set_bytes{{{infra_filter},container!="",container!="POD"}})', unit="bytes"),
    panel(5, "Node filesystem usage", f'100 * (1 - node_filesystem_avail_bytes{{{infra_filter},fstype!~"tmpfs|overlay"}}/node_filesystem_size_bytes{{{infra_filter},fstype!~"tmpfs|overlay"}})', unit="percent"),
    panel(6, "Infrastructure logs", '{node=~"${node:regex}",namespace="observability"}', "logs", datasource="loki")])

app_filter = 'service_name=~"${service_name:regex}",http_route="/test"'
counter = "http_server_request_duration_seconds_count"
save(ROOT / "samples/observability/dashboards/services.json", "lab-services-example", "Lab Services Example", [
    variable("service_name", f"label_values({counter}, service_name)", "sample-spring-boot")], [
    panel(1, "Request rate", f'sum by(service_name)(rate({counter}{{{app_filter}}}[5m]))', unit="reqps"),
    panel(2, "Error percentage", f'100 * (sum(rate({counter}{{{app_filter},http_response_status_code=~"5.."}}[5m])) or vector(0)) / sum(rate({counter}{{{app_filter}}}[5m]))', "stat", "percent"),
    panel(3, "p95 response time", f'histogram_quantile(0.95,sum by(le,service_name)(rate(http_server_request_duration_seconds_bucket{{{app_filter}}}[5m])))', unit="s"),
    panel(4, "JVM memory used (Java service)", 'sum(jvm_memory_used_bytes{service_name=~"${service_name:regex}"})', unit="bytes"),
    panel(5, "Server logs → trace", '{namespace="sample-app",service_name=~"${service_name:regex}"} | json', "logs", datasource="loki")])

# Fixed-value examples are the learner's starting point before variables.
def fixed_copy(source, destination, uid, title, replacements):
    dashboard = json.loads(source.read_text(encoding="utf-8"))
    dashboard.update({"uid": uid, "title": title, "templating": {"list": []}})
    for item in dashboard["panels"]:
        for target in item["targets"]:
            for old, new in replacements.items(): target["expr"] = target["expr"].replace(old, new)
    destination.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

infra_dir = ROOT / "infrastructure/grafana/dashboards"
apps_dir = ROOT / "samples/observability/dashboards"
memory = '100 * (1 - node_memory_MemAvailable_bytes{node=~"${node:regex}"} / node_memory_MemTotal_bytes{node=~"${node:regex}"})'
for file in (infra_dir / "infrastructure.json", apps_dir / "services.json"):
    dashboard = json.loads(file.read_text(encoding="utf-8"))
    for v in dashboard["templating"]["list"]:
        if v["name"] != "cluster": v.update({"multi": True, "includeAll": True})
    if file.parent == infra_dir:
        dashboard["panels"].extend([
            panel(7, "Collection status", 'up{job="node",node=~"${node:regex}"}', "stat"),
            panel(8, "Node memory bars", memory, "barchart", "percent"),
            panel(9, "Node memory bar gauges", memory, "bargauge", "percent"),
            panel(10, "Node memory table", memory, "table", "percent")])
        dashboard["panels"][-3]["options"] = {"xField": "node", "orientation": "vertical"}
    else:
        dashboard["panels"].append(panel(6, "Requests in 15 minutes", 'sum by(service_name)(increase(http_server_request_duration_seconds_count{service_name=~"${service_name:regex}",http_route="/test"}[15m]))', "barchart"))
        dashboard["panels"][-1]["options"] = {"xField": "service_name", "orientation": "vertical"}
    file.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

fixed_copy(infra_dir / "infrastructure.json", infra_dir / "infrastructure-fixed.json", "lab-infra-fixed", "Lab Infrastructure Fixed Example",
           {"$cluster": "observability-lab", "${node:regex}": "observability-lab-worker", "$node": "observability-lab-worker"})
fixed_copy(apps_dir / "services.json", apps_dir / "services-fixed.json", "lab-services-fixed", "Lab Services Fixed Example",
           {"${service_name:regex}": "sample-spring-boot", "$service_name": "sample-spring-boot"})

trace = panel(1, "Request duration — click to open trace", "", "xychart", "ms", "tempo")
trace["targets"] = [{"refId": "A", "datasource": {"type": "tempo", "uid": "tempo"}, "queryType": "traceql",
                      "query": '{ resource.service.name = "sample-spring-boot" && span:kind = server && span.http.route = "/test" }',
                      "tableType": "spans", "limit": 100, "spss": 1}]
trace["transformations"] = [{"id": "organize", "options": {"renameByName": {
    "startTime": "Start time", "duration": "Duration", "traceID": "Trace ID"}}}]
trace["options"] = {"seriesMapping": "auto", "dims": {"x": "Start time", "y": "Duration"},
                    "show": "points", "pointSize": {"fixed": 8}}
trace["fieldConfig"]["defaults"]["links"] = [{"title": "Open this trace",
    "url": (ROOT / "samples/observability/trace-explore-link.txt").read_text().strip(), "targetBlank": True, "oneClick": True}]
save(apps_dir / "traces.json", "lab-traces-example", "Lab Trace Scatter Example", [], [trace])
