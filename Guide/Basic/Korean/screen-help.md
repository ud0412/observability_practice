# 화면에서 버튼을 찾지 못할 때

이 교본은 Grafana 13.2.3 영어 UI를 기준으로 합니다. 먼저 `kubectl -n observability get deployment grafana -o jsonpath='{.spec.template.spec.containers[0].image}'`로 `grafana/grafana:13.2.3`인지 확인합니다.

| 하려는 일 | 진입 경로와 위치 | 다음에 보여야 할 것 |
|---|---|---|
| 메트릭·로그 먼저 보기 | 왼쪽 메뉴 Explore → 왼쪽 위 데이터 소스 | 쿼리 입력 영역과 Run query |
| 새 Dashboard | 왼쪽 Dashboards → New → New dashboard | 가운데 New dashboard, 오른쪽 Add |
| 패널 추가 | Edit 상태 → 오른쪽 끝 파란 + → Panel 상자 안 큰 + | 새 패널과 Configure visualization |
| 기존 패널 편집 | 패널 위에 마우스 → 제목 근처 메뉴 → Edit | 미리보기와 아래 Queries |
| 표현 변경 | 편집 화면의 현재 시각화 이름 또는 All visualizations | 시각화 검색 목록 |
| 숫자 단위 | 패널 편집 오른쪽 Standard options → Unit | 단위 검색/선택 |
| 변수 추가 | Dashboard Edit → 오른쪽 + → Dashboard controls → Variable | 변수 종류와 Name 설정 |
| 변수 편집 | Edit 상태에서 해당 선택 컨트롤 클릭 | 오른쪽 변수 설정 |
| 조회한 원본 표 보기 | 패널 편집 미리보기의 Table view | 데이터 행·열 |
| 데이터 열 정리 | 패널 편집 아래 Transformations → Add transformation | 변환 선택 목록 |
| 저장 | 위쪽 Save → 저장 창 Save | 저장된 Dashboard |

새 화면에서 과거의 `Add visualization`이나 `Dashboard Settings → Variables` 메뉴를 찾지 않습니다. 현재 화면에서는 Add 영역과 Variable 컨트롤을 사용합니다. 오른쪽 영역이 닫혀 있으면 파란 +로 엽니다. 영역 안 옵션이 많으면 오른쪽 영역 자체를 스크롤합니다.

버튼 이름이 다르면 먼저 버전과 화면 언어를 확인합니다. 같은 버전에서 경로가 다르면 실제 화면을 기준으로 기록하고 교본을 보완합니다. 캡처가 있는 시작 화면은 [첫 Dashboard 실습](08-first-dashboard/02-practice.md)에서 볼 수 있습니다.
