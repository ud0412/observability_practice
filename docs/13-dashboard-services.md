# 13. 서비스 Dashboard 직접 만들기

선행 조건은 두 서버 OTel metric·trace·JSON log 수집이다. Grafana에서 `Lab Services`를 빈 Dashboard로 만들고 refresh 30초, 최근 15분으로 설정한다. `service_name` 변수를 Mimir query `label_values(http_server_request_duration_seconds_count, service_name)`로 만든다. 실제 metric 이름이 다르면 12장의 조회 결과를 사용한다.

| 패널 | 예제 쿼리 | 설정 |
|---|---|---|
| 처리율 | `sum by(service_name) (rate(http_server_request_duration_seconds_count{service_name=~"$service_name",http_route="/test"}[5m]))` | Time series·req/s |
| 오류율 | `100 * sum(rate(http_server_request_duration_seconds_count{service_name=~"$service_name",http_route="/test",http_response_status_code=~"5.."}[5m])) / sum(rate(http_server_request_duration_seconds_count{service_name=~"$service_name",http_route="/test"}[5m]))` | Stat·percent |
| p95 응답 시간 | `histogram_quantile(0.95, sum by(le,service_name) (rate(http_server_request_duration_seconds_bucket{service_name=~"$service_name",http_route="/test"}[5m])))` | Time series·seconds |
| Java 메모리 | Explore에서 실제 `jvm_memory_*`를 선택하고 service_name 필터 | bytes IEC, pool/type label에 따른 집계 |
| 서버 log | `{namespace="sample-app",service_name=~"$service_name"} | json` | Loki Logs |

변수·legend·unit·threshold를 설정하고 서비스 선택이 metric과 log에 함께 적용되는지 확인한다. 요청이 거의 없으면 rate·p95가 비거나 흔들린다. 표본이 적은 p95를 정밀 성능 측정처럼 해석하지 않는다. 처음에는 Test 버튼을 여러 번 누르고, 충분한 표본은 별도 수동 요청으로 만든다.

```bash
# WSL에서 별도로 실행. 인프라 up에 포함되지 않는다.
for i in $(seq 1 60); do curl -s http://localhost:8080/test >/dev/null; sleep 1; done
```

오류율이 빈 경우 기본 성공 요청에 오류 series가 아직 생성되지 않았을 수 있다. 14장의 오류 시나리오를 수행한 뒤 확인한다. JVM 패널은 Java 서비스를 선택할 때만 의미가 있고 FastAPI에 JVM data를 기대하지 않는다.

Logs 패널의 trace_id 링크를 눌러 같은 요청을 열고 span에서 log로 다시 이동한다. Dashboard 저장·export/import는 09장과 같은 관리 경로를 사용한다. [완성 예시](../samples/observability/dashboards/services.json)는 직접 만든 뒤 비교한다.

완료 과제: 정상·지연·오류 요청을 보고 처리율·오류율·p95·log·trace의 변화 원인을 설명한다. [다음: 연결·문제 분석](14-correlation-and-troubleshooting.md)
