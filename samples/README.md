# 서버 샘플

React의 버튼 하나가 Spring Boot `/test`를 호출하고, Spring Boot가 FastAPI `/test`를 호출한다. React 계측은 없다. 서버 log는 stdout → 노드 Alloy → Loki, 서버 metric·trace는 OTLP → 중앙 Alloy → Mimir/Tempo로 보낸다.

- [빌드·배포 실습](../docs/11-sample-build-and-deploy.md)
- [자동 계측](../docs/12-server-otel-instrumentation.md)
- [서버 Dashboard](../docs/13-dashboard-services.md)
- [log/trace 연결·오류 분석](../docs/14-correlation-and-troubleshooting.md)

인프라 `up` 명령은 이 디렉터리의 빌드·배포·호출을 수행하지 않는다. 각 Docker build context는 해당 서비스 디렉터리만 사용한다.
