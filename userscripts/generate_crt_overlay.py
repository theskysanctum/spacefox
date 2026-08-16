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

OUT_DIR = USERSCRIPTS_ROOT / "generated"
PROFILE = PROFILES["MEDIA_SCANLINES"]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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

    data_uri = f"data:image/png;base64,{tile_b64}"
    template = (USERSCRIPTS_ROOT / "crt-overlay.template.js").read_text()
    (OUT_DIR / "crt-overlay.user.js").write_text(template.replace("__CRT_TILE_DATA_URI__", data_uri))
    print(f"Wrote {OUT_DIR}/crt-overlay.user.js")


if __name__ == "__main__":
    main()
