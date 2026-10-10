# 09 실습 — 선·막대·호형 게이지·표·로그 만들기

시작 조건: `Lab Infrastructure Basic`에 Stat 패널 저장 완료. Windows Grafana에서 진행합니다. 아직 사용자 변수는 만들지 않습니다.

## 모든 패널의 공통 시작과 저장

Dashboard를 열고 **Edit → 오른쪽 파란 + → Panel 상자 → Configure visualization**을 선택합니다. Queries 탭에서 데이터 소스를 선택하고 Code 모드에 쿼리를 입력합니다. Refresh로 데이터가 나온 뒤 시각화를 고릅니다. 각 패널을 마칠 때 **Save → 저장 창 Save → Back**으로 돌아옵니다. 아래 실습을 한 번에 입력하지 않고 하나씩 완성하세요.

## 1. CPU 사용률 선그래프

데이터 소스 Mimir에 다음을 입력합니다.

```promql
100 * (1 - avg by(node) (rate(node_cpu_seconds_total{node="observability-lab-worker",mode="idle"}[5m])))
```

이 숫자는 최근 5분 동안 CPU가 쉬고 있지 않은 비율입니다. `rate`는 누적 기록의 증가 속도를 구합니다. 처음 설치한 직후에는 충분한 샘플이 모일 때까지 기다립니다.

1. 시각화 목록에서 **Time series**를 선택합니다.
2. **Panel options → Title**은 `Worker CPU 사용률`로 설정합니다.
3. 오른쪽 **Graph styles → Style**은 **Lines**로 설정합니다.
4. **Standard options → Unit**에서 `Percent (0-100)`을 검색해 선택합니다.
5. **Min=0, Max=100, Decimals=1**로 설정합니다.
6. 쿼리 A의 **Legend**를 **Custom**으로 바꾸고 `{{node}}`를 입력합니다.
7. 저장합니다.

확인: 가로축은 시각, 세로축은 %입니다. 범례는 worker 이름입니다. 값이 낮거나 변화가 작아도 수집이 정상이라면 성공입니다.

## 2. 메모리 사용률 호형 게이지

새 패널의 Mimir 쿼리입니다.

```promql
100 * (1 - node_memory_MemAvailable_bytes{node="observability-lab-worker"} / node_memory_MemTotal_bytes{node="observability-lab-worker"})
```

1. 시각화 **Gauge**, 제목 `Worker 메모리 사용률`을 선택합니다.
2. **Value options → Calculation → Last * (not null)**을 선택합니다.
3. **Gauge options → Style → Arc**를 선택합니다. Circle은 원형 표현입니다.
4. **Standard options → Unit=Percent (0-100), Min=0, Max=100, Decimals=1**로 설정합니다.
5. 오른쪽 **Thresholds**에서 **Thresholds mode=Absolute**를 선택합니다.
6. Base 색을 녹색으로 두고 **Add threshold**로 `70` 노란색, `90` 빨간색을 추가합니다.
7. **Gauge options → Show thresholds**를 켜서 기준 구간을 확인하고 저장합니다.

확인: 현재 사용률과 0~100 범위가 표시됩니다. 값이 70 미만이면 녹색입니다. 값을 강제로 높일 필요는 없습니다.

## 3. 노드별 비교 막대그래프

새 패널에 아래 쿼리를 입력합니다. 이번에는 특정 node 필터를 빼서 두 노드를 모두 조회합니다.

```promql
100 * (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)
```

1. 쿼리 A의 **Options**를 펼칩니다. **Type=Instant**, **Format=Table**을 선택합니다.
2. Refresh를 누른 뒤 미리보기의 **Table view**를 켭니다. `node` 문자열 열과 숫자 값 열, 두 행이 있는지 확인합니다.
3. Table view를 끄고 시각화 **Bar chart**를 선택합니다.
4. 오른쪽 **Bar chart options → X Axis**를 `node`로 선택합니다. 문자열 대상 열을 선택하는 설정입니다.
5. **Orientation=Vertical**, Unit은 Percent (0-100), Min=0, Max=100으로 설정합니다.
6. 제목은 `노드별 메모리 사용률 비교`로 저장합니다.

확인: 두 노드의 막대가 보입니다. 두 kind 노드는 WSL 자원을 공유하므로 서로 다른 PC의 메모리 사용률로 해석하지 않습니다. 두 값을 더하지 않습니다.

