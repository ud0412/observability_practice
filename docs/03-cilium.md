# 03. Cilium CNI 설치와 통신 확인

kind 클러스터를 만든 WSL Bash에서 진행한다. Cilium은 CNI 역할을 맡고 kube-proxy는 유지한다. Hubble, Cilium Gateway API, L7 proxy와 별도 Cilium Envoy DaemonSet은 기본 구성에서 끈다. HTTP 라우팅은 별도 Envoy Gateway가 맡는다.

```bash
source scripts/lib/common.sh
helm repo add cilium https://helm.cilium.io --force-update
helm repo update cilium
helm upgrade --install cilium cilium/cilium --version "$CILIUM_VERSION" \
  -n kube-system --kubeconfig "$KUBECONFIG" --kube-context "kind-$LAB_NAME" \
  -f infrastructure/cilium/values.yaml --wait --timeout 10m
k wait --for=condition=Ready nodes --all --timeout=300s
k -n kube-system get pods -l k8s-app=cilium -o wide
```

완료 기준은 노드 2개 Ready, Cilium Pod 2개, operator 1개다. [values](../infrastructure/cilium/values.yaml)의 Kubernetes IPAM·replica·자원 설정을 읽는다. Cilium은 커널 BPF·권한 조건이 있으므로 rootless 런타임으로 임의 교체하지 않는다.

DNS와 Pod → Service 통신을 확인한다.

```bash
k create namespace lab-check
k -n lab-check run web --image=nginx:1.29.6-alpine
k -n lab-check expose pod web --port=80
k -n lab-check wait --for=condition=Ready pod/web --timeout=120s
k -n lab-check run client --image=busybox:1.37.0 --restart=Never --command -- sh -c 'nslookup kubernetes.default; wget -qO- http://web'
k -n lab-check logs client
k delete namespace lab-check
```

예상 결과는 Kubernetes DNS 조회 성공과 nginx HTML 응답이다. 실패 시 CoreDNS 상태, Cilium 로그, `k describe pod`의 scheduling/CNI 이벤트를 구분한다. 이 진단 namespace는 즉시 정리한다.

[Cilium kind 안내](https://docs.cilium.io/en/stable/installation/kind/), [다음: Envoy](04-envoy-gateway.md)
