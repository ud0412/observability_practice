# 07 실습 — Grafana 설치와 첫 조회

시작 조건: 06 실습 완료. 설치는 WSL Bash, 화면 조회는 Windows 브라우저에서 합니다.

## 1. 설치와 Gateway 연결

```bash
kubectl apply -f "$LAB_STATE_DIR/rendered/grafana.yaml"
kubectl -n observability rollout status deployment/grafana --timeout=450s
kubectl apply -f "$LAB_STATE_DIR/rendered/grafana-route.yaml"
bash scripts/lab.sh verify
bash scripts/lab.sh access
```

정상 결과: Grafana 주소 `http://localhost:8080/grafana/`. access는 Windows에서 접속할 통로를 백그라운드로 열고 관리 PID를 기록합니다. 이미 실행 중이라는 메시지면 새 통로를 중복 실행하지 않고 기존 주소를 엽니다.

## 2. 로그인

WSL에서 비밀번호를 확인합니다. 자기 실습 PC에서만 확인하고 화면 캡처에 포함하지 않습니다.

```bash
.venv/bin/python -c 'import json,os; print(json.load(open(os.environ["LAB_STATE_DIR"]+"/credentials.json"))["GRAFANA_PASSWORD"])'
```

Windows 브라우저에서 위 Grafana 주소를 엽니다. 사용자 이름은 `admin`, 비밀번호는 출력된 값입니다. 로그인 후 왼쪽 메뉴가 접혀 있으면 왼쪽 위 메뉴 아이콘으로 펼칩니다.

## 3. 메트릭이 들어오는지 확인

1. 왼쪽 주 메뉴에서 **Explore**를 선택합니다.
2. Explore 화면 왼쪽 위 데이터 소스 목록에서 **Mimir**를 선택합니다.
3. 오른쪽 위 시간 범위를 **Last 15 minutes**로 설정합니다.
4. 쿼리 편집기의 **Code**를 선택하여 아래 문장을 붙여 넣습니다.

```promql
up{job="node"}
```

5. **Run query**를 누릅니다. 초기 수집에는 30~60초가 걸릴 수 있습니다.
6. 결과의 label에 두 노드 이름이 있고 값이 `1`인지 확인합니다.

`1`은 메트릭 수집 성공입니다. 노드의 모든 상태가 정상이라는 의미는 아닙니다.

## 4. 로그가 들어오는지 확인

1. 같은 화면의 데이터 소스를 **Loki**로 바꿉니다.
2. 쿼리를 직접 입력하는 **Code** 모드에서 다음을 입력합니다.

```logql
{namespace="observability"}
```

3. **Run query**를 누릅니다. 시간·서비스·로그 메시지가 보이면 성공입니다.
4. 로그 한 줄을 눌러 상세 label을 펼칩니다. namespace·pod·node를 확인합니다.

Tempo는 이 단계에서 조회 결과가 없어도 정상입니다. 12 실습에서 서버 트레이스를 보냅니다.

## 5. 컨테이너 메트릭도 확인

Explore에서 Mimir를 다시 선택하고 아래를 실행합니다.

```promql
sum by(namespace,pod) (container_memory_working_set_bytes{container!="",container!="POD"})
```

namespace·pod 이름별 숫자가 보이면 cAdvisor 수집도 동작합니다. 값의 단위는 bytes이며, 빈 container와 Pod 기반 컨테이너 항목을 제외해 실제 작업 컨테이너만 조회합니다. 다음 장에서 노드와 Pod의 사용량을 구분하여 표현합니다.

| 문제 | 확인 방법 |
|---|---|
| 주소 접속 실패 | WSL의 access 결과, `kubectl -n observability get httproute grafana` |
| 로그인 실패 | 관리 credentials.json의 현재 비밀번호인지 |
| 데이터 소스 없음 | 왼쪽 **Connections → Data sources**에서 세 소스 확인, Grafana Pod 로그 |
| Mimir No data | 06 실습 Alloy Ready·로그, 시간 범위를 최근 15분으로 변경 |
| Loki 빈 결과 | 1분 기다린 뒤 다시 조회, `{namespace="observability"}` 철자 확인 |

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../08-first-dashboard/01-concept.md)
