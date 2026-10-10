# 12 실습 — 자동 메트릭·트레이스와 로그 ID 확인

시작 조건: 기본 샘플 정상 응답. 실행 위치: WSL Bash와 Windows Grafana.

## 1. 계측 설정 적용

```bash
kubectl apply -k samples/kubernetes/instrumented
kubectl -n sample-app rollout status deployment/spring-boot --timeout=300s
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

[Java 설정](../../../../samples/kubernetes/instrumented/spring-boot.yaml)의 JAVA_TOOL_OPTIONS와 [Python 설정](../../../../samples/kubernetes/instrumented/fastapi.yaml)의 command를 읽습니다. OTEL_SERVICE_NAME은 각각 `sample-spring-boot`, `sample-fastapi`입니다.

## 2. 데이터를 만들어 보내기

Test 버튼을 3~5번 누릅니다. 최소 30~60초 기다립니다. 로그에서 exporter 오류가 반복되는지도 확인합니다.

```bash
kubectl -n sample-app logs deployment/spring-boot --tail=40
kubectl -n sample-app logs deployment/fastapi --tail=40
```

요청 로그의 `trace_id`는 같은 요청에서 동일한 32자리 ID입니다. `span_id`는 서비스의 처리 단계별로 다른 16자리 ID입니다. 시작 로그처럼 요청 바깥의 메시지는 ID가 없어도 정상입니다.

## 3. Tempo에서 첫 트레이스 열기

1. Grafana 왼쪽 **Explore**를 엽니다.
2. 위쪽 데이터 소스를 **Tempo**, 시간 범위를 **Last 15 minutes**로 설정합니다.
3. 쿼리 유형에서 **TraceQL**을 선택하고 아래를 입력합니다.

```traceql
{ resource.service.name = "sample-spring-boot" && span.http.route = "/test" }
```

4. **Run query**를 누릅니다. 아래에 트레이스 결과 표가 나타납니다.
5. 표의 **Trace ID**를 클릭합니다. 오른쪽 또는 분할된 상세 영역에 요청의 시간 막대가 나타납니다.
6. Spring 서버 처리, FastAPI로 보내는 HTTP client 처리, FastAPI 서버 처리가 같은 트레이스 안에 있는지 확인합니다. 계측 도구가 추가 내부 span을 만들 수 있어 막대 개수는 정확히 3개로 고정하지 않습니다.

## 4. 자동 메트릭 확인

Explore 데이터 소스를 **Mimir**, Code 모드로 바꾸고 실행합니다.

```promql
http_server_request_duration_seconds_count{service_name=~"sample-spring-boot|sample-fastapi",http_route="/test"}
```

정상 결과: 두 service_name의 누적 요청 수가 나타납니다. 실제 목록을 먼저 확인하려면 다음을 실행합니다.

```promql
{__name__=~"http_server_.*",service_name=~"sample-spring-boot|sample-fastapi"}
```

이번 고정 조합은 HTTP duration histogram을 seconds 단위로 변환합니다. `_count`는 요청 수, `_sum`은 시간 합계, `_bucket`은 시간 구간별 요청 수입니다. service_name·http_route·http_response_status_code label을 확인합니다.

No data이면 순서대로 버튼 호출 → 30초 export 대기 → agent/launcher 로그 → 중앙 Alloy 로그 → Mimir Ready를 확인합니다. 한 서버가 별도 트레이스로 보이면 Java client 계측과 Python launcher 적용 여부를 확인합니다.

완료 확인: 하나의 트레이스에 두 서버가 연결되고, 두 서비스의 메트릭과 같은 Trace ID의 JSON 로그가 보입니다.

[Java 자동 계측](https://opentelemetry.io/docs/zero-code/java/agent/) · [Python 자동 계측](https://opentelemetry.io/docs/zero-code/python/)

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../13-service-dashboard/01-concept.md)