## 4. 같은 데이터를 가로 계기판으로 표현

새 패널에 3번 쿼리를 입력합니다. **Type=Instant**, **Format=Time series**로 설정하고 Legend를 `{{node}}`로 설정합니다.

시각화 **Bar gauge**, 제목 `노드 메모리 가로 계기판`, **Value options → Calculation=Last * (not null)**, **Orientation=Horizontal**로 설정합니다. Unit·Min·Max·Thresholds는 2번처럼 설정합니다.

확인: 노드마다 이름과 가로 막대가 나타납니다. 선그래프는 이전 변화를, 가로 계기판은 현재 비교를 보기 좋다는 차이를 설명해 보세요.

## 5. 정확한 값은 표로 확인

새 패널에 3번 쿼리를 입력하고 **Type=Instant, Format=Table**, 시각화 **Table**을 선택합니다. 제목은 `노드 메모리 사용률 표`로 설정합니다. 값 열의 Unit을 Percent (0-100)으로 지정합니다.

열을 정리하려면 쿼리 아래 **Transformations → Add transformation → Organize fields by name**을 선택합니다. `node`와 값 열을 남기고 필요 없는 열을 눈 아이콘으로 숨깁니다. 숫자 값 열의 표시 이름을 `메모리 사용률`로 바꿉니다. 여러 frame 오류가 보이면 Query Format이 Table인지 다시 확인합니다.

확인: 두 노드의 정확한 숫자를 표에서 읽을 수 있습니다.

## 6. 로그 패널 만들기

새 패널의 데이터 소스를 **Loki**로 바꾸고 Code 모드에 입력합니다.

```logql
{namespace="observability",node="observability-lab-worker"}
```

시각화 **Logs**, 제목 `Worker의 Observability 로그`를 선택합니다. 오른쪽 **Logs options**에서 시간 표시와 긴 메시지 줄바꿈을 켭니다. 로그 한 줄을 클릭하면 상세 label이 보입니다.

## 7. Pod 사용량 선그래프

이번에는 노드 전체가 아니라 worker에서 실행 중인 Pod를 봅니다. 새 Mimir 패널에 아래를 입력합니다.

```promql
sum by(namespace,pod) (rate(container_cpu_usage_seconds_total{node="observability-lab-worker",container!="",container!="POD"}[5m]))
```

Time series, 제목 `Worker의 Pod CPU`, Unit은 `Cores`, Legend는 `{{namespace}} / {{pod}}`로 설정합니다. 값이 0.1이면 CPU 하나의 약 10%만큼 사용한 것입니다.

다른 새 패널에는 메모리 쿼리를 입력합니다.

```promql
sum by(namespace,pod) (container_memory_working_set_bytes{node="observability-lab-worker",container!="",container!="POD"})
```

Time series, 제목 `Worker의 Pod 메모리`, Unit은 `Bytes (IEC)`, Legend는 같은 형식으로 설정합니다. MiB/GiB로 값이 표시되는지 확인하고 저장합니다.

## 8. 파일시스템 공간 사용률

새 Mimir 패널에 입력합니다.

```promql
100 * (1 - node_filesystem_avail_bytes{node="observability-lab-worker",fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{node="observability-lab-worker",fstype!~"tmpfs|overlay"})
```

Time series, 제목 `Worker의 파일시스템 사용률`, Unit=Percent (0-100), Min=0, Max=100, Legend=`{{mountpoint}}`로 설정합니다. 이름이 다른 파일시스템들의 선을 구분합니다. 관측 대상은 kind 노드의 파일시스템이고 Windows의 모든 드라이브가 아닙니다.

완료 확인: 첫 Stat과 여러 표현 방식, Pod·파일시스템 패널을 저장했습니다. 아직 선택 목록은 없습니다. 다음 장에서 직접 입력한 node 이름을 변수로 바꿉니다.

[Gauge](https://grafana.com/docs/grafana/v13.2/visualizations/panels-visualizations/visualizations/gauge/) · [Bar chart](https://grafana.com/docs/grafana/v13.2/visualizations/panels-visualizations/visualizations/bar-chart/) · [Mimir에서 사용하는 Prometheus 조회 옵션](https://grafana.com/docs/grafana/v13.2/datasources/prometheus/query-editor/)

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../10-variables/01-concept.md)
