#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

PROFILE="${1:?usage: install-userchrome.sh <path-to-firefox-profile>}"

python3 theme/generate_userchrome.py

mkdir -p "$PROFILE/chrome"
cp -r theme/generated/userChrome.css theme/generated/userContent.css theme/generated/fonts "$PROFILE/chrome/"

USER_JS="$PROFILE/user.js"
if ! grep -q "toolkit.legacy.userProfileCustomizations.stylesheets" "$USER_JS" 2>/dev/null; then
    echo 'user_pref("toolkit.legacy.userProfileCustomizations.stylesheets", true);' >> "$USER_JS"
fi

echo "Installed SpaceFox theme into $PROFILE/chrome/"
