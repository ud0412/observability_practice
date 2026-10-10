# 16 실습 — Pod 재시작과 전체 삭제

시작 조건: 15 실습까지 완료. WSL Bash의 환경변수는 00 실습을 따릅니다. S3 확인은 02 실습처럼 별도 터미널에 port-forward를 실행합니다.

보존은 보존 기간 내 **백엔드에 저장된 데이터와 PVC/WAL 상태**를 기준으로 한다. 앱 SDK/collector의 전송 전 메모리 버퍼까지 무손실이라는 의미는 아니다. local PV는 원래 worker에 묶이며 노드 자체 손실에 대한 HA 구성은 아니다.

먼저 Grafana에서 metric·서버 log·trace를 조회해 시간 범위와 trace ID를 기록한다. 직접 만든 Dashboard를 저장하고 export는 관리 경로에 둔다. S3 객체 보존은 별도 port-forward를 유지한 상태에서 다음으로 준비한다.

```bash
.venv/bin/python scripts/check-s3.py --keep
```

다른 터미널에서 상태 서비스를 **하나씩** 재생성하고 매번 Ready를 기다린다.

```bash
kubectl -n storage delete pod -l app=seaweedfs
kubectl -n storage rollout status deployment/seaweedfs --timeout=450s
for component in mimir loki tempo alloy-central grafana; do
  kubectl -n observability delete pod -l "app=$component"
  kubectl -n observability rollout status "deployment/$component" --timeout=450s
done
kubectl -n observability delete pod -l app=alloy-node
kubectl -n observability rollout status daemonset/alloy-node --timeout=300s
```

SeaweedFS 재생성으로 기존 port-forward가 종료되었다면 다시 시작한다. 업로드 없이 기존 객체를 조회한다.

```bash
.venv/bin/python scripts/check-s3.py --read-existing
```

Grafana 접근용 port-forward도 필요하면 access를 다시 실행한다. 이전 시간 범위의 metric·log·trace 및 저장한 Dashboard를 다시 확인한다. PVC를 삭제하지 않았고 동일 claim이 사용되는지 `kubectl get pvc,pv -A`로 확인한다. 이미 저장된 기록은 남고 재생성 이후 새 수집도 이어져야 한다.

실습을 끝낼 때는 다음을 실행한다.

```bash
bash scripts/lab.sh destroy
# 재실행도 안전해야 한다.
bash scripts/lab.sh destroy
```

| 제거 대상 | 범위 |
|---|---|
| kind 클러스터 | 노드 컨테이너·리소스·수동 배포 sample-app 포함 |
| 관리 저장 경로 | S3 객체/metadata, PVC 실체, WAL, Alloy 상태, Grafana DB/Dashboard |
| 생성 상태 | 전용 kubeconfig·키·비밀번호·export·로그·관리 port-forward |

destroy는 Docker label과 정확한 bind mount, 경로·소유 marker·symlink 경계를 검사한다. root 소유 PVC 파일을 지우는 데 sudo가 필요할 수 있다. 경로 확인을 통과한 실습 디렉터리만 삭제한다. 삭제 오류가 있으면 non-zero로 실패하고 남은 대상 확인 후 재실행한다.

교본·샘플 소스·제공 예시 JSON·공유 설치 도구·공유 이미지 cache는 실습 생성 데이터가 아니다. destroy는 전역 Docker prune을 실행하지 않는다. 관리 경로 밖으로 사용자가 복사한 export는 자동 삭제 범위 밖이므로 기본 export 위치를 따른다. 수동으로 별도 실행한 S3 port-forward는 Ctrl+C로 종료한다.

완료 기준은 `kind get clusters`에 실습이 없고, `test ! -e "$LAB_STATE_DIR"`가 성공하며, 관리 access 프로세스가 종료된 것이다. 재시작하려면 선행 저장소에서 `up`으로 Kubernetes를 준비하고, Observability 저장소에서 `up`을 실행합니다. 새 키와 빈 저장소로 시작합니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../README.md)
