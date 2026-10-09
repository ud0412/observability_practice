# 11. React·Spring Boot·FastAPI를 빌드하고 배포

선행 조건은 Grafana까지 완료된 인프라다. WSL 저장소 루트에서 진행한다. Docker build context는 각 서비스 디렉터리이며 개인 키나 로컬 기획 파일을 복사하지 않는다.

```bash
source scripts/lib/common.sh
docker build -t observability-frontend:lab-v1 samples/frontend
docker build --build-arg OTEL_JAVA_VERSION="$OTEL_JAVA_VERSION" \
  -t observability-spring-boot:lab-v1 samples/spring-boot
docker build -t observability-fastapi:lab-v1 samples/fastapi
kind load docker-image --name "$LAB_NAME" observability-frontend:lab-v1 \
  observability-spring-boot:lab-v1 observability-fastapi:lab-v1
k apply -k samples/kubernetes/base
k -n sample-app rollout status deployment/frontend --timeout=180s
k -n sample-app rollout status deployment/spring-boot --timeout=300s
k -n sample-app rollout status deployment/fastapi --timeout=180s
```

FastAPI는 Python image에서 requirements를 설치한다. Spring Boot는 Maven build 후 JRE image에 jar와 agent를 넣는다. 기본 배포에서는 agent를 실행하지 않는다. React는 npm lock file로 빌드한 정적 파일을 nginx에서 제공한다.

Windows 브라우저의 `http://localhost:8080/`를 열고 `Test` 버튼을 누른다. DevTools Console에 시작·성공·실패가 표시된다. Network 탭에서 동일 origin `/test`와 응답 status를 확인한다.

```bash
k -n sample-app logs deployment/spring-boot --tail=20
k -n sample-app logs deployment/fastapi --tail=20
k -n sample-app logs deployment/frontend --tail=20
```

두 서버의 요청 log는 JSON stdout이며 노드 Alloy를 통해 Loki에 수집된다. 현재 계측 전이므로 trace_id/span_id가 없거나 비어 있는 것은 정상이다. FE nginx access log는 Loki에서 볼 수 있지만 브라우저 Console log는 보내지 않는다.

Gateway의 `/test` Exact route가 FE의 `/` PathPrefix보다 우선한다. FastAPI Service는 내부 통신만 사용한다. `ImagePullBackOff`이면 이미지 이름·kind load·`imagePullPolicy: Never`를 확인한다. 502는 Spring 로그와 FastAPI 준비 상태를 확인한다.

완료 기준은 버튼 한 번으로 두 서버가 응답하고 각각의 log를 확인하는 것이다. [다음: 자동 계측](12-server-otel-instrumentation.md)
