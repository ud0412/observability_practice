# 13 실습 — 고정 서비스에서 선택 가능한 Dashboard로

시작 조건: 12 실습에서 자동 메트릭·트레이스 확인. Windows Grafana, 요청 생성은 WSL Bash에서 진행합니다.

## 1. 고정한 서비스의 요청 수 막대그래프

08 실습처럼 새 Dashboard를 만들고 `Lab Services Basic`으로 저장합니다. 새 Mimir 패널에 입력합니다.

```promql
sum by(service_name) (increase(http_server_request_duration_seconds_count{service_name="sample-spring-boot",http_route="/test"}[15m]))
```

**Type=Instant, Format=Table**, 시각화 **Bar chart**, X Axis는 `service_name`, 제목은 `최근 15분 요청 수`로 설정합니다. 아직 하나의 막대입니다. increase는 조회 구간의 요청 증가량을 추정하므로 표시가 소수일 수 있습니다. Decimals=0으로 표시하되 정확한 원장 개수로 해석하지 않습니다.

## 2. 처리율과 응답 시간 선그래프

각 쿼리를 별도 Mimir 패널로 만들고 Time series를 선택합니다.

초당 처리율, Unit은 `Requests/sec`입니다.

```promql
sum by(service_name) (rate(http_server_request_duration_seconds_count{service_name="sample-spring-boot",http_route="/test"}[5m]))
```

평균 응답 시간, Unit은 `Seconds (s)`입니다.

```promql
sum by(service_name) (rate(http_server_request_duration_seconds_sum{service_name="sample-spring-boot",http_route="/test"}[5m])) / sum by(service_name) (rate(http_server_request_duration_seconds_count{service_name="sample-spring-boot",http_route="/test"}[5m]))
```

각 Legend는 `{{service_name}}`으로 설정하고 저장합니다. 아직 요청이 적으면 그래프가 비거나 불안정할 수 있습니다. 다음 명령으로 60초 동안 요청을 보낸 후 30초 기다립니다.

```bash
for i in $(seq 1 60); do curl -s http://localhost:8080/test >/dev/null; sleep 1; done
```

## 3. 로그 패널

Loki의 Logs 패널에 입력합니다.

```logql
{namespace="sample-app",service_name="sample-spring-boot"} | json
```

제목은 `서비스 요청 로그`로 저장합니다.

## 4. service_name 변수로 변경

10 실습의 **Edit → + → Variable → Query**를 사용합니다. Name과 Label은 `service_name`, 데이터 소스 Mimir, Query type은 Label values, Metric은 `http_server_request_duration_seconds_count`, Label은 `service_name`입니다.

Preview에서 `sample-spring-boot`와 `sample-fastapi`를 확인합니다. Apply, Refresh=On dashboard load, Multi-value와 Include All value를 켜고 저장합니다.

앞에서 만든 메트릭·로그 쿼리의 `service_name="sample-spring-boot"`를 **모두** `service_name=~"${service_name:regex}"`로 바꿉니다. 다른 부분은 유지합니다.

정상 결과: 서비스 선택이 바뀌면 요청 수·처리율·평균 시간·로그가 함께 바뀝니다. All 선택에서는 두 서비스를 비교할 수 있습니다.

## 5. p95와 오류율 추가

p95를 Time series, Unit=Seconds (s)로 추가합니다.

```promql
histogram_quantile(0.95, sum by(le,service_name) (rate(http_server_request_duration_seconds_bucket{service_name=~"${service_name:regex}",http_route="/test"}[5m])))
```

오류율을 Stat, Unit=Percent (0-100)로 추가합니다. 이 패널은 현재 선택한 서비스 전체의 비율입니다.

```promql
100 * (sum(rate(http_server_request_duration_seconds_count{service_name=~"${service_name:regex}",http_route="/test",http_response_status_code=~"5.."}[5m])) or vector(0)) / sum(rate(http_server_request_duration_seconds_count{service_name=~"${service_name:regex}",http_route="/test"}[5m]))
```

요청이 전혀 없을 때는 분모가 0이라 유효한 비율이 나오지 않을 수 있습니다. 오류 재현은 15 실습에서 진행합니다.

완료 확인: 고정 서비스로 먼저 만들고, 기존 패널을 변수 방식으로 변경했습니다. JVM 메트릭은 Java 서비스에만 있다는 점을 기억하세요. 복습용 [예시 JSON](../../../../samples/observability/dashboards/services.json)은 직접 만든 후 비교합니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../14-trace-scatter/01-concept.md)
