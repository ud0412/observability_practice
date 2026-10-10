# 검증 기록과 실제 실습 확인표

## 2026-10-10 Basic 개편 검증

문서 경로를 `Guide/Basic/Korean`으로 변경하고 17개 주제를 설명·실습 두 페이지로 나눴습니다. WSL·Kubernetes·Cilium·Gateway 설치 구현과 교본은 선행 `wsl_kubernetes_practice`로 분리했습니다.

| 검사 | 결과 |
|---|---|
| Observability 계약·렌더링·삭제 경계·트레이스 링크 | 10개 중 9개 통과, Windows symlink 권한 때문에 1개 skip |
| 선행 과정 준비·완료 기록·버전·보존·삭제 | 4개 통과 |
| 양쪽 Markdown 상대 링크·YAML·교본 쌍 | 통과 |
| 변수 없는/있는 Dashboard 및 점도표 예시 JSON | 파싱·필수 필드 검사 통과 |
| 양쪽 Bash 구문(shfmt)·ShellCheck | 통과 |
| 개인 키·로컬 기획 제외 | ignore 확인 통과 |
| 실제 새 Dashboard 화면 | 실습자가 제공한 캡처의 Add·Panel·Variable 위치 대조 |
| 나머지 Grafana 화면 | v13.2 공식 문서 대조; 설치된 환경에서 전체 클릭 실습 미수행 |
| WSL 통합 설치·실제 장애 보존·destroy | 미수행; 실습자 확인 필요 |

자동화의 범위와 실제 삭제 동작은 소스·임시 디렉터리 테스트로 검사했습니다. 사용자 WSL에 환경을 구축한 결과가 아닙니다. 점도표는 실제 Tempo 표의 필드 이름·단위와 클릭한 Trace ID까지 실습에서 확인해야 합니다.

개편 후 추가 확인표:

- [ ] 선행 자동 up 후 Observability가 클러스터를 새로 만들지 않음
- [ ] 첫 Stat부터 선·막대·Arc 게이지·가로 게이지·표·로그 작성 성공
- [ ] 고정 쿼리를 변수로 변경, 단일·다중·All 선택 성공
- [ ] 실제 Spring 서버 요청당 점 하나와 시간 단위 확인
- [ ] 점 클릭 후 같은 Trace ID의 시간 막대 열림
- [ ] 트레이스 상세에서 로그까지 왕복
- [ ] 양쪽 저장소에서 전체 destroy와 재실행 확인

소스·정적 검증과 WSL 인프라 실행 검증을 구분한다. AI는 사용자 WSL에 클러스터나 Observability 스택을 설치하지 않았다.

검증 명령은 저장소 루트 기준이다.

```bash
python -m unittest discover -s tests -v
python tools/check_repository.py
find scripts -name '*.sh' -print0 | xargs -0 -n1 bash -n
(cd samples/fastapi && python -m pytest -q)
(cd samples/frontend && npm ci && npm run build)
(cd samples/spring-boot && mvn -B -ntp test)
```

로컬 실행 결과는 구현 완료 시 이 문서 아래에 기록한다. GitHub Actions는 소스 검사를 반복하며 WSL 통합 실습을 대체하지 않는다.

## 2026-10-09 소스 검증 결과

| 검사 | 결과 |
|---|---|
| React npm lock·production build | 통과 |
| Spring Boot Maven test/package | 정상·downstream 500·timeout 3개 테스트 통과, jar 생성 |
| FastAPI pytest | 정상·HTTP 500·JSON context/fallback 3개 테스트 통과 |
| 소스 통합 계측 | 실제 Java Agent 2.32.0 + Python 자동 계측 초기화로 동일 trace_id·서로 다른 span_id 확인. 하나의 요청에 5개 span 수신·서버 간 부모 관계 확인 |
| 실제 OTLP HTTP metric | 두 서비스 모두 `http.server.request.duration`, unit `s`, cumulative histogram 확인. `http.route`, `http.response.status_code` 속성 확인 |
| 상태·삭제 계약 테스트 | 8개 중 7개 통과. Windows symlink 생성 권한이 없어 실제 symlink 케이스 1개는 skip; Linux CI에서 실행 |
| Markdown 상대 링크·YAML·예시 Dashboard JSON·scope | 통과 |
| Cilium/Envoy Helm + 샘플 Kustomize | 선택 버전으로 실제 렌더링 통과 |
| Gateway/Envoy 리소스 | 선택 Envoy chart CRD의 실제 JSON schema 검사 통과 |
| Alloy node/central | 제품 내장 validate 통과 |
| Loki | 제품 내장 verify-config 통과 |
| Bash | shfmt 구문 검사 및 ShellCheck 통과 |
| Tempo/Mimir 실행형 config 검사 | 미수행. Tempo Windows binary는 호스트 application-control 정책으로 실행 제한, Mimir는 이 호스트용 서버 binary 없음. YAML·공식 버전별 설정/예제 검토 수행 |
| WSL 통합 설치·S3/백엔드 연동·장애 보존·실제 destroy | 미수행. 아래 실습자 확인표 사용 |

소스 통합 검사 도구는 [계측 검사 도구](../../../tools/check_sample_correlation.py)다. 로컬 임시 서버와 OTLP test receiver를 사용하고 종료 시 프로세스를 정리한다. Kubernetes·Grafana·저장 백엔드를 생성하지 않는다. Python에서는 launcher와 같은 공식 `initialize()` hook을 사용했다. FastAPI TestClient의 httpx 전환 안내 warning은 테스트 성공 여부와 구분한다.

```bash
# 소스 테스트용 FastAPI 환경·JDK·빌드 jar·검증된 agent가 있는 경우
python tools/check_sample_correlation.py --agent /path/to/opentelemetry-javaagent.jar
```

실습자가 실제 환경에서 확인할 항목:

- [ ] WSL 12~16GB에서 설치 완료·자원 사용 측정
- [ ] 노드 2개 Ready, Cilium DNS/Pod 통신
- [ ] Envoy Gateway/Proxy와 Grafana HTTPRoute Accepted/ResolvedRefs
- [ ] PVC 6개 Bound, S3 버킷·인증·객체 왕복
- [ ] node/cAdvisor metric과 해당 노드 log 중복 없는 수집
- [ ] Mimir/Loki/Tempo S3에 실제 데이터 블록 생성
- [ ] 두 서버 자동 HTTP metric·trace 및 같은 trace_id의 JSON log
- [ ] Grafana log→trace→service log 왕복
- [ ] 직접 만든 두 Dashboard와 JSON export/import
- [ ] Pod 재생성 후 저장 데이터·Dashboard 유지
- [ ] destroy 이후 cluster·실습 파일·관리 access 프로세스 없음
- [ ] 부분 설치 상태 및 destroy 두 번 실행 정상 처리

버전·metric/label·UI 메뉴가 다르면 고정된 버전을 먼저 확인한다. 수정한 실제 결과를 근거로 교본과 예시 JSON을 함께 업데이트한다.
