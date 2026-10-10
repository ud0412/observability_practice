# 11 설명 — Test 버튼으로 무엇을 관찰하나요?

사용자는 React 화면의 Test 버튼 하나만 누릅니다. 브라우저는 Spring Boot의 `/test`를 호출하고, Spring Boot는 FastAPI의 `/test`를 호출합니다.

React는 정적 파일을 nginx에서 제공합니다. 브라우저 Console에 버튼 동작을 기록하지만 React에 OTel 계측은 적용하지 않습니다. nginx의 서버 접근 로그와 브라우저 Console은 다른 기록입니다. 이번에는 nginx 로그만 Loki로 수집합니다.

Spring Boot와 FastAPI는 요청의 시작·완료·실패를 JSON 로그로 남깁니다. JSON은 이름과 값을 묶은 형식입니다. 아직 자동 계측을 적용하지 않았으므로 이 단계의 로그에 Trace ID가 없어도 정상입니다.

**빌드**는 소스 코드를 실행 가능한 이미지로 만드는 과정입니다. **kind load**는 그 이미지를 로컬 Kubernetes 노드에 넣는 과정이고, **배포**는 이미지로 Pod를 실행하는 과정입니다. 외부 이미지 저장소 계정은 필요하지 않습니다.

인프라 자동 설치에 샘플은 포함되지 않습니다. 이 장에서 처음으로 직접 빌드하고 배포합니다.

[목차](../README.md) · [이어서 실습하기](02-practice.md)
