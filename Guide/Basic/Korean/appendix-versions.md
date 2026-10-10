# 버전 잠금과 선정 근거

2026-10-09 공식 릴리스 기준으로 [versions.env](../../../config/versions.env)를 고정했다. 최신 kind 0.33.0 기본 이미지 1.37 대신 **Kubernetes 1.36.4**를 선택했다. Cilium 1.20와 Envoy Gateway 1.9의 지원 범위가 1.36까지 겹친다. node image digest도 고정한다.

| 항목 | 버전 | 공식 근거 |
|---|---|---|
| kind | 0.33.0 | [release·node digest](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0) |
| Cilium | 1.20.2 | [지원 Kubernetes](https://docs.cilium.io/en/stable/network/kubernetes/compatibility/) |
| Envoy Gateway / API | 1.9.2 / 1.6.1 | [호환성 표](https://gateway.envoyproxy.io/news/releases/matrix/) |
| SeaweedFS | 4.48 | [release](https://github.com/seaweedfs/seaweedfs/releases/tag/4.48) |
| Mimir / Loki / Tempo | 3.2.2 / 3.7.8 / 3.1.0 | [Mimir](https://github.com/grafana/mimir/releases/tag/mimir-3.2.2), [Loki](https://github.com/grafana/loki/releases/tag/v3.7.8), [Tempo](https://github.com/grafana/tempo/releases/tag/v3.1.0) |
| Alloy / Grafana | 1.20.1 / 13.2.3 | [Alloy](https://github.com/grafana/alloy/releases/tag/v1.20.1), [Grafana](https://github.com/grafana/grafana/releases/tag/v13.2.3) |
| Spring Boot / Java Agent | 4.1.1 / 2.32.0 | [Boot](https://repo.maven.apache.org/maven2/org/springframework/boot/spring-boot-starter-parent/), [agent](https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/tag/v2.32.0) |
| Python OTel SDK / instrumentation | 1.45.1 / 0.66b1 | [SDK](https://pypi.org/project/opentelemetry-sdk/1.45.1/), [distro](https://pypi.org/project/opentelemetry-distro/0.66b1/) |

Python instrumentation의 `b1`은 이 프로젝트 공식 배포 버전 체계다. SDK와 instrumentation 조합을 함께 잠근다. runtime에서 latest나 floating chart version을 조회하지 않는다. Helm chart/app version과 base image version은 다른 항목이다.

업데이트 시 호환성 → config/schema → render/lint → 실제 실습 재현 → Dashboard metric/label 순서로 확인한다. Tempo S3 문서는 SeaweedFS를 로컬 평가용으로 소개하며 완전한 호환성을 보장하지 않는다. [Tempo S3 안내](https://grafana.com/docs/tempo/latest/configuration/hosted-storage/s3/)에 따라 버킷 API와 실제 저장·재시작을 학습자가 검증한다.
