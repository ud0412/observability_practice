# 05. local PV와 SeaweedFS S3

WSL Bash에서 정적 local PV 6개와 `lab-local` StorageClass를 적용한다. 추가 provisioner Pod를 실행하지 않는다. 각 PV는 worker의 `/var/local/observability/<service>`에 연결된다. StorageClass의 Retain은 PVC를 삭제해도 파일을 자동 폐기하지 않는 정책이며, 최종 `destroy`가 host 파일까지 정리한다.

```bash
source scripts/lib/common.sh
k apply -f "$LAB_STATE_DIR/rendered/storage.yaml"
k get pv
k get pvc -A
k apply -f "$LAB_STATE_DIR/rendered/seaweedfs.yaml"
k -n storage rollout status deployment/seaweedfs --timeout=450s
k -n storage get pvc,pods,svc
```

WaitForFirstConsumer PVC는 workload가 배치되기 전 Pending일 수 있다. SeaweedFS PVC는 배포 후 Bound여야 한다. PV의 capacity 숫자는 예약·quota를 강제하는 실제 디스크 크기가 아니다. host 디스크 여유를 함께 확인한다.

`weed mini -dir=/data`는 master/volume/filer/S3를 한 프로세스로 실행한다. `/data` 전체를 PVC에 두어 filer metadata도 보존한다. 초기 버킷은 `mimir-blocks`, `loki-data`, `tempo-traces`다. 재시작 시 기존 버킷을 삭제하지 않는다. 키는 관리 경로의 credentials와 Kubernetes Secret으로 생성한다.

S3 연결 실습에는 별도 WSL 터미널에서 다음을 실행하고 유지한다.

```bash
source scripts/lib/common.sh
k -n storage port-forward --address 127.0.0.1 service/seaweedfs 8333:8333
```

첫 터미널에서 검사용 클라이언트를 준비한다.

```bash
.venv/bin/pip install boto3==1.40.50
.venv/bin/python scripts/check-s3.py --endpoint http://127.0.0.1:8333
```

검사는 credentials를 출력하지 않고 인증된 버킷 목록·검사용 객체 업로드·조회·삭제를 확인한다. 검사 완료 후 port-forward는 Ctrl+C로 종료한다. endpoint 내부 주소는 `seaweedfs.storage.svc.cluster.local:8333`, region은 `us-east-1`, HTTP와 path-style을 사용한다.

완료 기준은 3개 버킷과 S3 왕복 성공이다. 403은 인증·action, timeout은 Service/port-forward, 객체 조회 실패는 filer/volume 상태를 확인한다. [15장](15-persistence-and-destroy.md)에서 SeaweedFS Pod 재생성 후 보존을 확인한다.

[SeaweedFS 공식 소스](https://github.com/seaweedfs/seaweedfs), [다음: 백엔드](06-mimir-loki-tempo.md)
