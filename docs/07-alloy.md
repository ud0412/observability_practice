# 07. 노드별 Alloy와 중앙 Alloy

```bash
source scripts/lib/common.sh
k apply -f "$LAB_STATE_DIR/rendered/alloy.yaml"
k -n observability rollout status daemonset/alloy-node --timeout=300s
k -n observability rollout status deployment/alloy-central --timeout=300s
k -n observability get pods -o wide
```

노드 Alloy가 2개, 중앙 Alloy가 1개여야 한다. control-plane taint도 toleration으로 허용한다. [노드 설정](../infrastructure/alloy-node/config.alloy)의 discovery field selector는 `spec.nodeName`을 제한하여 전체 클러스터 로그가 노드마다 중복 수집되지 않게 한다.

| 입력 | 처리 | 출력 |
|---|---|---|
| 노드 `/proc`·`/sys`·rootfs | 내장 unix exporter → scrape 30초 | Mimir remote_write |
| kubelet/cAdvisor | API proxy·ServiceAccount·CA 검증 | Mimir remote_write |
| 해당 노드 `/var/log/pods` | file tail → CRI 처리·labels | Loki |
| 서버 OTLP metric | 중앙 Alloy·service_name label 변환 | Prometheus 변환 → Mimir |
| 서버 OTLP trace | 중앙 Alloy·batch | Tempo OTLP |

[중앙 설정](../infrastructure/alloy-central/config.alloy)은 log receiver를 연결하지 않는다. 서버 log는 stdout 경로를 사용한다. 같은 log를 OTLP로 다시 내보내지 않는다. trace_id/span_id는 log 내용으로 저장하고 Loki stream label로 만들지 않는다.

metric remote_write WAL과 log 읽기 위치는 영속 경로에 있다. 앱/collector의 전송 전 메모리 버퍼와 저장된 WAL은 다른 상태다. 기본 OTLP metric temporality는 cumulative이며, delta를 Prometheus 변환기에 그대로 보내면 지표가 빠질 수 있다.

완료 기준은 Alloy Ready와 error 로그 없음이다. [다음 Grafana 단계](08-grafana.md)에서 `node_cpu_seconds_total`, `container_cpu_usage_seconds_total`, 실제 Pod log를 조회해 파이프라인을 검증한다.

kind node의 unix metric은 WSL 커널·namespace에 영향을 받는다. 두 노드가 별도 물리 PC인 것처럼 합산하지 않는다. `/host/root`는 kind 노드 파일시스템 관측 범위다.

[Alloy Kubernetes log](https://grafana.com/docs/alloy/latest/collect/logs-in-kubernetes/), [Prometheus 변환](https://grafana.com/docs/alloy/latest/reference/components/otelcol/otelcol.exporter.prometheus/)
