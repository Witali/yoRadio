"""Pass the external test identity privately to the pinned WSS campaign.

Dry-run unless --execute is supplied. Never print private arguments or copy
certificate keys, NVS, composed flash, raw MI or packet capture into this tree.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("drained", "withheld", "read-resume"), required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--execute", action="store_true")
    options = parser.parse_args()
    assert 1 <= len(options.label) <= 96
    assert all(char in "abcdefghijklmnopqrstuvwxyz0123456789-" for char in options.label)
    base = Path(__file__).resolve().parent
    root = base.parents[1]
    material = json.loads((root / ".build/cws-stream26/wss-material-location.json").read_bytes())
    assert material["private"] is True and material["excluded_from_publication"] is True
    files = material["files"]
    assert all(isinstance(files[name], str) for name in ("ca", "certificate", "key"))
    assert isinstance(material["openssl"], str)
    command = [sys.executable, "-u", "-B", str(base / "run-pressure-v5.py"),
               "--mode", options.mode, "--transport", "wss", "--output",
               str(root / ".build/cpbuf24" / options.label), "--keep-private",
               "--ca", files["ca"], "--certificate", files["certificate"],
               "--key", files["key"], "--openssl", material["openssl"]]
    if options.execute:
        command.append("--execute")
    return subprocess.run(command, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
