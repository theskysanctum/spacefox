#!/usr/bin/env python3
import json
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

EXTENSIONS_ROOT = Path(__file__).resolve().parent
SPACEFOX_ROOT = EXTENSIONS_ROOT.parent
OUT_DIR = EXTENSIONS_ROOT / "generated"
SPACEFOX_SCRIPTS_DIR = EXTENSIONS_ROOT / "spacefox-scripts"
SPACEFOX_SCRIPTS_ID = "scripts@spacefox.local"
INSTALL_DIR = "/usr/lib/spacefox"


def fetch_amo_bundle(settings: dict) -> None:
    bundle = json.loads((EXTENSIONS_ROOT / "bundle.json").read_text())
    for entry in bundle:
        slug = entry["slug"]
        data = json.loads(
            urllib.request.urlopen(f"https://addons.mozilla.org/api/v5/addons/addon/{slug}/").read()
        )
        guid = data["guid"]
        url = data["current_version"]["file"]["url"]
        dest = OUT_DIR / f"{guid}.xpi"
        print(f"{slug} -> {guid}")
        urllib.request.urlretrieve(url, dest)
        settings[guid] = {
            "installation_mode": "force_installed",
            "install_url": f"file://{INSTALL_DIR}/distribution/extensions/{guid}.xpi",
        }


def package_spacefox_scripts(settings: dict) -> None:
    subprocess.run(
        [sys.executable, str(SPACEFOX_ROOT / "userscripts" / "generate_crt_overlay.py")],
        check=True,
    )

    dest = OUT_DIR / f"{SPACEFOX_SCRIPTS_ID}.xpi"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in SPACEFOX_SCRIPTS_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(SPACEFOX_SCRIPTS_DIR))
    print(f"scripts -> {SPACEFOX_SCRIPTS_ID}")
    settings[SPACEFOX_SCRIPTS_ID] = {
        "installation_mode": "force_installed",
        "install_url": f"file://{INSTALL_DIR}/distribution/extensions/{SPACEFOX_SCRIPTS_ID}.xpi",
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    settings = {}
    fetch_amo_bundle(settings)
    package_spacefox_scripts(settings)

    policies = {
        "policies": {
            "ExtensionSettings": settings,
            "Preferences": {
                "xpinstall.signatures.required": {"Value": False, "Status": "locked"},
            },
        }
    }
    (OUT_DIR / "policies.json").write_text(json.dumps(policies, indent=2))
    print(f"Wrote {OUT_DIR}/policies.json")


if __name__ == "__main__":
    main()
