# 14. 같은 요청의 log와 trace 연결

Windows 브라우저에서 Test 한 번을 누르고 Grafana Explore에서 다음 LogQL을 실행한다.

```logql
{namespace="sample-app",service_name=~"sample-spring-boot|sample-fastapi"} | json
```

Spring의 request started와 FastAPI request completed에 같은 32자리 trace_id가 있는지 확인한다. 각 활성 span의 16자리 span_id는 다르다. Loki는 JSON 내용에서 trace_id를 추출해 Tempo UID `tempo`에 trace ID 조회 링크를 만든다. ID를 Loki index label로 추가하면 요청마다 새로운 stream이 생기므로 사용하지 않는다.

1. log 상세의 **View trace**를 누른다.
2. Spring server → HTTP client → FastAPI server span의 부모 관계와 시간을 확인한다.
3. FastAPI span의 Logs 연결을 눌러 service_name과 trace_id가 일치하는 Loki 기록을 찾는다.
4. 시간이 안 맞으면 두 datasource의 시간 범위와 trace-to-logs ±1분 설정을 확인한다.

지연·오류·timeout은 WSL에서 FastAPI 설정을 변경하여 재현한다. 각 변경 후 rollout을 기다리고 Test를 누른다.

```bash
source scripts/lib/common.sh
# 지연: FastAPI 처리 시간이 1초 증가
k -n sample-app set env deployment/fastapi TEST_DELAY_MS=1000 TEST_FAILURE_MODE=none
k -n sample-app rollout status deployment/fastapi
# 오류: FastAPI 500, Spring 502
k -n sample-app set env deployment/fastapi TEST_DELAY_MS=0 TEST_FAILURE_MODE=http500
k -n sample-app rollout status deployment/fastapi
# timeout: FastAPI 5초 지연, Spring 응답 timeout 3초 → 504
k -n sample-app set env deployment/fastapi TEST_DELAY_MS=5000 TEST_FAILURE_MODE=none
k -n sample-app rollout status deployment/fastapi
# 정상 복구
k -n sample-app set env deployment/fastapi TEST_DELAY_MS=0 TEST_FAILURE_MODE=none
k -n sample-app rollout status deployment/fastapi
```

| 관찰 | 확인 순서 |
|---|---|
| log trace_id 없음 | 계측 overlay 적용·활성 요청 안의 log·JSON encoder/context injection |
| 서비스가 별개 trace | Java client 지원·traceparent 전달·Python launcher |
| 로그 링크가 다른 결과 | derived regex·datasource UID·trace ID query |
| trace에서 log 없음 | service.name↔service_name 매핑·LogQL JSON parsing·시간 범위 |
| metric No data | 실제 이름·label·export interval·cumulative·Alloy error |
| 404/502 | HTTPRoute Accepted/ResolvedRefs·Service endpoint·서버 log |
| Pod Pending/OOM | local PV node affinity·리소스·WSL 메모리·describe 이벤트 |

timeout에서 FastAPI는 Spring이 응답을 포기한 뒤에도 처리 중일 수 있다. 각 서비스 span 시간과 log를 비교한다. React Console의 오류도 확인하되 브라우저 trace는 생성하지 않는다.

[Grafana trace/log 연결](https://grafana.com/docs/grafana/latest/datasources/tempo/configure-tempo-data-source/trace-correlations/), [Python context 주입](https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html), [다음: 보존·삭제](15-persistence-and-destroy.md)
