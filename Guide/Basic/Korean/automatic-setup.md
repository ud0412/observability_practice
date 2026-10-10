# Grafana까지 자동 설치하기

자동 설치는 수동 실습의 같은 설정을 사용합니다. FE·BE 샘플은 설치하지 않습니다. 설명을 읽으며 설치하려면 [목차](README.md)의 00부터 진행합니다.

두 저장소 준비와 선행 revision 고정은 [00 실습](00-start/02-practice.md)의 1번을 먼저 따릅니다.

실행 위치: WSL Bash. WSL 설정과 Docker Engine·도구 준비는 [선행 교본](https://github.com/ud0412/wsl_kubernetes_practice/tree/master/Guide/Basic/Korean)에서 먼저 완료합니다.

```bash
cd ~/practice/wsl_kubernetes_practice
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
bash scripts/lab.sh up
cd ../observability_practice
export WSL_KUBERNETES_REPO="$HOME/practice/wsl_kubernetes_practice"
export LAB_STATE_DIR="$HOME/.local/share/observability-practice/observability-lab"
export KUBECONFIG="$LAB_STATE_DIR/kubeconfig"
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
bash scripts/lab.sh up
bash scripts/lab.sh access
```

`up`은 선행 환경 검사 → 저장 공간과 SeaweedFS → 백엔드 → Alloy → Grafana 순서입니다. 실패하면 표시된 구성 요소의 Pod 로그와 Events를 확인한 후 다시 실행합니다. 기존 저장 데이터와 키를 유지하며 적용합니다.

Windows에서 `http://localhost:8080/grafana/`를 열고 [07 실습](07-grafana/02-practice.md)의 로그인·조회부터 진행합니다. 자동 설치는 Dashboard를 대신 만들어 주지 않습니다. 직접 작성 실습을 위해 빈 상태로 시작합니다.

| 명령 | 역할 |
|---|---|
| prepare | 선행 환경 확인, 설치 YAML과 키 준비 |
| up | Observability만 설치 |
| verify | Pod·PVC·Grafana route 준비 확인 |
| status | 노드·Pod·PVC 확인 |
| access | localhost Grafana 접속 통로 열기 |
| destroy | 선행 클러스터와 모든 관리 실습 데이터 삭제 |

verify 성공은 실제 데이터 수집·S3 업로드·재시작 보존까지 검사했다는 뜻이 아닙니다. 각 실습의 완료 기준을 따릅니다. [전체 종료 방법](16-preservation/02-practice.md)을 확인하세요.
