# 00. 무엇을 관찰하는가

metric은 CPU·요청 수 같은 수치, log는 특정 시점의 사건 기록, trace는 한 요청이 여러 서비스에서 처리되는 시간과 관계다. Grafana는 조회 화면이고 데이터를 저장하는 백엔드는 각각 Mimir, Loki, Tempo다.

노드 Alloy는 모든 kind 노드에서 실행한다. 내장 unix exporter로 노드 metric, kubelet/cAdvisor로 컨테이너 metric, 해당 노드의 파일에서 container log를 수집한다. 중앙 Alloy는 서버 앱의 OTLP metric·trace를 받아 변환·전송한다. Prometheus server나 별도 node-exporter는 추가하지 않는다.

SeaweedFS는 S3 API를 제공하며 객체 자체는 이 PC의 디스크에 보관한다. Mimir/Loki/Tempo가 S3에 블록을 업로드하기 전의 WAL과 작업 파일에는 별도 영속 디스크가 필요하다. WAL은 복구를 위해 먼저 기록하는 Write-Ahead Log다.

| 구성요소 | 배치 | 영속 상태 |
|---|---|---|
| Mimir/Loki/Tempo | 각 1 Pod·단일 프로세스 | WAL, 작업 디렉터리, S3 블록 |
| SeaweedFS mini | 1 Pod | 객체 파일·filer metadata |
| 노드 Alloy | DaemonSet·노드당 1개 | 읽기 위치·remote_write WAL |
| 중앙 Alloy | Deployment 1개 | metric remote_write WAL |
| Grafana | Deployment 1개 | SQLite DB·사용자 작성 Dashboard |

모든 관리 상태는 WSL의 `~/.local/share/observability-practice/observability-lab` 아래에 둔다. Pod 장애 복구와 전체 실습 삭제를 구분한다. local PV는 원래 노드에 묶이므로 전체 노드 장애에 대한 HA 실습은 아니다.

확인 과제: stdout log가 중앙 Alloy를 거치는지, trace가 Loki에 저장되는지, S3가 있는데 왜 WAL이 필요한지 설명한다.

[다음: WSL·도구](01-wsl-and-tools.md)
