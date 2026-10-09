# 02. 기본 CNI 없는 kind 2노드 만들기

선행 조건은 01장 도구 준비다. WSL Bash 저장소 루트에서 진행한다. kind 노드는 Docker 컨테이너이고, containerd가 내부 Pod 컨테이너를 실행한다.

```bash
source scripts/lib/common.sh
bash scripts/lab.sh prepare
kind create cluster --name "$LAB_NAME" \
  --config "$LAB_STATE_DIR/rendered/kind.yaml" --kubeconfig "$KUBECONFIG"
k get nodes -o wide
```

`prepare`는 소유권 marker·키·디렉터리와 YAML만 만들며 리소스를 배포하지 않는다. [renderer](../infrastructure/render.py)의 kind 설정은 `disableDefaultCNI: true`, control-plane 1개, worker 1개다. 각 노드의 `/var/local/observability`는 실습 전용 WSL 디렉터리에 연결한다. 기본 kindnet과 Cilium을 동시에 설치하지 않는다.

CNI를 설치하기 전 노드 NotReady·CoreDNS Pending은 정상 중간 상태다. 이름은 `observability-lab-control-plane`, `observability-lab-worker`로 나타나야 한다. 이미지와 digest는 [versions.env](../config/versions.env)에서 고정한다.

이미 같은 실습 클러스터가 있으면 수동으로 다시 생성하지 않는다. `bash scripts/steps/01-cluster.sh`는 소유 bind mount를 검사한 뒤 기존 클러스터를 재사용한다. 다른 용도의 같은 이름 클러스터에는 적용하지 않는다.

확인 과제: 렌더링된 kind YAML의 두 `extraMounts`를 찾아 host/container 경로 대응을 설명한다. 생성 실패 시 `docker info`, kind 오류, proxy 및 디스크 여유를 확인한다.

[kind 공식 문서](https://kind.sigs.k8s.io/docs/user/quick-start/), [다음: Cilium](03-cilium.md)
