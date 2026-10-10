# Observability Practice — Basic / Korean

kubectl의 기본 명령을 사용할 수 있지만 Observability는 처음인 사람을 위한 과정입니다. 먼저 설명을 읽고, 바로 다음 실습 페이지에서 해당 구성 요소를 설치하거나 화면을 만들어 봅니다. 명령은 실습자가 직접 실행합니다.

선행 과정은 [WSL Kubernetes Practice Basic](https://github.com/ud0412/wsl_kubernetes_practice/tree/master/Guide/Basic/Korean)입니다. 그 저장소의 자동 스크립트로 kind·Cilium·Gateway API·Envoy Gateway를 준비한 뒤 이 과정을 시작합니다. 처음이라면 **00 설명 → 00 실습 → 01 설명** 순서로 읽으세요.

| 순서 | 주제 | 먼저 이해하기 | 따라 하기 |
|---|---|---|---|
| 00 | 시작과 선행 환경 | [설명](00-start/01-concept.md) | [실습](00-start/02-practice.md) |
| 01 | 숫자·로그·요청 흐름 | [설명](01-observability/01-concept.md) | [실습](01-observability/02-practice.md) |
| 02 | 저장 공간과 SeaweedFS S3 | [설명](02-storage/01-concept.md) | [실습](02-storage/02-practice.md) |
| 03 | 메트릭과 Mimir | [설명](03-mimir/01-concept.md) | [실습](03-mimir/02-practice.md) |
| 04 | 로그와 Loki | [설명](04-loki/01-concept.md) | [실습](04-loki/02-practice.md) |
| 05 | 트레이스와 Tempo | [설명](05-tempo/01-concept.md) | [실습](05-tempo/02-practice.md) |
| 06 | 노드 Alloy와 중앙 Alloy | [설명](06-alloy/01-concept.md) | [실습](06-alloy/02-practice.md) |
| 07 | Grafana 설치와 데이터 조회 | [설명](07-grafana/01-concept.md) | [실습](07-grafana/02-practice.md) |
| 08 | 첫 Dashboard와 숫자 패널 | [설명](08-first-dashboard/01-concept.md) | [실습](08-first-dashboard/02-practice.md) |
| 09 | 선·막대·게이지·표·로그 | [설명](09-visualizations/01-concept.md) | [실습](09-visualizations/02-practice.md) |
| 10 | 고정값을 변수로 바꾸기 | [설명](10-variables/01-concept.md) | [실습](10-variables/02-practice.md) |
| 11 | 세 서비스 빌드와 로그 | [설명](11-samples/01-concept.md) | [실습](11-samples/02-practice.md) |
| 12 | 서버 자동 계측 | [설명](12-otel/01-concept.md) | [실습](12-otel/02-practice.md) |
| 13 | 서비스 Dashboard | [설명](13-service-dashboard/01-concept.md) | [실습](13-service-dashboard/02-practice.md) |
| 14 | 트레이스 점에서 시간 막대로 | [설명](14-trace-scatter/01-concept.md) | [실습](14-trace-scatter/02-practice.md) |
| 15 | 같은 요청의 로그와 트레이스 | [설명](15-correlation/01-concept.md) | [실습](15-correlation/02-practice.md) |
| 16 | Pod 재시작과 전체 삭제 | [설명](16-preservation/01-concept.md) | [실습](16-preservation/02-practice.md) |

한 번에 인프라를 준비하려면 [자동 설치](automatic-setup.md)를 사용하세요. 이 경로도 선행 과정이 필요하고, FE·BE 샘플은 자동 설치하지 않습니다. 완료 후 07 실습의 데이터 조회부터 진행할 수 있습니다.

화면 기준은 **Grafana 13.2.3, 영어 UI, Windows 브라우저**입니다. 메뉴 이름은 화면에 있는 영어를 그대로 적었습니다. 터미널 명령은 별도 표시가 없으면 **WSL Ubuntu의 Bash, observability_practice 저장소 루트**에서 실행합니다. 새 터미널에서는 00 실습의 환경변수 설정을 반복하세요.

문서의 예상 화면은 설치 성공을 가정한 안내입니다. 현재 [확보된 실제 캡처와 화면 검증 범위](assets/README.md), [검증 기록](validation.md)을 확인할 수 있습니다. 실제 캡처가 없는 단계는 메뉴 경로·영역·버튼·다음 화면을 글로 안내합니다.

Basic에서 직접 만들 것은 인프라 Dashboard, 서비스 Dashboard, 트레이스 점도표와 상세 시간 막대입니다. 공개 Dashboard는 심화 과정에서 다룹니다.

- [버전과 호환성](appendix-versions.md)
- [화면에서 메뉴를 찾지 못할 때](screen-help.md)
- [예시 JSON 사용법과 export/import](dashboard-files.md)
