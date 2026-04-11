#!/bin/bash
# build-openvpn.sh: Download and compile an OpenVPN version to /opt/openvpn-<version>
# Usage: sudo ./build-openvpn.sh <version>
# Example: sudo ./build-openvpn.sh 2.6.14

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 2.6.14"
    exit 1
fi

VERSION="$1"
PREFIX="/opt/openvpn-${VERSION}"
URL="https://swupdate.openvpn.org/community/releases/openvpn-${VERSION}.tar.gz"
BUILDDIR=$(mktemp -d /tmp/openvpn-build.XXXXXX)

if [ -x "${PREFIX}/sbin/openvpn" ]; then
    echo "OpenVPN ${VERSION} already installed at ${PREFIX}"
    exit 0
fi

echo "==> Checking build dependencies..."
DEPS=(build-essential libssl-dev liblzo2-dev libpam0g-dev liblz4-dev)
MISSING=()
for dep in "${DEPS[@]}"; do
    if ! dpkg -s "$dep" &>/dev/null && ! rpm -q "$dep" &>/dev/null 2>&1; then
        MISSING+=("$dep")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "Note: You may need these packages: ${MISSING[*]}"
    echo "On Fedora/RHEL: dnf install openssl-devel lzo-devel pam-devel lz4-devel gcc make"
    echo "On Debian/Ubuntu: apt install ${MISSING[*]}"
fi

cleanup() { rm -rf "$BUILDDIR"; }
trap cleanup EXIT

echo "==> Downloading OpenVPN ${VERSION}..."
cd "$BUILDDIR"
curl -fSL "$URL" -o "openvpn-${VERSION}.tar.gz"

echo "==> Extracting..."
tar xzf "openvpn-${VERSION}.tar.gz"
cd "openvpn-${VERSION}"

echo "==> Configuring (prefix=${PREFIX}, --disable-dco)..."
./configure --prefix="$PREFIX" --disable-dco --quiet

echo "==> Building..."
make -j"$(nproc)" --quiet

echo "==> Installing to ${PREFIX}..."
make install --quiet

echo "==> Done! Binary: ${PREFIX}/sbin/openvpn"
"${PREFIX}/sbin/openvpn" --version | head -1
