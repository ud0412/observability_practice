# Podman 대안 검토

기본 과정은 Docker Engine + kind다. Podman이 더 무겁다고 측정한 결론은 아니다. 사용자 우선순위인 재현성·부하·실습 안정성을 고려해 문서 지원이 충분한 기본 경로를 선정했다.

rootless kind는 cgroup v2, systemd delegation 등 조건이 필요하다. Cilium의 BPF·권한·host 접근과 Alloy host mount, local PV, Envoy 네트워크까지 같은 조건에서 검증해야 한다. 이 저장소의 운영 스크립트는 Docker ownership 검사에 맞춰 작성되어 있다. provider 환경변수만 바꾸어 정상 지원된다고 간주하지 않는다.

비교한다면 같은 Kubernetes 버전·2노드·수집 주기·보존 기간·입력 부하로 유휴 메모리, 요청 처리 CPU/메모리, 생성 시간, 네트워크/스토리지 및 재시작 동작을 측정한다. 별도의 Podman 전용 소유권/destroy 검증을 구현한 후 대안 경로로 승격한다.

[kind rootless 공식 안내](https://kind.sigs.k8s.io/docs/user/rootless/), [Cilium 요구사항](https://docs.cilium.io/en/stable/operations/system_requirements/)
