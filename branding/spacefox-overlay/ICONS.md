Drop SpaceFox's actual icon artwork directly in this `spacefox-overlay/`
directory (not in a subfolder -- `setup-branding.sh` copies this whole
directory's contents straight into the branding dir's root, mirroring
Firefox's own flat branding layout). This file itself is documentation,
not consumed by the build -- delete it once real artwork is in place.

Filenames Firefox's `unofficial` branding directory ships (confirm the
exact list against the fetched source for the version SpaceFox is
tracking -- it can shift between releases):

- default16.png, default22.png, default24.png, default32.png,
  default48.png, default64.png, default128.png
- mozicon128.png
- firefox.ico (Windows), firefox.icns (macOS)
- content/about-logo.png, content/about-logo@2x.png

No SpaceFox artwork exists yet -- `setup-branding.sh` will currently just
carry over the placeholder `unofficial` branding's own icons for anything
not overlaid here.
