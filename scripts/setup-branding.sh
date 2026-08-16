#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

BUILD_DIR="$(pwd)/build"
VERSION="$(cat "$BUILD_DIR/CURRENT_VERSION" 2>/dev/null || cat VERSION)"
SRC_DIR="$BUILD_DIR/firefox-$VERSION"
BRAND_DIR="$SRC_DIR/browser/branding/spacefox"

if [ ! -d "$SRC_DIR/browser/branding/unofficial" ]; then
    echo "error: $SRC_DIR/browser/branding/unofficial not found -- run fetch-source.sh first" >&2
    exit 1
fi

rm -rf "$BRAND_DIR"
cp -r "$SRC_DIR/browser/branding/unofficial" "$BRAND_DIR"
cp -r branding/spacefox-overlay/. "$BRAND_DIR/"

echo "Branded $BRAND_DIR as SpaceFox"
