# 02 실습 — 저장 공간과 SeaweedFS S3 연결

시작 조건: 00 실습의 `prepare` 완료. 실행 위치: WSL Bash, observability_practice 루트. 새 터미널이라면 00 실습의 export를 먼저 실행합니다.

## 1. 저장 공간 적용

```bash
kubectl apply -f "$LAB_STATE_DIR/rendered/storage.yaml"
kubectl get pv
kubectl get pvc -A
```

여섯 PVC가 생성됩니다. 아직 사용할 Pod가 없으므로 `Pending`이어도 정상입니다. Pod가 배치될 때 PV에 연결하는 방식입니다.

## 2. SeaweedFS 설치

```bash
kubectl apply -f "$LAB_STATE_DIR/rendered/seaweedfs.yaml"
kubectl -n storage rollout status deployment/seaweedfs --timeout=450s
kubectl -n storage get pods,pvc,svc
```

정상 결과: SeaweedFS Pod가 Ready, PVC가 Bound, Service의 S3 포트가 8333입니다. `mini` 방식으로 여러 내부 역할을 한 프로세스에서 실행합니다.

## 3. S3에 연결할 통로 열기

**두 번째 WSL 터미널**에서 00 실습의 세 export를 반복한 후 실행합니다.

```bash
kubectl -n storage port-forward --address 127.0.0.1 service/seaweedfs 8333:8333
```

정상 결과: `Forwarding from 127.0.0.1:8333`. 이 터미널은 실행 상태로 둡니다. 브라우저 로그인 화면을 찾는 단계가 아니라 S3 클라이언트가 사용할 통로를 여는 단계입니다.

## 4. 버킷과 객체 왕복 확인

첫 터미널의 저장소 루트로 돌아와 실행합니다.

```bash
.venv/bin/pip install boto3==1.40.50
.venv/bin/python scripts/check-s3.py --endpoint http://127.0.0.1:8333
```

검사 도구는 키를 관리 파일에서 읽습니다. 키를 직접 입력하거나 출력하지 않습니다. 세 버킷 확인 → 테스트 객체 업로드 → 내용 읽기 → 테스트 객체 삭제를 수행합니다.

정상 결과: `S3 authentication, bucket listing and object read verified`. 확인 후 두 번째 터미널에서 **Ctrl+C**로 통로를 닫습니다.

| 문제 | 확인 방법 |
|---|---|
| Connection refused | 두 번째 터미널의 port-forward가 실행 중인지 |
| 403 | SeaweedFS 로그에서 인증 오류 확인: `kubectl -n storage logs deployment/seaweedfs --tail=50` |
| PVC Pending 지속 | `kubectl -n storage describe pod -l app=seaweedfs`의 Events에서 worker·경로 확인 |

완료 확인: 세 버킷 확인과 객체 왕복이 성공했습니다. 이후 백엔드는 내부 주소 `seaweedfs.storage.svc.cluster.local:8333`에 접속합니다. HTTP·path-style·region `us-east-1`을 사용합니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../03-mimir/01-concept.md)
