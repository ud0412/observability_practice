# 01. Windows와 WSL 사전 준비

목표는 WSL2 Linux에서 Docker Engine·kind·kubectl·Helm·Python을 사용할 수 있게 하는 것이다. 명령은 실행 위치를 지켜 수행한다. Ubuntu 24.04 LTS를 기준으로 한다.

Windows PowerShell에서 WSL 설치 상태를 확인한다.

```powershell
wsl --install -d Ubuntu-24.04
wsl --update
wsl --list --verbose
```

Windows의 `%UserProfile%\.wslconfig`를 편집한다. 다른 설정이 있다면 병합한다.

```ini
[wsl2]
memory=16GB
processors=6
swap=4GB
```

기존 WSL 작업을 종료한 뒤 PowerShell의 `wsl --shutdown`으로 새 설정을 적용한다. WSL에서 `/etc/wsl.conf`에 `[boot]`와 `systemd=true`를 설정하고 다시 시작한다. [WSL systemd 공식 안내](https://learn.microsoft.com/en-us/windows/wsl/systemd)

WSL Ubuntu Bash에서 Docker 공식 apt 저장소를 구성한다.

```bash
sudo apt update
sudo apt install -y ca-certificates curl git python3 python3-venv
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

그룹 변경 후 WSL 터미널을 다시 연다. Docker 그룹은 Docker daemon을 통한 호스트 관리 권한을 갖는다. 이 교본의 bind mount 소유권 검사는 WSL 내부 Engine 기준이다. 기존 Docker Desktop 사용자는 해당 배포판의 Desktop integration을 해제하고 내부 Engine 경로를 선택한다. 다른 프로젝트의 Desktop 설정은 유지하고 두 daemon의 socket을 혼용하지 않는다. [Docker Ubuntu 설치](https://docs.docker.com/engine/install/ubuntu/)

저장소는 `/mnt/c` 대신 WSL Linux 파일시스템으로 복제한다. 비밀 파일은 소스 빌드에 필요 없다.

```bash
mkdir -p ~/src
cd ~/src
git clone https://github.com/ud0412/observability_practice.git
cd observability_practice
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
export PATH="$HOME/.local/bin:$PATH"
bash scripts/install-tools.sh
bash scripts/preflight.sh
```

도구 준비 명령은 클러스터를 생성하지 않는다. 디스크 여유는 `df -h ~`, 메모리는 `free -h`, 런타임은 `docker info`로 확인한다. WSL 12GB가 하한 목표이고 16GB를 권장한다. 실제 자원 사용은 실습 중 측정한다.

**각 수동 실습 터미널에서** 저장소 루트로 이동한 뒤 다음을 실행한다.

```bash
source scripts/lib/common.sh
```

이 파일은 버전과 전용 저장 경로를 읽고 `KUBECONFIG`를 지정한다. `k` 함수는 `kubectl --kubeconfig "$KUBECONFIG" --context "kind-observability-lab"`의 축약이다. 다른 클러스터의 현재 context를 사용하지 않는다.

[다음: kind](02-kind.md)
