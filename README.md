# SpaceFox

A patch-based Firefox rebrand, in the same shape as LibreWolf/Waterfox: no
full Gecko source fork, no maintained divergent history. Instead, `scripts/`
downloads an official Firefox release source tarball, and `branding/` +
`patches/` apply on top of it fresh, every time. Firefox's own upstream
history is never vendored into this repo -- just the diff we carry.

## Goal: a controller-native browser

SpaceFox exists to be driven entirely with a game controller and embedded
inside a pygame frontend, rather than run as a bare kiosk window driven by
synthetic mouse input. It's the browser component for
[CosmOS](https://github.com/theskysanctum/gamebox) (a game-console OS),
where the current Brave-based Web/Streaming feature drives an unmodified
kiosk browser purely through synthetic X11 cursor/scroll events -- workable,
but the browser itself has no idea a controller exists. SpaceFox's actual
patches (beyond branding) will build toward the browser itself understanding
controller input and toward a pygame-side wrapper that can host/frame it,
instead of everything living on the synthetic-input side. Not yet
implemented -- currently branding-only, see `patches/series`.

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
the OSK bridge) is built as Violentmonkey-format userscripts rather than
patches or a hand-rolled WebExtension: a content-script-only concern with no
need for a persistent background page, since SpaceFox is a single-window
kiosk browser -- only one page is ever meaningfully active at a time, so
each page opening its own connection when it needs something (like the OSK)
is simpler than coordinating a shared one.

`userscripts/generate_crt_overlay.py` reads CosmOS's real
`backend/screen_profiles.py` (`MEDIA_SCANLINES`, the same profile
`gamebox.py` already applies to Browser/Streaming today via the X11-level
`crt_overlay.py`) and renders a tiny tileable PNG through ImageMagick,
base64-embedded into `userscripts/generated/crt-overlay.user.js` from
`userscripts/crt-overlay.template.js`. Runs entirely in-page (a fixed,
`pointer-events: none` div), so it can never cover Firefox's own chrome by
construction -- unlike the X11 overlay, no window-geometry coordination
needed. `gamebox.py`'s `crt_overlay_backend.show("browser"/"streaming", ...)`
calls should eventually stop firing once this replaces them for SpaceFox
specifically; not done yet, that's a CosmOS-side integration change.

**Not yet wired up:** force-installing Violentmonkey via `policies.json`
gets the extension installed, but doesn't make it load our script --
Violentmonkey normally adds scripts through its own UI (visit a raw
`.user.js` URL, click install) or by pre-seeding its internal storage,
which is fragile/version-dependent and not worth hand-rolling. Needs either
a first-boot install step, or -- probably cleaner -- wrapping our own
scripts as their own small force-installed WebExtension (`content_scripts`
matching `<all_urls>`, no UI) the same way as uBlock Origin/Dark Reader, and
keeping Violentmonkey around only for future GreasyFork scripts a user adds
themselves.

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
  force-installed extension bundle (uBlock Origin, Dark Reader), see below.
- `scripts/install-extensions.sh` -- fetches the bundle and installs it into
  a real build's output directory.
- `userscripts/generate_crt_overlay.py` / `userscripts/crt-overlay.template.js`
  -- generates `userscripts/generated/crt-overlay.user.js`, see below.
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
