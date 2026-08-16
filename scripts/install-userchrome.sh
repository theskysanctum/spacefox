#!/bin/sh
# Regenerates SpaceFox's theme from CosmOS's theme.py (see
# theme/generate_userchrome.py) and installs it into a real Firefox
# profile's chrome/ directory -- including flipping the pref that makes
# Firefox load userChrome.css/userContent.css at all (off by default
# upstream, since Firefox 69).
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
