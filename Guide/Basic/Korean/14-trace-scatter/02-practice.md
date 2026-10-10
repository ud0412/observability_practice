# 14 실습 — 트레이스 점을 클릭해 시간 막대 열기

시작 조건: 자동 계측과 `Lab Services Basic` 완료. 실제 서버 트레이스가 Tempo에 있어야 합니다. Windows Grafana에서 진행하고, 요청 생성만 WSL에서 합니다.

## 1. 정상·느린 요청 만들기

정상 상태에서 Test를 3번 누릅니다. WSL에서 지연 설정을 적용합니다.

```bash
kubectl -n sample-app set env deployment/fastapi TEST_DELAY_MS=1000 TEST_FAILURE_MODE=none
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

Test를 3번 더 누릅니다. 데이터 전송을 위해 30초 기다립니다. 약 1초가 걸린 요청과 짧은 요청을 비교할 수 있습니다.

## 2. 패널에서 실제 요청 표 확인

1. `Lab Services Basic`에서 Edit → + → Panel → Configure visualization을 엽니다.
2. 데이터 소스를 **Tempo**, Query type을 **TraceQL**로 선택합니다.
3. 아래를 입력하고 Refresh를 누릅니다.

```traceql
{ resource.service.name = "sample-spring-boot" && span:kind = server && span.http.route = "/test" }
```

4. 쿼리의 **Options → Table Format(또는 Table Type) → Spans**를 선택합니다. trace와 중첩 span 표 대신 평평한 span 행을 받는 설정입니다.
5. Limit은 `100`, Span Limit은 `1`로 설정합니다. 요청당 선택한 서버 span 한 행을 사용합니다.
6. 시각화를 우선 **Table**로 선택하고 Table view에서 시작 시각·처리 시간·Trace ID가 같은 행에 있는지 확인합니다.

이 버전의 필드 표시 이름과 원본 이름은 화면 위치에 따라 다를 수 있습니다. **패널 편집 → Table view의 열 제목**으로 확인합니다. `Start time`/`startTime`, `Duration`/`duration`, `Trace ID`/`traceID`가 해당 열입니다. span의 Duration을 사용하며 검색 결과 전체의 traceDuration과 혼동하지 않습니다.

## 3. 열 이름과 자료형 준비

패널 아래 **Transformations → Add transformation → Organize fields by name**을 선택합니다. 이 세 열을 `Start time`, `Duration`, `Trace ID`로 rename합니다. 그 밖의 불필요한 열은 숨깁니다. **Trace ID 열은 숨기거나 제거하지 않습니다.** 클릭 링크가 같은 행의 ID를 읽기 때문입니다.

시작 시각이 이미 시간형이면 그대로 사용합니다. 텍스트라면 **Add transformation → Convert field type → Start time → Time**을 선택합니다. Duration은 숫자형이어야 합니다. 숫자의 원 단위를 Table view와 Field 설정에서 확인합니다. Tempo 결과가 ms이면 아래 Unit도 milliseconds로 지정하고, ns인 원본이면 **Add field from calculation → Binary operation → Duration / 1000000**, Alias=`Duration ms`로 변환한 값을 사용합니다. 문자 `1s`가 들어간 표시용 열 대신 숫자 원본 필드를 사용합니다.

필드 이름을 정규화하고 원본 단위를 확인하는 단계가 끝나기 전에는 점도표 설정으로 넘어가지 않습니다. 숫자 단위가 다르면 1초 지연이 1000ms 부근에 나타나지 않습니다.

## 4. 점도표 설정

1. **All visualizations → XY chart**를 선택합니다.
2. 오른쪽 **XY chart options → Series mapping=Auto**를 선택합니다.
3. **Frame**은 앞에서 확인한 span 표를 선택합니다.
4. **X field=Start time**, **Y field=Duration**을 선택합니다. ns 변환을 했다면 Y는 `Duration ms`입니다. 나머지 숫자 열이 Y로 선택되지 않게 합니다.
5. **Show=Points**, **Point size=8**로 설정합니다.
6. **Standard options → Unit=Milliseconds (ms)**를 선택합니다. Duration이 원래 seconds면 단위 Seconds를 쓰거나 1000을 곱해 ms로 통일합니다.
7. 제목을 `요청별 처리 시간 — 점을 눌러 상세 보기`로 설정합니다.

정상 결과: 짧은 요청 점과 약 1000ms 이상의 느린 점이 보입니다. 마우스를 올리면 시각과 처리 시간이 나타납니다. 두 요청의 시각과 값이 같으면 점이 겹칠 수 있으므로 요청을 간격을 두고 만듭니다.

## 5. 클릭 링크 추가

한 점의 숫자 값이 아니라 같은 행의 Trace ID를 넘겨야 합니다. 오른쪽 옵션에서 **Data links → Add link**를 엽니다.

- Title: `이 요청의 트레이스 열기`
- URL: 아래 파일의 한 줄 전체를 복사
- Open in new tab: 켬
- One click: 켬

복사할 링크: [trace-explore-link.txt](../../../../samples/observability/trace-explore-link.txt). 이 링크는 datasource UID `tempo`, 같은 행의 `${__data.fields["Trace ID"]}`를 사용합니다. 필드 이름은 3번의 rename과 정확히 같아야 합니다. URL을 직접 수정할 때 큰따옴표와 URL 인코딩을 지우지 않습니다.

Save로 링크 설정을 반영하고 Dashboard도 저장합니다. Explore를 열어 두면 원래 Dashboard의 점도표와 상세 화면을 비교하기 쉽습니다.

## 6. 클릭한 요청과 상세 화면 대조

1. 약 1000ms 이상인 점 하나를 클릭합니다.
2. 새 탭의 Explore에서 Tempo의 트레이스 상세를 확인합니다.
3. 상세 화면의 Trace ID가 원본 표의 선택한 행과 같은지 확인합니다.
4. Spring Boot 서버 span을 펼치고 그 아래 HTTP client와 FastAPI span의 시간 막대를 읽습니다.
5. FastAPI의 약 1초 지연이 긴 호출 막대에 나타나는지 확인합니다.

숫자 선그래프를 새로 그리는 단계가 아니라 **선택한 요청 내부의 시간 막대**를 여는 단계입니다.

| 문제 | 확인 |
|---|---|
| XY chart에 쓸 열이 없음 | Spans 표의 시간형·숫자형 여부, Convert field type |
| 한 요청에 여러 점 | Spring 서버 span과 /test만 필터했는지 |
| 링크에 ID 대신 문자열이 남음 | rename한 `Trace ID` 열을 유지했는지, URL 토큰 철자 |
| 클릭하면 No trace found | datasource UID tempo, 원본 표의 ID로 Explore 직접 조회 |
| 상세 시간과 점 값이 다름 | span Duration과 trace duration의 구분, ns/ms/s 변환 |

## 7. 정상 상태 복구

```bash
kubectl -n sample-app set env deployment/fastapi TEST_DELAY_MS=0 TEST_FAILURE_MODE=none
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
```

완료 확인: 실제 요청 점을 클릭해 그 요청의 상세 시간 막대를 열었습니다. 다음 장에서 해당 요청의 로그까지 연결합니다.

[XY chart](https://grafana.com/docs/grafana/v13.2/visualizations/panels-visualizations/visualizations/xy-chart/) · [Tempo의 Spans 표](https://grafana.com/docs/grafana/v13.2/datasources/tempo/query-editor/traceql-editor/) · [같은 행의 값으로 Data link 구성](https://grafana.com/docs/grafana/v13.2/visualizations/panels-visualizations/configure-data-links/)

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../15-correlation/01-concept.md)
