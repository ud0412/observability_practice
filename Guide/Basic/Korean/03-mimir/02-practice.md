# 03 실습 — Mimir 설치하기

시작 조건: SeaweedFS Ready, 03 설명 읽기 완료. 실행 위치: WSL Bash, 저장소 루트. 새 터미널의 환경변수는 00 실습을 따릅니다.

## 1. 준비된 설치 파일 적용

```bash
kubectl apply -f "$LAB_STATE_DIR/rendered/mimir.yaml"
```

이 파일에는 설정을 담은 ConfigMap, 실행할 Deployment, 내부 접속용 Service가 들어 있습니다. 설정 원본은 [config.yaml](../../../../infrastructure/mimir/config.yaml)입니다. 실제 S3 키는 Secret에서 읽습니다.

## 2. 준비 완료까지 기다리기

```bash
kubectl -n observability rollout status deployment/mimir --timeout=450s
kubectl -n observability get pods -l app=mimir
kubectl -n observability get pvc mimir
```

정상 결과: `successfully rolled out`, Pod `1/1 Running`, PVC `Bound`. Running만 보이고 Ready가 0/1이면 준비가 끝나지 않은 것입니다.

## 3. 시작 로그 확인

```bash
kubectl -n observability logs deployment/mimir --tail=50
```

반복되는 S3 인증 오류나 설정 해석 오류가 없어야 합니다. 메트릭을 아직 보내지 않았으므로 데이터가 없는 것은 설치 실패가 아닙니다.

| 막힌 상황 | 다음 확인 |
|---|---|
| Pending | `kubectl -n observability describe pod -l app=mimir`의 Events |
| CrashLoopBackOff | 위 로그와 `kubectl -n observability logs deployment/mimir --previous --tail=50` |
| S3 연결 오류 | SeaweedFS Pod와 Service가 Ready인지, 02 실습 S3 검사 성공 여부 |

완료 확인: Mimir Pod Ready와 PVC Bound를 확인했습니다. 수집기를 설치한 뒤 Grafana에서 실제 메트릭을 조회합니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../04-loki/01-concept.md)
