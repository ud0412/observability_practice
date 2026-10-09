# 실습 교본 목차

명령의 실행 위치는 각 장에 표시한다. `k`는 전용 kubeconfig/context를 지정하는 kubectl 함수이며 01장에서 정의한다. 자동 구축과 수동 경로는 같은 renderer·config·values를 사용한다.

| 순서 | 실습 | 완료 기준 |
|---|---|---|
| 00 | [전체 구조](00-overview.md) | 각 신호의 수집·저장·조회 경로 설명 |
| 01 | [WSL·도구](01-wsl-and-tools.md) | Docker/도구/WSL 사전 점검 통과 |
| 02 | [kind](02-kind.md) | 기본 CNI 없는 2노드 생성 |
| 03 | [Cilium](03-cilium.md) | 노드 Ready, DNS/Pod 통신 확인 |
| 04 | [Envoy Gateway](04-envoy-gateway.md) | Gateway Accepted, 데이터 평면 구분 |
| 05 | [영속 저장소·SeaweedFS](05-storage-and-seaweedfs.md) | PVC·S3 인증·객체 저장 확인 |
| 06 | [Mimir·Loki·Tempo](06-mimir-loki-tempo.md) | 세 단일 프로세스 백엔드 Ready |
| 07 | [Alloy](07-alloy.md) | 노드별 수집 및 OTLP 경로 확인 |
| 08 | [Grafana](08-grafana.md) | Envoy 경유 접속·데이터 소스 확인 |
| 09 | [인프라 Dashboard 제작](09-dashboard-infrastructure.md) | 쿼리·변수·패널 직접 작성 |
| 10 | [자동 구축](10-automatic-setup.md) | 동일 인프라 생성·재실행 |
| 11 | [샘플 빌드·배포](11-sample-build-and-deploy.md) | 버튼으로 두 서버 호출 |
| 12 | [서버 OTel 자동 계측](12-server-otel-instrumentation.md) | metric·trace·log context 확인 |
| 13 | [서비스 Dashboard 제작](13-dashboard-services.md) | 처리율·오류율·p95·log 패널 작성 |
| 14 | [연결·문제 분석](14-correlation-and-troubleshooting.md) | 같은 요청의 log↔trace, 오류 분석 |
| 15 | [Pod 장애 보존·destroy](15-persistence-and-destroy.md) | 재생성 후 보존, 종료 후 전체 삭제 |

부록: [버전](appendix-versions.md), [Podman](appendix-podman.md), [검증](validation.md).

자동 경로를 선택해도 00~01, 09, 11~15장의 학습은 수행한다. 10장 자동 설치는 02~08장 결과를 만들어 준다.
