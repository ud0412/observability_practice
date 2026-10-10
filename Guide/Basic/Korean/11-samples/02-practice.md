# 11 실습 — 세 서비스 빌드와 배포

시작 조건: Grafana까지 설치, access 실행 중. WSL Bash, observability_practice 루트에서 진행합니다. 새 터미널의 export는 00 실습을 따릅니다.

## 1. 이미지를 하나씩 빌드

```bash
docker build -t observability-frontend:lab-v1 samples/frontend
```

정상 결과: React 정적 빌드와 nginx 이미지 생성 완료입니다. 이어서 두 서버를 빌드합니다.

```bash
source config/versions.env
docker build --build-arg OTEL_JAVA_VERSION="$OTEL_JAVA_VERSION" -t observability-spring-boot:lab-v1 samples/spring-boot
docker build -t observability-fastapi:lab-v1 samples/fastapi
docker image ls --filter reference='observability-*:lab-v1'
```

`source config/versions.env`는 버전 값을 읽는 동작입니다. 아직 Java Agent를 실행하지 않습니다. Spring 이미지 안에 이후 계측에 사용할 파일까지 준비합니다.

## 2. kind 노드에 이미지 넣기

```bash
kind load docker-image --name observability-lab observability-frontend:lab-v1 observability-spring-boot:lab-v1 observability-fastapi:lab-v1
```

Docker에만 이미지가 있고 kind 노드에 없으면 Pod가 시작하지 못합니다. imagePullPolicy가 Never이므로 외부에서 자동 다운로드하지 않습니다.

## 3. 배포하고 준비 기다리기

```bash
kubectl apply -k samples/kubernetes/base
kubectl -n sample-app rollout status deployment/frontend --timeout=180s
kubectl -n sample-app rollout status deployment/spring-boot --timeout=300s
kubectl -n sample-app rollout status deployment/fastapi --timeout=180s
kubectl -n sample-app get pods,svc,httproute
```

`-k`는 폴더의 kustomization 설정을 함께 적용합니다. 정상 결과는 세 Deployment Ready입니다. Gateway는 `/test`를 Spring으로, 나머지 `/`를 FE로 보냅니다. FastAPI는 클러스터 내부에서 호출합니다.

## 4. 버튼과 각 로그 확인

Windows 브라우저에서 `http://localhost:8080/`를 열고 **Test**를 누릅니다. 응답 성공이 보여야 합니다. **F12 → Console**에서 버튼 동작 기록을 확인하고, **Network**에서 `/test` 요청과 HTTP 응답을 확인합니다.

WSL에서 각 서버의 로그를 확인합니다.

```bash
kubectl -n sample-app logs deployment/spring-boot --tail=20
kubectl -n sample-app logs deployment/fastapi --tail=20
kubectl -n sample-app logs deployment/frontend --tail=20
```

정상 결과: 두 서버에서 요청 시작/완료 JSON 기록, frontend에서 nginx 접근 기록이 보입니다.

Grafana **Explore → Loki → Code**에서 아래 쿼리를 실행합니다.

```logql
{namespace="sample-app",service_name="sample-spring-boot"} | json
```

그다음 `sample-spring-boot`를 `sample-fastapi`로 바꿔 조회합니다. 브라우저 Console의 기록은 Loki에 보내지 않으므로 Loki에서 해당 메시지를 찾지 않습니다.

| 문제 | 확인 |
|---|---|
| ErrImageNeverPull / ImagePullBackOff | 이미지 태그와 kind load 완료 여부 |
| 버튼 응답 502 | FastAPI Ready와 Spring 로그 |
| 접속 404 | sample-app HTTPRoute의 Accepted/ResolvedRefs |
| Loki에 로그 없음 | 30~60초 기다리기, 노드 Alloy·namespace와 service_name label |

완료 확인: 버튼 한 번으로 두 서버를 호출하고 두 서버의 로그를 읽었습니다. 활성 요청 로그의 trace_id가 비어 있는 상태는 다음 장에서 바꿉니다.

[먼저 읽을 설명](01-concept.md) · [목차](../README.md) · [다음 학습](../12-otel/01-concept.md)
