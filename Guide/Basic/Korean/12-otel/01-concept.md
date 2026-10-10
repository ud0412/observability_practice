# 12 설명 — 코드를 크게 바꾸지 않고 자동 계측하기

**계측**은 서비스에서 메트릭·트레이스 같은 관측 데이터를 얻을 수 있게 하는 작업입니다. OpenTelemetry(OTel)는 여러 도구가 공통 형식으로 데이터를 주고받도록 돕습니다.

이번에는 Java Agent와 Python 실행 도구가 HTTP 요청과 호출을 자동으로 관찰합니다. 업무 코드에서 직접 span을 만들지 않습니다. 업무 로그 메시지는 이미 앱 코드가 작성하고 있습니다.

Spring Boot에는 JVM 시작 옵션으로 Java Agent를 붙입니다. FastAPI는 `opentelemetry-instrument`로 시작합니다. 두 도구 모두 중앙 Alloy의 4318 포트로 데이터를 보냅니다.

Spring이 FastAPI를 호출할 때 HTTP 요청에 트레이스 정보를 전달하고, FastAPI가 이를 받아 같은 Trace ID를 사용합니다. 서비스별 처리 단계에는 서로 다른 Span ID가 생깁니다. 로그에도 현재 요청의 ID가 들어가므로 같은 요청의 로그와 트레이스를 연결할 수 있습니다.

메트릭은 30초 간격으로 내보냅니다. 로그는 기존 stdout 경로를 계속 사용하고 OTel 로그 전송은 꺼서 이중 수집을 피합니다. React의 브라우저 트레이스는 만들지 않습니다.

[목차](../README.md) · [이어서 실습하기](02-practice.md)
