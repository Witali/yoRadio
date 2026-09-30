#!/usr/bin/env python3
"""Run the cache-test flash image twice with a plugin-enabled Linux QEMU."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from analyze import analyze


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("qemu", "bios", "flash", "plugin", "output"):
        parser.add_argument(f"--{option}", type=Path, required=True)
    parser.add_argument("--qemu-source-revision", required=True)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    for name in ("qemu", "bios", "flash", "plugin", "output"):
        setattr(args, name, getattr(args, name).resolve())
        if "," in str(getattr(args, name)):
            parser.error("QEMU comma-separated options require paths without commas")
    args.output.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent
    root = source.parents[2]
    fixture_root = root / "tests/fixtures/aac_stream_format"
    manifest = json.loads((fixture_root / "manifest.json").read_text())
    fixtures = {}
    for name in ("lc-48000-stereo.aac", "he-48000-stereo.aac", "hev2-44100-stereo.aac"):
        path = fixture_root / name
        expected = manifest["files"][name]
        digest = sha(path)
        if digest != expected["sha256"] or path.stat().st_size != expected["size_bytes"]:
            raise ValueError(f"Fixture mismatch: {name}")
        fixtures[name] = digest
    provenance = {
        "qemu_source_revision": args.qemu_source_revision,
        "qemu_version": subprocess.check_output([str(args.qemu), "--version"], text=True).strip(),
        "qemu_sha256": sha(args.qemu), "plugin_sha256": sha(args.plugin),
        "flash_sha256": sha(args.flash),
        "sources_sha256": {p.name: sha(p) for p in (
            source / "esp32c3_cache.c", source / "cache_model.h",
            root / "idf/esp32c3-oled-native/main/qemu_cache_test.c")},
        "fixture_manifest_sha256": sha(root / "tests/fixtures/aac_stream_format/manifest.json"),
        "fixtures_sha256": fixtures,
        "host_wall_time_is_not_guest_cpu_time": True, "runs": [],
    }
    # The merged image normally sits next to these ESP-IDF build outputs.
    provenance["firmware_build_files_sha256"] = {
        name: sha(args.flash.parent / name)
        for name in ("sdkconfig", "yoradio_esp32c3_oled_native.elf", "yoradio_esp32c3_oled_native.bin")
        if (args.flash.parent / name).is_file()
    }
    for run in (1, 2):
        stem = args.output / f"run-{run}"
        trace = stem.with_suffix(".json")
        # Reject stale output if a failed launch leaves an earlier report behind.
        if trace.exists():
            trace.unlink()
        command = [str(args.qemu), "-M", "esp32c3,audiodev=audio0", "-nographic",
                   "-no-reboot", "-snapshot", "-icount", "shift=0,align=off,sleep=off",
                   "-L", str(args.bios), "-audiodev", f"wav,id=audio0,path={stem}.wav,out.frequency=48000",
                   "-drive", f"file={args.flash},if=mtd,format=raw",
                   "-plugin", f"{args.plugin},out={trace}"]
        start = time.monotonic()
        with stem.with_suffix(".log").open("w", encoding="utf-8") as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT,
                           timeout=args.timeout, check=True)
        summary = analyze(stem.with_suffix(".log").read_text(encoding="utf-8"),
                          json.loads(trace.read_text()))
        if stem.with_suffix(".wav").stat().st_size <= 44:
            raise ValueError("No virtual PCM output")
        stem.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        provenance["runs"].append({"run": run, "host_elapsed_seconds": time.monotonic() - start,
                                   "command": command, "log_sha256": sha(stem.with_suffix(".log")),
                                   "trace_sha256": sha(trace)})
        print(f"CACHE_TRACE_PASS run={run}", flush=True)
    if sha(args.flash) != provenance["flash_sha256"]:
        raise ValueError("Input flash image was modified")
    (args.output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
