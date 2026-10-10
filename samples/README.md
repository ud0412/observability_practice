# Basic 서버 샘플

React의 Test 버튼 → Spring Boot `/test` → FastAPI `/test`를 실행합니다. React는 계측하지 않습니다. 서버 로그는 stdout → 노드 Alloy → Loki, 서버 메트릭·트레이스는 OTLP → 중앙 Alloy → Mimir/Tempo 경로로 보냅니다.

- [빌드·배포](../Guide/Basic/Korean/11-samples/02-practice.md)
- [서버 자동 계측](../Guide/Basic/Korean/12-otel/02-practice.md)
- [서비스 Dashboard](../Guide/Basic/Korean/13-service-dashboard/02-practice.md)
- [트레이스 점도표](../Guide/Basic/Korean/14-trace-scatter/02-practice.md)
- [로그와 트레이스 연결](../Guide/Basic/Korean/15-correlation/02-practice.md)

인프라 자동 스크립트는 이 샘플을 빌드·배포·호출하지 않습니다. 각 Docker build context는 해당 서비스 폴더만 사용합니다.
