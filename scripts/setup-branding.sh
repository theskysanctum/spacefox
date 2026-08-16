#!/bin/sh
# Brands the fetched Firefox source (see fetch-source.sh) as SpaceFox:
# copies Firefox's own browser/branding/unofficial/ (the directory
# upstream ships specifically for community/unofficial builds like this
# one) as a base, then overlays branding/spacefox-overlay/ (SpaceFox's
# actual name, icons, wordmark) on top of it. The base gives us a
# correct Makefile.in/moz.build/jar.mn/locales scaffold for free instead
# of hand-authoring Firefox's own build plumbing from scratch.
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
