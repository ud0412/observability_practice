# 06 실습 — 노드 Alloy와 중앙 Alloy 설치

시작 조건: Mimir·Loki·Tempo Ready. 실행 위치: WSL Bash, 저장소 루트.

## 1. 두 종류의 수집기 적용

```bash
kubectl apply -f "$LAB_STATE_DIR/rendered/alloy.yaml"
kubectl -n observability rollout status daemonset/alloy-node --timeout=300s
kubectl -n observability rollout status deployment/alloy-central --timeout=300s
```

## 2. 노드별 배치 확인

```bash
kubectl -n observability get pods -l app=alloy-node -o wide
kubectl -n observability get daemonset alloy-node
kubectl -n observability get pods -l app=alloy-central -o wide
```

정상 결과: 노드 Alloy 두 개의 NODE 열이 각각 control-plane과 worker입니다. DaemonSet의 DESIRED·CURRENT·READY가 모두 2입니다. 중앙 Alloy는 하나이며 어느 노드에 배치되었는지 NODE 열에서 확인합니다.

## 3. 로그와 수신 주소 확인

```bash
kubectl -n observability logs -l app=alloy-node --tail=30 --prefix
kubectl -n observability logs deployment/alloy-central --tail=30
kubectl -n observability get service alloy-central
```

중앙 수신 포트는 OTLP gRPC 4317과 HTTP 4318입니다. 샘플 서버는 HTTP 4318을 사용합니다. 이 포트를 Windows 브라우저에서 여는 실습은 아닙니다.

## 4. 설정에서 전달 대상 찾기

[노드 설정](../../../../infrastructure/alloy-node/config.alloy)에서 `prometheus.remote_write`와 `loki.write`를 찾습니다. [중앙 설정](../../../../infrastructure/alloy-central/config.alloy)에서 `otelcol.receiver.otlp`와 `otelcol.exporter.otlp`를 찾습니다. 앞쪽은 받는 주소, 뒤쪽은 전달 대상입니다.

완료 확인: Alloy 2+1개 Ready. 실제 수집 확인은 다음 Grafana 실습에서 `up`, 노드 메트릭, Pod 로그를 조회하며 진행합니다. 중앙에는 아직 샘플 데이터가 없는 것이 정상입니다.

설정 오류로 준비되지 않으면 `kubectl -n observability describe pod -l app=alloy-central`과 위 로그를 확인합니다. 노드 Alloy가 하나뿐이면 DaemonSet의 Events와 두 노드 Ready 여부를 확인합니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../07-grafana/01-concept.md)
