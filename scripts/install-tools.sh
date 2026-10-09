#!/usr/bin/env bash
# Explicit preparation command; never called by up. Installs into ~/.local/bin.
source "$(dirname "$0")/lib/common.sh"
arch=$(uname -m)
case "$arch" in x86_64) arch=amd64 ;; aarch64) arch=arm64 ;; *)
	echo 'Unsupported architecture' >&2
	exit 1
	;;
esac
command -v curl >/dev/null
mkdir -p "$HOME/.local/bin"
tool_tmp=$(mktemp -d)
trap 'rm -rf -- "$tool_tmp"' EXIT
cd "$tool_tmp" || exit 1
curl -fsSLO "https://github.com/kubernetes-sigs/kind/releases/download/v$KIND_VERSION/kind-linux-$arch"
curl -fsSLO "https://github.com/kubernetes-sigs/kind/releases/download/v$KIND_VERSION/kind-linux-$arch.sha256sum"
sha256sum -c "kind-linux-$arch.sha256sum"
install -m 755 "kind-linux-$arch" "$HOME/.local/bin/kind"
curl -fsSLo kubectl "https://dl.k8s.io/release/v$KUBERNETES_VERSION/bin/linux/$arch/kubectl"
curl -fsSLo kubectl.sha256 "https://dl.k8s.io/release/v$KUBERNETES_VERSION/bin/linux/$arch/kubectl.sha256"
echo "$(cat kubectl.sha256)  kubectl" | sha256sum -c -
install -m 755 kubectl "$HOME/.local/bin/kubectl"
curl -fsSLO "https://get.helm.sh/helm-v$HELM_VERSION-linux-$arch.tar.gz"
curl -fsSLO "https://get.helm.sh/helm-v$HELM_VERSION-linux-$arch.tar.gz.sha256sum"
sha256sum -c "helm-v$HELM_VERSION-linux-$arch.tar.gz.sha256sum"
tar -xzf "helm-v$HELM_VERSION-linux-$arch.tar.gz"
install -m 755 "linux-$arch/helm" "$HOME/.local/bin/helm"
echo "Tools installed. Add $HOME/.local/bin to PATH."
