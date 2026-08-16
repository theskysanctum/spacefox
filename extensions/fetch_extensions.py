#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

EXTENSIONS_ROOT = Path(__file__).resolve().parent
OUT_DIR = EXTENSIONS_ROOT / "generated"
INSTALL_DIR = "/usr/lib/spacefox"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bundle = json.loads((EXTENSIONS_ROOT / "bundle.json").read_text())

    settings = {}
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

    policies = {"policies": {"ExtensionSettings": settings}}
    (OUT_DIR / "policies.json").write_text(json.dumps(policies, indent=2))
    print(f"Wrote {OUT_DIR}/policies.json")


if __name__ == "__main__":
    main()
