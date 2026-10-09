# 09. 인프라 Dashboard를 빈 화면부터 만들기

선행 조건은 08장 데이터 조회다. Windows Grafana UI에서 진행한다. 완성본 import 전에 쿼리의 의미를 확인하며 직접 만든다.

1. Explore의 Mimir에서 `node_cpu_seconds_total`의 label과 최근 값을 확인한다.
2. Dashboards → New dashboard → Add visualization에서 Mimir를 선택한다. 이름 `Lab Infrastructure`, folder `Practice`, 기본 시간 범위 최근 15분, refresh 30초로 저장한다.
3. Dashboard Settings → Variables에서 `cluster`와 `node` query variable을 만든다. cluster: `label_values(node_cpu_seconds_total, cluster)`, node: `label_values(node_cpu_seconds_total{cluster="$cluster"}, node)`. 기본은 단일 node 선택으로 시작한다.
4. 아래 패널을 하나씩 추가하고 unit·legend·threshold를 설정한다.

| 패널 | PromQL | 표시 |
|---|---|---|
| CPU 사용률 | `100 * (1 - avg by(node) (rate(node_cpu_seconds_total{cluster="$cluster",node=~"$node",mode="idle"}[5m])))` | Time series·percent 0~100·legend node |
| 메모리 사용률 | `100 * (1 - node_memory_MemAvailable_bytes{cluster="$cluster",node=~"$node"} / node_memory_MemTotal_bytes{cluster="$cluster",node=~"$node"})` | Gauge·percent·70/90 threshold |
| 파일시스템 사용률 | `100 * (1 - node_filesystem_avail_bytes{cluster="$cluster",node=~"$node",fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{cluster="$cluster",node=~"$node",fstype!~"tmpfs|overlay"})` | Time series·percent·legend mountpoint |
| Pod CPU | `sum by(namespace,pod) (rate(container_cpu_usage_seconds_total{cluster="$cluster",node=~"$node",container!="",container!="POD"}[5m]))` | Time series·CPU cores |
| Pod 메모리 | `sum by(namespace,pod) (container_memory_working_set_bytes{cluster="$cluster",node=~"$node",container!="",container!="POD"})` | Time series·bytes IEC |

Logs 패널에는 Loki를 선택하고 `{cluster="$cluster",node=~"$node",namespace="observability"}`를 입력한다. 시간을 바꾸고 node를 전환하여 panel filter가 동작하는지 확인한다. metric과 log 모두 같은 변수 label을 사용한다.

CPU rate는 누적 counter의 증가량이다. scrape 30초인 경우 5분 창은 여러 샘플을 포함한다. refresh를 1초로 바꿔도 새 scrape가 더 빨리 생기지 않는다. WSL 메모리·CPU의 관측 범위는 [07장](07-alloy.md)을 따른다. `No data`가 보이면 label·시간 범위·수집 대상부터 확인한다.

Dashboard를 저장하고 다시 연다. Export → JSON에서 provisioning용 외부 공유 옵션을 사용하지 않는 일반 JSON을 저장한다. Windows 파일 선택기에서 `\\wsl.localhost\Ubuntu-24.04\home\<WSL사용자>\.local\share\observability-practice\observability-lab\exports\`를 선택한다. 이후 다른 이름/UID로 import해 datasource UID 연결을 확인한다. 이 export도 destroy 대상이다.

확인 과제: 빈 Dashboard부터 작성한 뒤 [완성 예시](../infrastructure/grafana/dashboards/infrastructure.json)와 비교한다. Grafana Pod를 재생성하여 저장한 Dashboard가 유지되는지 [15장](15-persistence-and-destroy.md)에서 확인한다.

[Grafana Dashboard 제작](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/create-dashboard/), [다음: 자동 구축](10-automatic-setup.md)
