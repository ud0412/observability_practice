# Dashboard 저장·export·import와 예시 JSON

예시 JSON은 직접 만들고 난 뒤 비교하는 복습 자료입니다. 자동 설치에서 provisioning하지 않습니다.

- [변수 없는 인프라](../../../infrastructure/grafana/dashboards/infrastructure-fixed.json)
- [변수 있는 인프라](../../../infrastructure/grafana/dashboards/infrastructure.json)
- [변수 없는 서비스](../../../samples/observability/dashboards/services-fixed.json)
- [변수 있는 서비스](../../../samples/observability/dashboards/services.json)
- [트레이스 점도표](../../../samples/observability/dashboards/traces.json)

## 직접 만든 것을 저장

Dashboard 상단 Save를 누르고 저장 창의 Save까지 눌러야 합니다. 브라우저를 닫았다가 다시 열어 Dashboard 목록에서 확인합니다.

## JSON export

저장한 Dashboard의 오른쪽 도구 모음 **Export 아이콘(상자에서 아래로 향하는 화살표)**을 선택해 JSON 내보내기 화면을 엽니다. **Export as JSON**에서 일반 export를 선택합니다. 외부용 데이터 소스 이름 치환 옵션은 기본 실습에서 사용하지 않습니다. **Download file**로 저장합니다.

Windows 저장 창에서 다음 관리 폴더를 선택합니다. 배포판 이름과 WSL 사용자 이름은 자신의 값으로 바꿉니다.

```text
\\wsl.localhost\Ubuntu-24.04\home\<WSL사용자>\.local\share\observability-practice\observability-lab\exports\
```

이 폴더의 export는 destroy에서 삭제됩니다. WSL 터미널에서는 `ls "$LAB_STATE_DIR/exports"`로 확인합니다.

## import로 다시 열기

**Dashboards → New → Import**로 들어갑니다. JSON 파일을 업로드하거나 내용을 붙여 넣고 Load를 선택합니다. 원래 Dashboard를 덮어쓰지 않도록 이름과 UID를 바꾼 다음 Import를 선택합니다. 데이터 소스를 묻는 화면이 나오면 Mimir·Loki·Tempo를 연결합니다.

예시는 classic dashboard JSON으로 제공되며 고정 datasource UID `mimir`, `loki`, `tempo`를 사용합니다. 실제 UI가 저장하면서 schema를 변환할 수 있습니다. 트레이스 예시의 열 이름은 실제 조회 표와 대조해야 합니다. 예시 import 성공과 직접 화면 실습 성공은 별도로 확인합니다.
