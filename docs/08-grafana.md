# 08. Grafana 설치·접속·데이터 소스

```bash
source scripts/lib/common.sh
k apply -f "$LAB_STATE_DIR/rendered/grafana.yaml"
k -n observability rollout status deployment/grafana --timeout=450s
k apply -f "$LAB_STATE_DIR/rendered/grafana-route.yaml"
k -n observability get httproute grafana -o yaml
bash scripts/lab.sh verify
bash scripts/lab.sh access
```

Windows 브라우저에서 `http://localhost:8080/grafana/`를 연다. 사용자는 `admin`이다. 비밀번호는 관리 경로의 `credentials.json`에서 로컬로 확인한다. 예상 출력이나 저장소에 비밀번호를 복사하지 않는다.

Grafana의 root_url·serve_from_sub_path·HTTPRoute를 `/grafana/`로 맞춘다. access 명령은 Gateway가 생성한 **Envoy Proxy Service**를 찾아 localhost에 port-forward하며 PID를 관리한다. Windows에서 접근이 안 되면 WSL의 `curl http://localhost:8080/grafana/api/health`부터 확인한다. 포트 충돌은 `config/lab.env`의 GRAFANA_PORT 변경 후 prepare/up 재실행으로 반영한다.

[datasource 설정](../infrastructure/grafana/datasources.yaml)은 UID `mimir`, `loki`, `tempo`를 고정한다. Grafana의 Connections → Data sources에서 세 연결을 확인한다. Mimir URL의 `/prometheus` prefix와 write API의 `/api/v1/push`를 혼동하지 않는다.

Explore에서 먼저 다음을 확인한다.

```promql
up{cluster="observability-lab"}
node_cpu_seconds_total
```

```logql
{cluster="observability-lab", namespace="observability"}
```

trace는 샘플을 계측한 뒤 생긴다. 지금 Tempo에 trace가 없다고 설치 실패로 판단하지 않는다. Grafana DB는 `/var/lib/grafana` PVC에 저장하며 직접 만든 Dashboard를 보존한다. datasource provisioning 재실행은 사용자 Dashboard를 덮어쓰지 않는다.

완료 기준은 Envoy 경유 로그인, 세 데이터 소스 연결, node metric과 container log 조회다. [다음: 인프라 Dashboard](09-dashboard-infrastructure.md)
