"""Validate physical C3 DIO/QIO evidence against the exact saved app bytes."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import mean
import zlib

from analyze_hardware import CASES, CPU_HZ, parse, rows


def validate(log, binary, mode, mhz):
    if (mode, mhz) not in {("dio", 80), ("qio", 40), ("qio", 80)}:
        raise ValueError("Unsupported flash comparison variant")
    # IDF deliberately sets ESPTOOLPY_FLASHMODE="dio" even for the QIO
    # choice: ROM loads the bootloader in DIO; that bootloader enables QIO.
    # These legacy log labels contain that image-header setting. The SPI0
    # register below is the independent proof of the actual running mode.
    probes, decoded = parse(log, "hardware", flash_mhz=mhz, flash_test=True)
    env = rows(log, "FLASH_ENV")
    if len(env) != 1:
        raise ValueError("Missing or duplicate runtime flash registers")
    e = env[0]
    ctrl, clock = int(e["ctrl"], 0), int(e["clock"], 0)
    mode_mask = (1 << 24) | (1 << 23) | (1 << 20) | (1 << 14)
    expected = 1 << (24 if mode == "qio" else 23)
    divider = 1 if clock & (1 << 31) else ((clock >> 16) & 255) + 1
    if (ctrl & mode_mask != expected or e["configured"] != "dio"
            or e["configured_mhz"] != f"{mhz}m"
            or int(e["source_mhz"]) != 80 or int(e["divider"]) != divider
            or 80 != mhz * divider or int(e["actual_mhz"]) != mhz
            or int(e["physical_bytes"]) != 4 * 1024 * 1024):
        raise ValueError("Runtime flash mode/clock/size does not match")
    reads = rows(log, "FLASH_READ")
    if len(reads) != 16 or [int(r["pass"]) for r in reads] != list(range(1, 17)):
        raise ValueError("Incomplete or duplicate flash read passes")
    expected_crc = zlib.crc32(binary)
    if len(binary) <= 32 * 1024:
        raise ValueError("Image does not exceed the hardware cache")
    offsets = {int(r["offset"], 0) for r in reads}
    if len(offsets) != 1 or not offsets <= {0x10000, 0x1e0000}:
        raise ValueError("Unexpected application partition")
    if any(int(r["bytes"]) != len(binary) or int(r["crc32"], 0) != expected_crc
           for r in reads):
        raise ValueError("Mapped flash read differs from saved app.bin")
    return dict(environment=e, app_sha256=hashlib.sha256(binary).hexdigest(),
                image_bytes=len(binary), read_passes=len(reads),
                read_bytes=len(reads) * len(binary), crc32=f"0x{expected_crc:08x}",
                probes=probes, decoded=decoded)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", nargs=4, action="append", required=True,
                        metavar=("MODE", "MHZ", "LOG", "APP_BIN"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    groups = {}
    for mode, mhz, log, binary in args.run:
        result = validate(Path(log).read_text(encoding="utf-8"),
                          Path(binary).read_bytes(), mode, int(mhz))
        result["log"] = Path(log).name
        groups.setdefault(f"{mode}{mhz}", []).append(result)
    if set(groups) != {"dio80", "qio40", "qio80"} or any(len(v) < 2 for v in groups.values()):
        raise ValueError("Need at least two complete boots of every variant")
    summary = dict(target="esp32c3", cpu_hz=CPU_HZ, deep_sleep=False,
                   whole_radio_tested=False, power_cycle_tested=False, variants={})
    for variant, runs in groups.items():
        if len({r["app_sha256"] for r in runs}) != 1:
            raise ValueError("Different app images within one variant")
        cases = {}
        for case in CASES:
            selected = [d for r in runs for d in r["decoded"]
                        if d["case"] == case and d["mode"] == "continuous"]
            cases[case] = dict(windows=len(selected),
                decoder_cpu_pct=mean(d["ticks"] / CPU_HZ / (d["samples"] / d["rate"]) * 100
                                     for d in selected))
        summary["variants"][variant] = dict(
            boots=len(runs), app_sha256=runs[0]["app_sha256"],
            image_bytes=runs[0]["image_bytes"], crc32=runs[0]["crc32"],
            registers=runs[0]["environment"],
            read_passes=sum(r["read_passes"] for r in runs),
            read_bytes=sum(r["read_bytes"] for r in runs), cases=cases,
            cold_256_line_cycles=mean(p["cold_ticks"] for r in runs for p in r["probes"]
                                      if p["lines"] == 256))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
