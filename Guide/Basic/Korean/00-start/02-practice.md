# 00 실습 — 선행 환경을 준비하고 확인하기

실행 위치: **WSL Ubuntu Bash**. 선행 과정에서 WSL·Docker Engine·kind·kubectl·Helm 설치를 완료해야 합니다. 처음부터 새로 한다면 아래 clone부터 진행합니다.

## 1. 두 저장소를 같은 폴더에 준비

```bash
mkdir -p ~/practice
cd ~/practice
git clone https://github.com/ud0412/wsl_kubernetes_practice.git
git clone https://github.com/ud0412/observability_practice.git
```

이미 clone했다면 clone을 반복하지 않고 각 저장소에서 변경 사항을 확인한 뒤 업데이트하세요. Windows의 `C:` 폴더보다 WSL의 `~/practice`에서 빌드하는 편이 파일 작업에 유리합니다.

선행 과정 버전은 [검증한 revision](../../../../config/prerequisite-revision.txt)에 기록했습니다. 이 교본과 동일한 소스를 사용하려면 `~/practice`에서 다음으로 맞춥니다. 선행 저장소에 수정 중인 파일이 있다면 그 변경을 먼저 보관합니다.

```bash
git -C wsl_kubernetes_practice checkout "$(cat observability_practice/config/prerequisite-revision.txt)"
```

이후 선행 저장소가 detached HEAD라고 표시되는 것은 해당 버전으로 소스를 고정한 상태입니다.

## 2. Kubernetes 선행 과정의 자동 구축

```bash
cd ~/practice/wsl_kubernetes_practice
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
bash scripts/lab.sh up
bash scripts/lab.sh verify
```

정상 결과: `Foundation ready`와 노드·Cilium·Gateway 준비 완료 메시지. 여기에 Observability는 아직 설치되지 않습니다. 선행 과정의 수동 실습을 이미 끝냈다면 `verify`만 실행하여 완료 기록을 만드세요.

기존 통합 교본으로 만든 `observability-lab`도 같은 저장 경로를 사용합니다. 선행 과정 `up`은 소유권을 확인한 기존 노드를 재사용합니다. 소유권이 다르다는 오류가 나면 클러스터를 임의로 덮어쓰지 말고 선행 과정의 종료 안내를 확인하세요.

## 3. Observability 저장소와 접속 정보 설정

```bash
cd ~/practice/observability_practice
export WSL_KUBERNETES_REPO="$HOME/practice/wsl_kubernetes_practice"
export LAB_STATE_DIR="$HOME/.local/share/observability-practice/observability-lab"
export KUBECONFIG="$LAB_STATE_DIR/kubeconfig"
kubectl config current-context
kubectl get nodes
```

정상 결과: context는 `kind-observability-lab`, 노드는 `observability-lab-control-plane`, `observability-lab-worker` 두 개이며 모두 `Ready`입니다. **새 WSL 터미널을 열 때마다 위 세 export와 cd를 반복**합니다. 실제 clone 위치가 다르면 첫 export 경로를 맞춥니다.

## 4. 실습 파일 준비

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
bash scripts/lab.sh prepare
```

`prepare`는 Kubernetes를 만들지 않습니다. 선행 환경을 확인하고, 키·비밀번호와 설치용 YAML을 관리 경로에 준비합니다. 여기서 비밀번호를 공개 문서에 복사하지 않습니다.

```bash
ls "$LAB_STATE_DIR/rendered"
```

`storage.yaml`, `seaweedfs.yaml`, `mimir.yaml`, `loki.yaml`, `tempo.yaml`, `alloy.yaml`, `grafana.yaml`, `grafana-route.yaml`이 보이면 다음 장으로 넘어갑니다.

| 막힌 상황 | 확인할 곳 |
|---|---|
| prerequisite checkout 오류 | WSL_KUBERNETES_REPO가 clone한 저장소의 절대 경로인지 |
| foundation.json 없음/불일치 | 선행 저장소에서 `bash scripts/lab.sh verify`를 수행했는지 |
| kubectl 접속 오류 | KUBECONFIG와 current-context, Docker Engine 실행 여부 |
| 메모리 부족 | 선행 과정의 WSL 설정에서 12~16GB 할당 |

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../01-observability/01-concept.md)
