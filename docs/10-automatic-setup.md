# 10. 같은 인프라를 자동 구축하기

01장 준비를 마친 WSL 저장소 루트에서 실행한다.

```bash
bash scripts/lab.sh up
bash scripts/lab.sh status
bash scripts/lab.sh access
```

up은 preflight → prepare/render → kind → Cilium → Envoy → local PV → SeaweedFS → Mimir/Loki/Tempo → Alloy → Grafana 순서로 실행한다. [steps](../scripts/steps/)는 수동 장의 동일 명령·설정 파일을 사용한다. WSL·Docker Engine 설치와 재부팅은 사전 준비이고 up이 OS를 변경하지 않는다.

샘플 FE/BE 빌드·이미지 로드·배포·계측·`/test` 호출은 포함하지 않는다. 자동 구축 성공 후에도 서버 trace는 아직 없다. 인프라 검증은 샘플 없이 readiness/PVC/Route를 확인한다. 실제 S3 왕복은 [05장](05-storage-and-seaweedfs.md), 수집 데이터는 [08장](08-grafana.md)에서 확인한다.

up 재실행은 같은 클러스터, 키, PVC, 버킷과 DB를 유지한다. renderer가 설정 checksum을 Pod template에 넣으므로 백엔드·Alloy·datasource 설정 변경 시 해당 Pod가 재생성된다. 버전 업그레이드 실습은 데이터 schema 호환성을 따로 확인한 후 수행한다.

실패한 단계와 오류가 표시되면 `k describe pod`, `k logs`, 해당 Helm/Route 상태를 읽고 수정한 뒤 재실행한다. 실패를 성공으로 표시하지 않는다. 대기시간 초과는 실제 원인을 먼저 확인한다.

```bash
# 전체 실습 종료; 보존 옵션 없이 관리 데이터 삭제
bash scripts/lab.sh destroy
```

destroy는 수동 경로로 만든 같은 실습 환경에도 적용한다. 재실행·부분 설치 실패 정리를 포함한 계약은 [15장](15-persistence-and-destroy.md)에 있다. 도구와 교본 소스는 설치 상태로 남는다.

[다음: 샘플 빌드·배포](11-sample-build-and-deploy.md)
