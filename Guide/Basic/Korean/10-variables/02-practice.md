# 10 실습 — 만든 패널을 변수 방식으로 변경

시작 조건: 09 실습 Dashboard 저장 완료. Windows Grafana에서 진행합니다. 이전 쿼리를 새로 만드는 대신 기존 패널을 고칩니다.

## 1. 노드 선택 변수 생성

1. `Lab Infrastructure Basic`을 열고 **Edit**를 누릅니다.
2. 오른쪽 파란 **+ → Add 영역의 Dashboard controls → Variable**을 선택합니다. 첫 Dashboard 캡처의 오른쪽 아래에 있는 버튼입니다.
3. 변수 종류를 **Query**로 선택합니다.
4. **Name=node**, **Label=노드**, **Display=Above dashboard**로 설정합니다.
5. **Open variable editor**를 선택합니다.
6. **Target data source=Mimir**, **Query type=Label values**, **Label=node**, **Metric=node_cpu_seconds_total**로 설정합니다.
7. 위쪽 **Preview**를 누릅니다. 값 목록에 `observability-lab-control-plane`, `observability-lab-worker`가 보여야 합니다.
8. **Apply**로 편집기를 닫고 **Refresh=On dashboard load**로 설정합니다.
9. 처음에는 **Multi-value**와 **Include All value**를 끈 상태로 저장합니다.

`label_values(node_cpu_seconds_total, node)`는 이 변수 조회의 의미를 표현한 문장입니다. Explore의 PromQL 입력칸에 붙여 넣는 문장이 아닙니다. 값을 못 찾으면 Metric과 Label의 철자를 확인합니다.

## 2. 첫 Stat 패널부터 변경

Dashboard의 노드 선택 목록에서 worker를 고릅니다. Stat 패널 제목의 메뉴 **Edit**로 패널 편집에 들어갑니다. 기존 쿼리를 교체합니다.

```promql
up{job="node",node=~"${node:regex}"}
```

Refresh로 값 `1`을 확인합니다. 제목을 `메트릭 수집 상태 — $node`로 바꾸고 저장합니다. Dashboard의 노드를 control-plane으로 바꿔 제목과 결과가 함께 변경되는지 확인합니다.

## 3. 선그래프와 게이지 변경

CPU 패널의 쿼리입니다.

```promql
100 * (1 - avg by(node) (rate(node_cpu_seconds_total{node=~"${node:regex}",mode="idle"}[5m])))
```

메모리 패널의 쿼리입니다. **분자와 분모를 모두** 변경합니다.

```promql
100 * (1 - node_memory_MemAvailable_bytes{node=~"${node:regex}"} / node_memory_MemTotal_bytes{node=~"${node:regex}"})
```

Logs 패널도 변경합니다.

```logql
{namespace="observability",node=~"${node:regex}"}
```

막대·가로 계기판·표 패널도 메모리 쿼리로 교체하면 같은 선택에 반응합니다. 패널별 조회 Type·Format·시각화는 이전 설정을 유지합니다. 하나씩 고치고 저장하세요.

Pod CPU·메모리·파일시스템 패널도 `node="observability-lab-worker"`를 `node=~"${node:regex}"`로 교체합니다. 파일시스템 쿼리는 분자·분모 두 곳 모두 바꿉니다. 여러 노드를 동시에 볼 때 파일시스템 Legend는 `{{node}} / {{mountpoint}}`로 바꿔 같은 mountpoint 이름을 구분합니다.

## 4. 다중 선택과 전체 선택

1. Dashboard **Edit** 상태에서 node 선택 컨트롤을 클릭하여 오른쪽 변수 설정을 엽니다.
2. **Selection options → Multi-value**와 **Include All value**를 켭니다.
3. **Custom all value**가 표시되면 비워 둡니다. Grafana가 목록 값을 조합하게 합니다.
4. Save 후 두 노드를 선택하고, 다음에는 **All**을 선택합니다.

정상 결과: CPU 선이 두 개, 메모리 게이지도 노드별로 표시됩니다. 여러 노드의 수집 상태를 하나로 합치지 않도록 Stat 패널의 **Value options → Show=All values**를 선택할 수 있습니다. Legend `{{node}}`로 이름을 구분합니다.

## 5. 변경 완료 확인

- node를 바꾸면 메트릭과 Logs가 함께 바뀝니다.
- 단일·다중·All 선택에서 No data가 생기지 않습니다.
- 제목이 필요 이상 길면 제목에서 `$node`를 빼고 범례로 노드를 표시합니다.

메트릭은 바뀌는데 로그가 안 바뀌면 Logs 쿼리도 수정했는지 확인합니다. 다중 선택만 실패하면 `=` 대신 `=~`와 `${node:regex}`를 사용했는지 확인합니다.

[현재 UI의 변수 추가](https://grafana.com/docs/grafana/v13.2/visualizations/dashboards/variables/add-template-variables/) · [변수 문법](https://grafana.com/docs/grafana/v13.2/visualizations/dashboards/variables/variable-syntax/)

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../11-samples/01-concept.md)
