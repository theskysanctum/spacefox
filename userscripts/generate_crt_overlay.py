#!/usr/bin/env python3
import base64
import os
import subprocess
import sys
import tempfile
from pathlib import Path

USERSCRIPTS_ROOT = Path(__file__).resolve().parent
SPACEFOX_ROOT = USERSCRIPTS_ROOT.parent
COSMOS_ROOT = Path(os.environ.get("COSMOS_ROOT", Path.home() / "os" / "cosmos"))
sys.path.insert(0, str(COSMOS_ROOT / "userland"))

from backend.screen_profiles import PROFILES  # noqa: E402

USERSCRIPT_OUT_DIR = USERSCRIPTS_ROOT / "generated"
EXTENSION_OUT_DIR = SPACEFOX_ROOT / "extensions" / "spacefox-scripts" / "generated"
PROFILE = PROFILES["MEDIA_SCANLINES"]

USERSCRIPT_HEADER = """// ==UserScript==
// @name         SpaceFox CRT Overlay
// @namespace    https://github.com/theskysanctum/spacefox
// @version      1.0
// @match        *://*/*
// @grant        none
// @run-at       document-start
// ==/UserScript==
"""


def build_tile_data_uri() -> str:
    r, g, b = PROFILE.color
    alpha = PROFILE.alpha / 255
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        subprocess.run(
            [
                "magick", "-size", f"1x{PROFILE.spacing}", "xc:none",
                "-fill", f"rgba({r},{g},{b},{alpha:.3f})",
                "-draw", "point 0,0",
                tmp.name,
            ],
            check=True,
        )
        tile_b64 = base64.b64encode(Path(tmp.name).read_bytes()).decode()
    return f"data:image/png;base64,{tile_b64}"


def main():
    USERSCRIPT_OUT_DIR.mkdir(parents=True, exist_ok=True)
    EXTENSION_OUT_DIR.mkdir(parents=True, exist_ok=True)

    data_uri = build_tile_data_uri()
    body = (USERSCRIPTS_ROOT / "crt-overlay.body.js").read_text().replace(
        "__CRT_TILE_DATA_URI__", data_uri
    )

    (USERSCRIPT_OUT_DIR / "crt-overlay.user.js").write_text(USERSCRIPT_HEADER + body)
    (EXTENSION_OUT_DIR / "crt-overlay.js").write_text(body)
    print(f"Wrote {USERSCRIPT_OUT_DIR}/crt-overlay.user.js")
    print(f"Wrote {EXTENSION_OUT_DIR}/crt-overlay.js")


if __name__ == "__main__":
    main()
