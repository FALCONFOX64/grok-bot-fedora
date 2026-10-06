#!/bin/bash
# Build a Fedora RPM from a Grok Bot .deb.
# Usage: ./build.sh /path/to/grok-bot_<version>_amd64.deb

set -euo pipefail

if [ "$#" -ne 1 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "usage: $0 /path/to/grok-bot_<version>_amd64.deb" >&2
    exit 2
fi

DEB=$(readlink -f "$1")
if [ ! -f "$DEB" ]; then
    echo "not a file: $1" >&2
    exit 1
fi

ROOT=$(cd "$(dirname "$0")" && pwd)
WORKDIR=$(mktemp -d)
trap 'rm -rf "$WORKDIR"' EXIT

mkdir -p "$WORKDIR/deb" "$WORKDIR/control" "$WORKDIR/root" "$WORKDIR/rpm"

(
    cd "$WORKDIR/deb"
    ar x "$DEB"
)

control_archive=$(echo "$WORKDIR"/deb/control.tar.*)
data_archive=$(echo "$WORKDIR"/deb/data.tar.*)
tar -xaf "$control_archive" -C "$WORKDIR/control"
tar -xaf "$data_archive" -C "$WORKDIR/root"

VERSION=$(awk -F': ' '/^Version: /{print $2; exit}' "$WORKDIR/control/control")
ARCH=$(awk -F': ' '/^Architecture: /{print $2; exit}' "$WORKDIR/control/control")

if [ -z "$VERSION" ]; then
    echo "the .deb has no Version field" >&2
    exit 1
fi
if [ "$ARCH" != "amd64" ]; then
    echo "this package is built for x86_64. The .deb architecture is ${ARCH:-unknown}." >&2
    exit 1
fi

mkdir -p "$WORKDIR/rpm"/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

rpmbuild -bb \
    --define "_topdir $WORKDIR/rpm" \
    --define "_version $VERSION" \
    --define "_payload $WORKDIR/root" \
    "$ROOT/grok-bot.spec"

built=$(find "$WORKDIR/rpm/RPMS" -type f -name '*.rpm' -print -quit)
if [ -z "$built" ]; then
    echo "rpmbuild did not write an rpm" >&2
    exit 1
fi

mkdir -p "$ROOT/dist"
cp -f "$built" "$ROOT/dist/"
echo "Wrote $ROOT/dist/$(basename "$built")"
