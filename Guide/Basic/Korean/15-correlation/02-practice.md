# 15 실습 — 같은 요청의 로그·트레이스와 오류 분석

시작 조건: 서버 자동 계측과 14 실습 완료. 화면은 Windows Grafana, 설정 변경은 WSL Bash 저장소 루트에서 진행합니다. 새 터미널에서는 00 실습의 export를 반복합니다.

## 1. 로그에서 요청 하나 선택

Test를 한 번 누릅니다. Grafana 왼쪽 **Explore → 데이터 소스 Loki → Code → Last 15 minutes**에서 입력하고 Run query를 누릅니다.

```logql
{namespace="sample-app",service_name=~"sample-spring-boot|sample-fastapi"} | json
```

Spring의 요청 시작과 FastAPI의 요청 완료 로그를 펼쳐 `trace_id`를 비교합니다. 같은 요청의 32자리 ID가 같고, 처리 단계의 `span_id`는 다릅니다. 시간으로 요청을 구분하기 어렵다면 버튼을 한 번만 누르고 그 직후 기록을 찾습니다.

## 2. 로그 → 트레이스 → 로그로 이동

1. 해당 요청의 로그 한 줄을 눌러 상세를 펼칩니다.
2. 상세의 **TraceID / View trace** 링크를 누릅니다. JSON 본문 아래에 있을 수 있으므로 상세 영역을 스크롤합니다.
3. 열린 Tempo 상세에서 Spring 서버 → HTTP client → FastAPI 서버의 막대를 확인합니다.
4. FastAPI span 이름을 클릭해 span 상세를 엽니다.
5. 상세 연결 영역의 **Logs** 링크 또는 로그 아이콘을 누릅니다.
6. Loki 조회 결과의 service_name과 trace_id가 선택한 span과 같은지 확인합니다.

정상 결과: 하나의 요청에서 log → trace → FastAPI log로 왕복합니다. 로그가 없으면 요청 전후 1분 시간 범위와 현재 서비스 label을 확인합니다. [데이터 소스 연결 설정](../../../../infrastructure/grafana/datasources.yaml)은 이 연결을 미리 설정합니다.

## 3. 지연 재현

WSL에서 FastAPI에 1초 지연을 설정합니다.

```bash
kubectl -n sample-app set env deployment/fastapi TEST_DELAY_MS=1000 TEST_FAILURE_MODE=none
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

준비 완료 후 Test를 3번 누릅니다. 30초 뒤 점도표에서 높은 점을 선택합니다. FastAPI 단계와 이를 기다리는 Spring의 호출 시간이 길어졌는지 확인합니다. 오류 응답 없이 오래 걸리는 요청의 예입니다.

## 4. 오류 재현

이제 지연을 해제하고 FastAPI가 의도적으로 500을 반환하게 합니다.

```bash
kubectl -n sample-app set env deployment/fastapi TEST_DELAY_MS=0 TEST_FAILURE_MODE=http500
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

Test를 누릅니다. FastAPI는 500, Spring은 downstream 실패를 502로 반환합니다. 브라우저 Console의 실패, 두 서버 오류 로그, 트레이스의 오류 표시를 확인합니다. 서비스 Dashboard에서 최근 요청에 오류 응답이 포함되는지 확인합니다. 오류율은 최근 5분 구간이므로 즉시 100%로 바뀌는 것은 아닙니다.

## 5. timeout 재현

FastAPI가 5초 기다리게 합니다. Spring의 응답 대기 제한은 3초입니다.

```bash
kubectl -n sample-app set env deployment/fastapi TEST_DELAY_MS=5000 TEST_FAILURE_MODE=none
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

Test를 한 번 누르고 10초 기다립니다. 브라우저에서는 Spring의 504를 확인합니다. FastAPI는 Spring이 기다리기를 멈춘 뒤에도 처리 중일 수 있습니다. 요청 실패 시각, FastAPI 완료 로그 시각, 두 span의 시간을 비교합니다.

## 6. 정상 복구

```bash
kubectl -n sample-app set env deployment/fastapi TEST_DELAY_MS=0 TEST_FAILURE_MODE=none
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

Test를 눌러 다시 성공하는지 확인합니다. 다음 장으로 갈 때는 정상 상태를 유지합니다.

| 문제 | 확인 순서 |
|---|---|
| 로그에 trace_id 없음 | 계측 overlay 적용, 요청 중의 업무 로그인지, agent/launcher 로그 |
| 두 서버가 별개 trace | HTTP client의 traceparent 전달과 Python 계측 실행 |
| View trace가 안 보임 | 유효한 32자리 ID와 Loki derivedFields 설정 |
| span에서 로그 없음 | service.name → service_name 대응, 시간 범위, JSON trace_id 검색 |
| 메트릭 No data | 실제 metric·label, 30초 export, 중앙 Alloy 오류 |
| Pod Pending/OOM | describe Events, local PV worker 배치, WSL 메모리 |

완료 확인: 지연·오류·timeout을 재현하고 같은 요청의 숫자·로그·트레이스 차이를 설명할 수 있습니다. React는 Console로 동작을 확인하고 브라우저 계측은 하지 않습니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../16-preservation/01-concept.md)
