"""Render the same files for manual and automatic installation. Never deploys."""
import json
import hashlib
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lib"))
from state import LAB_NAME, check_owner, state_path  # noqa: E402


def versions():
    return dict(line.split("=", 1) for line in (ROOT / "config/versions.env").read_text().splitlines()
                if line and not line.startswith("#"))


def resource(kind, name, namespace=None, **extra):
    result = {"apiVersion": "v1", "kind": kind, "metadata": {"name": name}}
    if namespace:
        result["metadata"]["namespace"] = namespace
    result.update(extra)
    return result


def configmap(name, filename, namespace="observability", key="config.yaml"):
    return resource("ConfigMap", name, namespace, data={key: (ROOT / filename).read_text()})


def service(name, ports, namespace="observability"):
    return resource("Service", name, namespace, spec={"selector": {"app": name}, "ports": [
        {"name": label, "port": port, "targetPort": port} for label, port in ports]})


def persistent(name, size, namespace="observability"):
    pv = resource("PersistentVolume", "lab-" + name, spec={
        "capacity": {"storage": size}, "accessModes": ["ReadWriteOnce"],
        "persistentVolumeReclaimPolicy": "Retain", "storageClassName": "lab-local",
        "local": {"path": "/var/local/observability/" + name},
        "claimRef": {"namespace": namespace, "name": name},
        "nodeAffinity": {"required": {"nodeSelectorTerms": [{"matchExpressions": [{
            "key": "kubernetes.io/hostname", "operator": "In", "values": [LAB_NAME + "-worker"]}]}]}},
    })
    pvc = resource("PersistentVolumeClaim", name, namespace, spec={
        "accessModes": ["ReadWriteOnce"], "storageClassName": "lab-local", "volumeName": "lab-" + name,
        "resources": {"requests": {"storage": size}}})
    return [pv, pvc]


def deployment(name, image, args, port, memory, namespace="observability", config=True, env=None, extra_ports=()):
    container = {"name": name, "image": image, "args": args,
                 "resources": {"requests": {"cpu": "100m", "memory": memory[0]}, "limits": {"memory": memory[1]}},
                 "ports": [{"containerPort": p} for p in (port, *extra_ports)],
                 "volumeMounts": [{"name": "data", "mountPath": "/data"}],
                 "readinessProbe": {"httpGet": {"path": "/ready", "port": port}, "initialDelaySeconds": 10},
                 "startupProbe": {"httpGet": {"path": "/ready", "port": port}, "failureThreshold": 90, "periodSeconds": 5}}
    volumes = [{"name": "data", "persistentVolumeClaim": {"claimName": name}}]
    if config:
        container["volumeMounts"].append({"name": "config", "mountPath": "/etc/lab", "readOnly": True})
        volumes.append({"name": "config", "configMap": {"name": name}})
    if env:
        container["env"] = env
    annotations = {}
    if config:
        suffix = "config.alloy" if name.startswith("alloy") else "config.yaml"
        annotations["checksum/config"] = hashlib.sha256((ROOT / "infrastructure" / name / suffix).read_bytes()).hexdigest()
    return {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": name, "namespace": namespace},
            "spec": {"replicas": 1, "strategy": {"type": "Recreate"}, "selector": {"matchLabels": {"app": name}},
                     "template": {"metadata": {"labels": {"app": name, "app.kubernetes.io/name": name}, "annotations": annotations},
                                  "spec": {"securityContext": {"fsGroup": 10001}, "containers": [container], "volumes": volumes}}}}


def secret_env():
    return [{"name": key, "valueFrom": {"secretKeyRef": {"name": "s3", "key": key}}}
            for key in ("S3_ACCESS_KEY", "S3_SECRET_KEY")]


def write(path, filename, documents):
    dest = path / "rendered" / filename
    dest.write_text(yaml.safe_dump_all(documents, sort_keys=False, allow_unicode=True), encoding="utf-8")
    dest.chmod(0o600)


