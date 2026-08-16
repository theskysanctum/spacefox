#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

./scripts/fetch-source.sh
./scripts/setup-branding.sh

BUILD_DIR="$(pwd)/build"
VERSION="$(cat "$BUILD_DIR/CURRENT_VERSION")"
SRC_DIR="$BUILD_DIR/firefox-$VERSION"

while read -r patch; do
    case "$patch" in
        ""|\#*) continue ;;
    esac
    echo "Applying patches/$patch"
    patch -d "$SRC_DIR" -p1 < "patches/$patch"
done < patches/series

cp mozconfigs/linux "$SRC_DIR/mozconfig"

cd "$SRC_DIR"
if [ ! -f .mozbuild-bootstrapped ]; then
    echo "First build -- running ./mach bootstrap (interactive, installs build deps)..."
    ./mach bootstrap
    touch .mozbuild-bootstrapped
fi

./mach build
