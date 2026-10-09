# 04. Envoy Gateway와 데이터 평면

Envoy Gateway controller는 Gateway API 설정을 읽고 Envoy Proxy를 생성한다. 브라우저 요청은 Proxy Service로 보내야 한다. controller Service로 port-forward하지 않는다.

```bash
source scripts/lib/common.sh
helm upgrade --install eg oci://docker.io/envoyproxy/gateway-helm \
  --version "v$ENVOY_GATEWAY_VERSION" -n envoy-gateway-system --create-namespace \
  --kubeconfig "$KUBECONFIG" --kube-context "kind-$LAB_NAME" \
  -f infrastructure/envoy-gateway/values.yaml --wait --timeout 10m
k wait --for=condition=Established crd/gateways.gateway.networking.k8s.io --timeout=120s
k apply -f "$LAB_STATE_DIR/rendered/gateway.yaml"
k -n envoy-gateway-system wait --for=condition=Accepted gateway/lab --timeout=180s
k -n envoy-gateway-system get gateway,svc,pods
```

chart가 Gateway API CRD를 소유한다. 별도 CRD bundle을 중복 설치하지 않는다. `GatewayClass lab-gateway`는 Envoy controller를 지정하고, `Gateway lab`은 HTTP 80 listener를 정의한다. EnvoyProxy가 Service를 ClusterIP로 생성하게 설정하므로 LoadBalancer 외부 IP가 없어도 정상이다.

HTTPRoute는 후속 Grafana/샘플 단계에서 추가한다. 서로 다른 namespace의 Route가 Gateway에 붙는 것은 allowedRoutes로 허용한다. backend Service는 해당 Route와 같은 namespace에 두므로 ReferenceGrant가 필요 없다.

완료 기준은 Gateway Accepted와 Envoy Proxy Pod 생성이다. `Programmed`와 listener conditions도 확인한다. 아직 backend Route를 설치하지 않았으므로 HTTP 404는 이 단계의 설치 실패 기준이 아니다.

[Envoy 호환성 표](https://gateway.envoyproxy.io/news/releases/matrix/), [다음: 저장소](05-storage-and-seaweedfs.md)
