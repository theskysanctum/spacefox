#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

VERSION="$(cat VERSION)"
if [ "$VERSION" = "latest" ]; then
    VERSION="$(curl -fsSL https://product-details.mozilla.org/1.0/firefox_versions.json \
        | python3 -c 'import json,sys; print(json.load(sys.stdin)["LATEST_FIREFOX_VERSION"])')"
    echo "VERSION=latest -> resolved to $VERSION"
fi

BUILD_DIR="$(pwd)/build"
TARBALL="$BUILD_DIR/firefox-$VERSION.source.tar.xz"
SRC_DIR="$BUILD_DIR/firefox-$VERSION"

mkdir -p "$BUILD_DIR"

if [ ! -f "$TARBALL" ]; then
    URL="https://ftp.mozilla.org/pub/firefox/releases/$VERSION/source/firefox-$VERSION.source.tar.xz"
    echo "Downloading $URL"
    curl -fL --progress-bar -o "$TARBALL" "$URL"
else
    echo "Reusing already-downloaded $TARBALL"
fi

if [ ! -d "$SRC_DIR" ]; then
    echo "Extracting to $SRC_DIR..."
    mkdir -p "$SRC_DIR"
    tar -xf "$TARBALL" -C "$SRC_DIR" --strip-components=1
else
    echo "Reusing already-extracted $SRC_DIR"
fi

echo "$VERSION" > "$BUILD_DIR/CURRENT_VERSION"
echo "Source ready at $SRC_DIR"
