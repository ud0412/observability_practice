# 06. 세 백엔드를 단일 프로세스로 배포

SeaweedFS가 Ready인 WSL Bash에서 진행한다. 단일 프로세스는 각각 하나의 실행 파일이 내부 역할들을 함께 수행하는 배포 방식이다. replicas만 1로 줄인 distributed chart와 다르다.

```bash
source scripts/lib/common.sh
for backend in mimir loki tempo; do
  k apply -f "$LAB_STATE_DIR/rendered/$backend.yaml"
  k -n observability rollout status "deployment/$backend" --timeout=450s
done
k -n observability get pods,pvc,svc
```

| 백엔드 | 설정 파일 | 저장 경로·주소 |
|---|---|---|
| Mimir | [config](../infrastructure/mimir/config.yaml) | classic 모드·Kafka 없음, `/data/tsdb`, S3 `mimir-blocks`, port 9009 |
| Loki | [config](../infrastructure/loki/config.yaml) | TSDB/v13 index, `/data/wal`, S3 `loki-data`, port 3100 |
| Tempo 3 | [config](../infrastructure/tempo/config.yaml) | `target=all`, `/data/wal`, S3 `tempo-traces`, HTTP 3200·OTLP 4317/4318 |

키는 환경변수와 `-config.expand-env=true`로 읽는다. ConfigMap에 실제 키를 넣지 않는다. 모든 상태 서비스는 replica 1·Recreate 전략으로 동일 데이터 디렉터리를 두 Pod가 동시에 열지 않게 한다. 기본 retention은 24시간이며 compaction 및 삭제 지연 때문에 S3 객체가 정확히 24시간 시각에 즉시 사라지는 것은 아니다.

완료 기준은 세 Deployment Available과 PVC Bound다. metric/log/trace가 입력되지 않으면 아직 데이터가 없는 것이 정상이다. Alloy와 샘플 이후 실제 버킷의 데이터 생성까지 확인한다. `k logs deployment/<backend>`에서 S3 인증 오류와 설정 parsing 오류를 구분한다.

확인 과제: S3 업로드 전 WAL과 업로드 후 객체의 역할을 설명한다. Tempo 3의 backend scheduler/worker 설정을 이전 Tempo 2의 compactor 설정과 혼용하지 않는다.

[Mimir 모드](https://grafana.com/docs/mimir/latest/references/architecture/deployment-modes/), [Loki 모드](https://grafana.com/docs/loki/latest/get-started/deployment-modes/), [Tempo 설정](https://grafana.com/docs/tempo/latest/configuration/), [다음: Alloy](07-alloy.md)