def render():
    path = state_path()
    check_owner(path)
    v = versions()
    keys = json.loads((path / "credentials.json").read_text())
    kind = {"kind": "Cluster", "apiVersion": "kind.x-k8s.io/v1alpha4", "networking": {"disableDefaultCNI": True},
            "nodes": [{"role": role, "image": v["KIND_NODE_IMAGE"], "extraMounts": [{
                "hostPath": str(path / "nodes" / role), "containerPath": "/var/local/observability"}]}
            for role in ("control-plane", "worker")]}
    write(path, "kind.yaml", [kind])
    initial = [resource("Namespace", n) for n in ("storage", "observability")]
    sc = resource("StorageClass", "lab-local", provisioner="kubernetes.io/no-provisioner",
                  volumeBindingMode="WaitForFirstConsumer", reclaimPolicy="Retain")
    sc["apiVersion"] = "storage.k8s.io/v1"
    initial.append(sc)
    for name, size, ns in [("seaweedfs", "8Gi", "storage"), ("mimir", "2Gi", "observability"),
                           ("loki", "2Gi", "observability"), ("tempo", "2Gi", "observability"),
                           ("alloy-central", "1Gi", "observability"), ("grafana", "1Gi", "observability")]:
        initial.extend(persistent(name, size, ns))
    for ns in ("storage", "observability"):
        initial.append(resource("Secret", "s3", ns, type="Opaque", stringData={
            key: keys[key] for key in ("S3_ACCESS_KEY", "S3_SECRET_KEY")}))
    write(path, "storage.yaml", initial)

    identity = {"identities": [{"name": "lab-admin", "credentials": [{"accessKey": keys["S3_ACCESS_KEY"],
                 "secretKey": keys["S3_SECRET_KEY"]}], "actions": ["Admin", "Read", "Write", "List", "Tagging"]}]}
    seaweed = deployment("seaweedfs", v["SEAWEEDFS_IMAGE"], ["mini", "-dir=/data", "-ip=127.0.0.1",
                          "-ip.bind=0.0.0.0", "-s3.config=/etc/s3/s3.json", "-bucket=mimir-blocks,loki-data,tempo-traces"],
                          8333, ("256Mi", "1Gi"), "storage", config=False)
    spec = seaweed["spec"]["template"]["spec"]
    spec["securityContext"] = {"runAsUser": 0}
    c = spec["containers"][0]
    c["readinessProbe"] = {"tcpSocket": {"port": 8333}}
    c["startupProbe"] = {"tcpSocket": {"port": 8333}, "failureThreshold": 60, "periodSeconds": 5}
    c["volumeMounts"].append({"name": "s3-config", "mountPath": "/etc/s3", "readOnly": True})
    spec["volumes"].append({"name": "s3-config", "secret": {"secretName": "seaweed-auth"}})
    write(path, "seaweedfs.yaml", [resource("Secret", "seaweed-auth", "storage", stringData={"s3.json": json.dumps(identity)}),
                                  seaweed, service("seaweedfs", [("s3", 8333)], "storage")])
    for name, port, memory in [("mimir", 9009, ("512Mi", "2Gi")), ("loki", 3100, ("256Mi", "1Gi")),
                               ("tempo", 3200, ("256Mi", "1Gi"))]:
        args = ["-config.file=/etc/lab/config.yaml", "-config.expand-env=true"]
        ports = (4317, 4318) if name == "tempo" else ()
        write(path, name + ".yaml", [configmap(name, "infrastructure/" + name + "/config.yaml"),
              deployment(name, v[name.upper() + "_IMAGE"], args, port, memory, env=secret_env(), extra_ports=ports),
              service(name, [("http", port)] + [("otlp-grpc", 4317), ("otlp-http", 4318)] if ports else [("http", port)])])

    sa = resource("ServiceAccount", "alloy-node", "observability")
    role = resource("ClusterRole", "lab-alloy", rules=[
        {"apiGroups": [""], "resources": ["pods", "nodes", "nodes/proxy"], "verbs": ["get", "list", "watch"]}])
    role["apiVersion"] = "rbac.authorization.k8s.io/v1"
    binding = resource("ClusterRoleBinding", "lab-alloy", roleRef={"apiGroup": "rbac.authorization.k8s.io", "kind": "ClusterRole", "name": "lab-alloy"},
                       subjects=[{"kind": "ServiceAccount", "name": "alloy-node", "namespace": "observability"}])
    binding["apiVersion"] = "rbac.authorization.k8s.io/v1"
    central = deployment("alloy-central", v["ALLOY_IMAGE"], ["run", "--server.http.listen-addr=0.0.0.0:12345", "--storage.path=/data", "/etc/lab/config.alloy"],
                         12345, ("128Mi", "512Mi"), extra_ports=(4317, 4318))
    cc = central["spec"]["template"]["spec"]["containers"][0]
    cc["readinessProbe"]["httpGet"]["path"] = "/-/ready"
    cc["startupProbe"]["httpGet"]["path"] = "/-/ready"
    central["spec"]["template"]["spec"]["securityContext"] = {"runAsUser": 0}
    node_spec = {"serviceAccountName": "alloy-node", "tolerations": [{"operator": "Exists", "effect": "NoSchedule"}],
                 "containers": [{"name": "alloy", "image": v["ALLOY_IMAGE"],
                    "args": ["run", "--server.http.listen-addr=0.0.0.0:12345", "--storage.path=/data", "/etc/lab/config.alloy"],
                    "env": [{"name": "NODE_NAME", "valueFrom": {"fieldRef": {"fieldPath": "spec.nodeName"}}}],
                    "securityContext": {"runAsUser": 0},
                    "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}, "limits": {"memory": "512Mi"}},
                    "readinessProbe": {"httpGet": {"path": "/-/ready", "port": 12345}},
                    "volumeMounts": [{"name": name, "mountPath": mount, "readOnly": readonly} for name, mount, readonly in [
                        ("config", "/etc/lab", True), ("data", "/data", False), ("logs", "/var/log/pods", True),
                        ("proc", "/host/proc", True), ("sys", "/host/sys", True), ("root", "/host/root", True)]]}],
                 "volumes": [{"name": "config", "configMap": {"name": "alloy-node"}}] + [
                    {"name": name, "hostPath": {"path": host, "type": "Directory"}} for name, host in [
                        ("data", "/var/local/observability/alloy-node"), ("logs", "/var/log/pods"),
                        ("proc", "/proc"), ("sys", "/sys"), ("root", "/")]]}
    node = {"apiVersion": "apps/v1", "kind": "DaemonSet", "metadata": {"name": "alloy-node", "namespace": "observability"},
            "spec": {"selector": {"matchLabels": {"app": "alloy-node"}}, "template": {"metadata": {"labels": {
                "app": "alloy-node", "app.kubernetes.io/name": "alloy-node"}, "annotations": {
                "checksum/config": hashlib.sha256((ROOT / "infrastructure/alloy-node/config.alloy").read_bytes()).hexdigest()}}, "spec": node_spec}}}
    write(path, "alloy.yaml", [sa, role, binding,
          configmap("alloy-node", "infrastructure/alloy-node/config.alloy", key="config.alloy"), node,
          configmap("alloy-central", "infrastructure/alloy-central/config.alloy", key="config.alloy"), central,
          service("alloy-central", [("http", 12345), ("otlp-grpc", 4317), ("otlp-http", 4318)])])

    grafana = deployment("grafana", v["GRAFANA_IMAGE"], [], 3000, ("128Mi", "384Mi"), config=False, env=[
        {"name": "GF_SECURITY_ADMIN_PASSWORD", "valueFrom": {"secretKeyRef": {"name": "grafana-admin", "key": "password"}}},
        {"name": "GF_SERVER_ROOT_URL", "value": "http://localhost:" + str(__import__("os").environ.get("GRAFANA_PORT", "8080")) + "/grafana/"},
        {"name": "GF_SERVER_SERVE_FROM_SUB_PATH", "value": "true"},
        {"name": "GF_ANALYTICS_REPORTING_ENABLED", "value": "false"}])
    gs = grafana["spec"]["template"]["spec"]
    grafana["spec"]["template"]["metadata"]["annotations"]["checksum/datasources"] = hashlib.sha256((ROOT / "infrastructure/grafana/datasources.yaml").read_bytes()).hexdigest()
    gs["securityContext"] = {"runAsUser": 472, "fsGroup": 472}
    gc = gs["containers"][0]
    gc["volumeMounts"][0]["mountPath"] = "/var/lib/grafana"
    gc["volumeMounts"].append({"name": "datasources", "mountPath": "/etc/grafana/provisioning/datasources", "readOnly": True})
    gs["volumes"].append({"name": "datasources", "configMap": {"name": "grafana-datasources"}})
    for probe in ("readinessProbe", "startupProbe"):
        gc[probe]["httpGet"]["path"] = "/api/health"
    # Local PV directories are created on the host. Grant only this volume to Grafana's UID.
    gs["initContainers"] = [{"name": "permissions", "image": "busybox:1.37.0", "command": ["sh", "-c", "chown -R 472:472 /data"],
                             "securityContext": {"runAsUser": 0}, "volumeMounts": [{"name": "data", "mountPath": "/data"}]}]
    write(path, "grafana.yaml", [resource("Secret", "grafana-admin", "observability", stringData={"password": keys["GRAFANA_PASSWORD"]}),
          configmap("grafana-datasources", "infrastructure/grafana/datasources.yaml", key="datasources.yaml"), grafana, service("grafana", [("http", 3000)])])
    proxy = {"apiVersion": "gateway.envoyproxy.io/v1alpha1", "kind": "EnvoyProxy", "metadata": {"name": "lab-proxy", "namespace": "envoy-gateway-system"},
             "spec": {"provider": {"type": "Kubernetes", "kubernetes": {"envoyService": {"type": "ClusterIP"}}}}}
    gateway_class = {"apiVersion": "gateway.networking.k8s.io/v1", "kind": "GatewayClass", "metadata": {"name": "lab-gateway"},
                     "spec": {"controllerName": "gateway.envoyproxy.io/gatewayclass-controller", "parametersRef": {
                         "group": "gateway.envoyproxy.io", "kind": "EnvoyProxy", "name": "lab-proxy", "namespace": "envoy-gateway-system"}}}
    gateway = {"apiVersion": "gateway.networking.k8s.io/v1", "kind": "Gateway", "metadata": {"name": "lab", "namespace": "envoy-gateway-system"},
               "spec": {"gatewayClassName": "lab-gateway", "listeners": [{"name": "http", "protocol": "HTTP", "port": 80,
                          "allowedRoutes": {"namespaces": {"from": "All"}}}]}}
    route = {"apiVersion": "gateway.networking.k8s.io/v1", "kind": "HTTPRoute", "metadata": {"name": "grafana", "namespace": "observability"},
             "spec": {"parentRefs": [{"name": "lab", "namespace": "envoy-gateway-system"}], "rules": [{
                 "matches": [{"path": {"type": "PathPrefix", "value": "/grafana"}}], "backendRefs": [{"name": "grafana", "port": 3000}]}]}}
    write(path, "gateway.yaml", [proxy, gateway_class, gateway])
    write(path, "grafana-route.yaml", [route])
    print("Rendered infrastructure under " + str(path / "rendered"))


if __name__ == "__main__":
    render()
