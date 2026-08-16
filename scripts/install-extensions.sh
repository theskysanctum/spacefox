#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

BUILD_DIR="$(pwd)/build"
VERSION="$(cat "$BUILD_DIR/CURRENT_VERSION")"
DIST_DIR="$BUILD_DIR/firefox-$VERSION/obj-spacefox/dist/bin/distribution"

python3 extensions/fetch_extensions.py

mkdir -p "$DIST_DIR/extensions"
cp extensions/generated/*.xpi "$DIST_DIR/extensions/"
cp extensions/generated/policies.json "$DIST_DIR/policies.json"

echo "Installed extension bundle into $DIST_DIR"
