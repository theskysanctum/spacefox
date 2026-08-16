# SpaceFox

A patch-based Firefox rebrand, in the same shape as LibreWolf/Waterfox: no
full Gecko source fork, no maintained divergent history. Instead, `scripts/`
downloads an official Firefox release source tarball, and `branding/` +
`patches/` apply on top of it fresh, every time. Firefox's own upstream
history is never vendored into this repo -- just the diff we carry.

## Goal: a controller-native browser

SpaceFox exists to be driven entirely with a game controller, rather than
run as a bare kiosk window driven only by synthetic mouse input. It's the
browser component for [CosmOS](https://github.com/theskysanctum/gamebox)
(a game-console OS), where the current Brave-based Web/Streaming feature
drives an unmodified kiosk browser purely through synthetic X11
cursor/scroll events -- workable, but the browser itself has no idea a
controller exists.

Rather than patching Gecko's own C++ input layer to teach the browser
about controllers directly, this is built as a small first-party
WebExtension (`extensions/spacefox-scripts/`, see below) that talks to
CosmOS's `gamebox.py` -- which already owns the real controller/joystick
reads -- over a local WebSocket. `gamebox.py` relays D-pad input as nav
commands; the extension does DOM-level spatial navigation and on-screen-
keyboard triggering. No Gecko patches needed for any of this -- see
"Controller navigation + OSK" below for what's actually built vs. still
a page-content-only concern (native browser chrome interaction, if ever
needed beyond back/forward/tabs, would be the one thing that *does* need
a patch or a different mechanism).

## Theming: matches CosmOS's own look, generated from its theme.py

Rather than a static hand-written stylesheet, `theme/generate_userchrome.py`
imports CosmOS's actual `userland/backend/theme.py` (the single source of
truth for the console's own dark-background/neon-gradient palette, already
used the same way by `userland/backend/web_upload.py`'s web portal) and
generates a `userChrome.css`/`userContent.css` pair from its real values --
`theme/generated/`, gitignored, regenerated on demand rather than committed,
so it can never drift out of sync with CosmOS's palette. It also vendors in
CosmOS's own three font weights (`fonts/{regular,light,bold}.ttf`) under the
same `CosmOSFont` family name the web portal uses, so text renders in the
same typeface CosmOS's own UI does. Currently reads as "CosmOS's own retro
dark/neon console look carried over into Firefox's chrome" -- if "older"
turns out to mean something more specific (a particular past Firefox UI
era, actual skeuomorphic aging, etc.) once this is seen live, the generator
is the one place to adjust, not scattered CSS.

Applies only to Firefox's own UI (`userChrome.css`) and Firefox's own
built-in pages like `about:*`/reader view/error pages (`userContent.css`)
-- real websites' own CSS always wins on their own pages, same as any
browser theme.

Install into a real profile with `./scripts/install-userchrome.sh
<profile-path>` -- also flips `toolkit.legacy.userProfileCustomizations.
stylesheets` (off by default upstream since Firefox 69, required for
`userChrome.css`/`userContent.css` to load at all).

The generated `userChrome.css` also sets which chrome survives: back/
forward, the urlbar, and tabs stay (`#nav-bar`, `#TabsToolbar`); the
bookmarks toolbar, the app/hamburger menu, and the extensions button are
hidden (`#PersonalToolbar`, `#PanelUI-button`, `#unified-extensions-button`).
Full chrome removal (Streaming: no UI at all, no way to escape back to raw
Firefox) isn't built yet -- needs an Openbox window rule plus a content
script intercepting escape-key combos, not just CSS.

## Bundled extensions

`extensions/bundle.json` lists AMO slugs (currently uBlock Origin,
Dark Reader, Violentmonkey); `extensions/fetch_extensions.py` resolves each through
Mozilla's real addon API (`addons.mozilla.org/api/v5/addons/addon/<slug>/`),
downloads its current `.xpi`, and writes an `ExtensionSettings` policies.json
force-installing them by their real extension IDs -- same enterprise-policy
mechanism (`policies.json`'s `ExtensionSettings`/`force_installed`) LibreWolf
and other Firefox forks already rely on for exactly this, works the same on
an unofficial build.

`install_url` in the generated policies.json points at
`/usr/lib/spacefox/distribution/extensions/<id>.xpi` -- a placeholder for
wherever SpaceFox actually ends up installed; not yet reconciled with how
CosmOS's own Containerfile will eventually package SpaceFox. Update
`INSTALL_DIR` in `extensions/fetch_extensions.py` once that's decided.

`scripts/install-extensions.sh` re-fetches and drops the bundle + policy
into a real build's output directory for local testing.

## Userscripts

Page-level behavior (the CRT/scanline overlay, and eventually spatial nav +
the OSK bridge) is written as content-script logic with no need for a
persistent background page, since SpaceFox is a single-window kiosk browser
-- only one page is ever meaningfully active at a time, so each page opening
its own connection when it needs something (like the OSK) is simpler than
coordinating a shared one.

Each script is authored once (`userscripts/crt-overlay.body.js`) and shipped
two ways from that single source, generated by
`userscripts/generate_crt_overlay.py`:

- **`userscripts/generated/crt-overlay.user.js`** -- Violentmonkey/GreasyFork
  format (with a `// ==UserScript==` header), for manual install or local
  dev iteration. Not auto-loaded by anything -- Violentmonkey normally adds
  scripts through its own UI (visit a raw `.user.js` URL, click install) or
  by pre-seeding its internal storage, which is fragile/version-dependent
  and not worth hand-rolling for our own first-party scripts.
- **`extensions/spacefox-scripts/generated/crt-overlay.js`** -- the same
  body, headerless, as the content script for `extensions/spacefox-scripts/`
  -- a small first-party WebExtension (just `manifest.json` +
  `content_scripts` matching `<all_urls>`, no UI) that `extensions/
  fetch_extensions.py` zips into `scripts@spacefox.local.xpi` and
  force-installs via `policies.json`, exactly the same mechanism as
  uBlock Origin/Dark Reader/Violentmonkey. This is what actually runs at
  runtime, deterministically, with no manual install step. Violentmonkey
  stays bundled for a user manually adding their own GreasyFork scripts
  later, not for shipping SpaceFox's own.

Since it's unsigned (no Mozilla AMO review -- it's our own local build,
never published), `fetch_extensions.py` also sets
`xpinstall.signatures.required: false` via `policies.json`'s `Preferences`
block, matching how unofficial/unbranded Firefox builds disable the
signing requirement in general. Real, documented policy keys, but
untested against SpaceFox's own real build yet -- worth confirming on
first boot, same as the DRM caveat above.

The CRT overlay itself reads CosmOS's real `backend/screen_profiles.py`
(`MEDIA_SCANLINES`, the same profile `gamebox.py` already applies to
Browser/Streaming today via the X11-level `crt_overlay.py`) and renders a
tiny tileable PNG through ImageMagick, base64-embedded into the script body.
Runs entirely in-page (a fixed, `pointer-events: none` div), so it can never
cover Firefox's own chrome by construction -- unlike the X11 overlay, no
window-geometry coordination needed. `gamebox.py`'s `crt_overlay_backend.
show("browser"/"streaming", ...)` calls should eventually stop firing once
this replaces them for SpaceFox specifically; not done yet, that's a
CosmOS-side integration change.

## Controller navigation + OSK

Real, working, verified end to end in an actual running Firefox (not just
Python-side, not just design) as of this writing -- see "Live-tested
findings" below for exactly what was checked and one real deployment
problem this surfaced.

- **`userland/backend/osk_bridge.py`** (in the CosmOS repo) -- a local
  WebSocket server (`127.0.0.1:8756`) `gamebox.py` starts once at init.
  Drains incoming messages every frame; connected clients can also be sent
  messages via `osk_bridge.send()`. Tested live with a real WebSocket
  client both directions before wiring it into `gamebox.py`.
- **`extensions/spacefox-scripts/spacefox-bridge.js`** -- the extension side
  of that connection: one shared `WebSocket` per page (reconnects on close),
  exposing `window.__spacefoxSend()`/`__spacefoxOnMessage()` for the other
  content scripts in the same execution context to use. Loads first in
  `manifest.json`'s `content_scripts` list -- the other two depend on its
  globals existing already.
- **`osk-bridge.js`** -- listens for `focusin`/`focusout` on editable
  elements (text inputs, textareas, contenteditable), sends
  `{"action":"show"}`/`{"action":"hide"}`. `gamebox.py`'s
  `poll_osk_bridge()` turns those into the exact same `toggle_osk()` call
  its own native UI already uses -- the existing OSK state machine
  (`osk_row`/`osk_col`/`osk_shift`, driven by real D-pad input) and its
  existing XTEST keystroke delivery (`cursor.type_key()`) needed zero
  changes; they already type into whatever's focused at the OS level,
  browser text field included. The bridge's only job is deciding *when*
  to show/hide it automatically, not how typing works.
- **`spatial-nav.js`** -- receives `{"action":"nav","direction":...}` from
  `gamebox.py` (sent when D-pad keys are pressed while browsing with the
  OSK inactive -- confirmed those keys were previously unused in that
  state, not repurposed from something else) and moves DOM focus between
  focusable elements (`a[href]`, `button`, `input`, `[tabindex]`, etc.)
  using a primary-axis-distance-plus-perpendicular-penalty heuristic (the
  same general shape TV/console browsers' spatial nav uses) -- pure
  in-page DOM traversal, no Gecko patch involved. `{"action":"activate"}`
  clicks whatever's currently focused.

Deliberately NOT relayed the other way (page reading the controller
directly via `navigator.getGamepads()`): the Gamepad API only reports
state after a user has already pressed a button once on that page (a
real, standard privacy-fingerprinting mitigation browsers implement), so
spatial nav wouldn't be available immediately on page load. Keeping
`gamebox.py` as the single owner of raw controller reads, same as every
other CosmOS input path, avoids that.

### Live-tested findings

Actually loaded into a real, unmodified system Firefox (temporarily, for
testing only) and driven end to end against the real `osk_bridge.py`
server -- not just read for syntax. Confirmed live:

- The CRT overlay actually renders, visibly, on a real page.
- The extension's WebSocket actually connects to `osk_bridge.py` and
  survives/reconnects when the server restarts.
- Clicking into and out of a real `<input>` sent real `{"action":"show"}`/
  `{"action":"hide"}` messages, received by the real server.
- Sending real `{"action":"nav","direction":"down"}` messages from the
  server moved real DOM focus, in order, exactly as the algorithm
  predicts (`link1` -> `textbox` -> `btn1`).

One real problem this surfaced: **force-installing via `policies.json`
did not actually work** on this machine's Firefox, even though
`about:policies` showed the policy as "Active" -- `about:addons`/
`about:debugging` showed no extension ever got installed, and
`extensions.json` had no record of an install attempt. The policy engine
read and parsed the config correctly; something in `ExtensionSettings`
force-install processing for a local unsigned `file://` `install_url`
silently didn't follow through, on this Firefox build at least. Loading
the exact same `extensions/spacefox-scripts/manifest.json` as a temporary
add-on via `about:debugging` worked immediately and is what all the
findings above are based on. This needs real investigation before relying
on the force-install path for CosmOS's actual deployment -- possible
causes not yet ruled out: a Fedora-packaging-specific quirk, a Firefox
version difference, or a genuine gap in how `install_url` handles local
files that AMO-hosted URLs don't hit.

**Not yet done:** none of this differentiates Browser vs. Streaming mode,
or handles the "Streaming: no way to escape" lockdown -- that's still an
Openbox-rule + key-interception problem, unrelated to this WebSocket.

## Why patch-based, not a full mozilla-central fork

A full fork (cloning mozilla-unified) means owning tens of GB of history and
rebasing SpaceFox's own changes against upstream forever. A patch-based
rebrand tracks upstream Firefox releases directly -- bump `VERSION`, re-run
the pipeline, re-apply patches (fixing any that no longer apply cleanly).
Far less maintenance for what SpaceFox actually needs: a renamed, rebranded
build, not a divergent codebase.

## Layout

- `VERSION` -- the Firefox release version SpaceFox currently tracks.
- `scripts/fetch-source.sh` -- resolves and downloads that version's source
  tarball from ftp.mozilla.org into `build/firefox-<version>/` (gitignored,
  regenerated every build).
- `scripts/setup-branding.sh` -- copies Firefox's own `browser/branding/
  unofficial/` (the directory upstream Firefox ships specifically for
  unofficial/community builds like this one) into `browser/branding/
  spacefox/` inside the extracted source, then overlays `branding/
  spacefox-overlay/` (our actual brand name, icons, wordmark) on top of it.
  Deliberately doesn't hand-author the branding directory's own Makefile.in/
  moz.build/jar.mn from scratch -- reuses Firefox's own scaffolding for
  those, only replaces the brand-identity files.
- `patches/` -- numbered `.patch` files (see `patches/series` for apply
  order) for anything beyond branding -- default prefs, UI tweaks, etc.
  Empty for now; branding-only until there's an actual patch to add.
- `mozconfigs/linux` -- the mozconfig passed to `./mach build`.
- `theme/generate_userchrome.py` -- generates `theme/generated/` (CSS +
  vendored fonts) from CosmOS's `theme.py`, see below.
- `scripts/install-userchrome.sh` -- regenerates the theme and installs it
  into a real Firefox profile's `chrome/` directory.
- `extensions/bundle.json` / `extensions/fetch_extensions.py` -- the
  force-installed extension bundle (uBlock Origin, Dark Reader,
  Violentmonkey, and SpaceFox's own first-party scripts), see below.
- `extensions/spacefox-scripts/` -- the first-party WebExtension that ships
  SpaceFox's own in-page scripts (see Userscripts below).
- `scripts/install-extensions.sh` -- fetches the bundle and installs it into
  a real build's output directory.
- `userscripts/crt-overlay.body.js` / `userscripts/generate_crt_overlay.py`
  -- generates both `userscripts/generated/crt-overlay.user.js` and
  `extensions/spacefox-scripts/generated/crt-overlay.js`, see below.
- `scripts/build.sh` -- orchestrates fetch -> branding -> patches -> mach
  build. NOT run automatically by anything -- a full Firefox build is a
  multi-hour, multi-GB, toolchain-heavy operation (needs `./mach bootstrap`
  first), so this is meant to be run by hand when actually ready to build.

## DRM (EME/Widevine)

`mozconfigs/linux` includes `--enable-eme=widevine`, which compiles in
Firefox's EME plumbing (this part is a straightforward build-time flag,
confirmed from LibreWolf's own published mozconfig, which ships the same
line for the same reason).

One real caveat, worth confirming on SpaceFox's actual first build rather
than assuming: Firefox's in-app Widevine CDM downloader has, at various
points, gated the download behind a Google-issued API key that only
official Mozilla builds carry -- meaning the in-app "Enable DRM" prompt can
fail on an unofficial build even with EME compiled in. If that happens, the
documented workaround (used by LibreWolf/Waterfox users) is sideloading the
CDM directly: copy `libwidevinecdm.so` (and its `manifest.json`) from a
real Firefox or Chrome install's `gmp-widevinecdm/<version>/` directory into
the same path under SpaceFox's own profile. Not verified against SpaceFox's
own build yet -- first real build should confirm which path applies.

## Building (once ready -- not automatic)

```
./scripts/fetch-source.sh      # downloads + extracts Firefox source
./scripts/setup-branding.sh    # brands the extracted source as SpaceFox
./scripts/build.sh             # mach bootstrap (first time) + mach build
```
