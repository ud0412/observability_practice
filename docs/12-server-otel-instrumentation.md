# 12. 서버의 metric·trace를 OTel로 자동 계측

기본 샘플이 정상 호출되는 WSL 터미널에서 다음 overlay를 적용한다.

```bash
source scripts/lib/common.sh
k apply -k samples/kubernetes/instrumented
k -n sample-app rollout status deployment/spring-boot --timeout=300s
k -n sample-app rollout status deployment/fastapi --timeout=180s
```

[Java patch](../samples/kubernetes/instrumented/spring-boot.yaml)는 JAVA_TOOL_OPTIONS에 `-javaagent`를 추가한다. [Python patch](../samples/kubernetes/instrumented/fastapi.yaml)는 `opentelemetry-instrument uvicorn ...` launcher를 사용한다. 비즈니스 코드에 수동 span 생성은 없다. 자동 계측은 HTTP server/client와 지원 runtime을 관찰하며 업무 log 메시지는 앱 코드가 작성한다.

공통 설정은 service.name, 중앙 Alloy의 HTTP/protobuf 4318 endpoint, metric·trace OTLP exporter, cumulative metric, 30초 export, 전수 sampling이다. `OTEL_LOGS_EXPORTER=none`으로 stdout 수집과 중복을 막는다. Python logging handler도 끄면서 trace context 주입은 유지한다.

브라우저에서 Test를 누른 뒤 Tempo Explore에서 최근 15분·service `sample-spring-boot`를 검색한다. 한 trace에 Spring server span, Java HTTP client span, FastAPI server span이 있어야 한다. Java client가 `traceparent`를 주입하고 Python이 이를 추출한다. React span은 없다.

두 서버 log에 같은 trace_id가 있는지 확인한다. Java는 Logback MDC property map을 JSON encoder가 읽고, Python은 otelTraceID/otelSpanID를 JSON formatter가 변환한다. 앱 시작 log처럼 활성 span이 없는 기록에 ID가 없어도 정상이다.

Mimir Explore에서 metric 목록을 먼저 확인한다.

```promql
{__name__=~"http_server_.*",service_name=~"sample-spring-boot|sample-fastapi"}
```

이 버전의 안정 HTTP duration은 `http.server.request.duration`이고, Prometheus 변환 후 seconds histogram이면 `http_server_request_duration_seconds_{bucket,count,sum}`이 된다. 실제 이름·unit·labels가 아래 표와 맞는지 확인하고 쿼리에 반영한다. 데이터가 나타날 때까지 최소 한 번의 30초 export를 기다린다.

| OTel | Mimir/Grafana에서 확인 |
|---|---|
| service.name resource | `service_name` label로 명시 변환 |
| http.server.request.duration, unit s | `http_server_request_duration_seconds_*` histogram |
| http.response.status_code | `http_response_status_code` datapoint label |
| http.route | `http_route` label, `/test` 필터 |
| Java runtime metric | `jvm_*` 실제 목록과 단위 확인; Python에 동일 JVM metric은 없음 |

metric이 비면 agent/launcher exporter 오류 → 중앙 Alloy receiver → 변환 → Mimir 순서로 확인한다. delta temporality와 exponential histogram의 수용 여부를 실제 데이터와 대조한다. [Java Agent](https://opentelemetry.io/docs/zero-code/java/agent/), [Python 자동 계측](https://opentelemetry.io/docs/zero-code/python/)

[다음: 서비스 Dashboard](13-dashboard-services.md)
