#!/usr/bin/env python3
"""Summarize five-second ESP8266 audio profile windows from UART logs."""

from __future__ import annotations

import argparse
import pathlib
import re
import statistics

ANSI = re.compile(r"\x1b\[[0-9;]*m")
HEADER = re.compile(
    r"=== (?P<codec>\w+) window=(?P<window>\d+) ms "
    r"audio=(?P<audio>\d+) ms \((?P<realtime>\d+\.\d+)% realtime\) "
    r"frames=(?P<frames>\d+) net=(?P<net>\d+) kbps ==="
)
STAGE = re.compile(
    r"(?P<name>tcp_wait|frame_scan|decode_core|pcm_output|normalize|"
    r"spi_queue_wait)=(?P<ms>\d+\.\d+) ms \((?P<load>\d+\.\d+)%\)"
)
CODEC_STAGE = re.compile(
    r"codec_stage=(?P<name>[a-z_]+) time=(?P<ms>\d+\.\d+) ms "
    r"wall=(?P<wall>\d+\.\d+)% core=(?P<core>\d+\.\d+)% "
    r"calls=(?P<calls>\d+) max=(?P<max>\d+) us rejected=(?P<rejected>\d+)"
)
PDM = re.compile(r"gain\+mix\+pdm=(?P<ms>\d+\.\d+) ms \((?P<load>\d+\.\d+)%\)")
CPU = re.compile(r"cpu busy=(?P<busy>\d+\.\d+)% idle=(?P<idle>\d+\.\d+)%")
HEAP = re.compile(
    r"heap total=(?P<total>\d+) used=(?P<used>\d+) "
    r"free=(?P<free>\d+) min_free=(?P<min_free>\d+)"
)


def parse_log(path: pathlib.Path) -> list[dict[str, float]]:
    windows: list[dict[str, float]] = []
    current: dict[str, float] | None = None
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = ANSI.sub("", raw_line)
        match = HEADER.search(line)
        if match:
            current = {
                key: float(value) if key in {"realtime"} else int(value)
                for key, value in match.groupdict().items()
                if key != "codec"
            }
            current["codec"] = match.group("codec")
            windows.append(current)
            continue
        if current is None:
            continue
        match = STAGE.search(line)
        if match:
            current[f"{match.group('name')}_ms"] = float(match.group("ms"))
            current[f"{match.group('name')}_load"] = float(match.group("load"))
            continue
        match = CODEC_STAGE.search(line)
        if match:
            name = match.group("name")
            for key in ("ms", "wall", "core"):
                current[f"codec_{name}_{key}"] = float(match.group(key))
            for key in ("calls", "max", "rejected"):
                current[f"codec_{name}_{key}"] = int(match.group(key))
            continue
        match = PDM.search(line)
        if match:
            current["pdm_ms"] = float(match.group("ms"))
            current["pdm_load"] = float(match.group("load"))
            continue
        match = CPU.search(line)
        if match:
            current["cpu_busy"] = float(match.group("busy"))
            current["cpu_idle"] = float(match.group("idle"))
            continue
        match = HEAP.search(line)
        if match:
            current.update({key: int(value) for key, value in match.groupdict().items()})
    return windows


def central(windows: list[dict[str, float]], key: str) -> float:
    return statistics.median(float(window[key]) for window in windows if key in window)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("logs", nargs="+", type=pathlib.Path)
    args = parser.parse_args()

    print("| Run | Codec | Windows | Realtime | CPU busy | CPU idle | "
          "Decode | PCM output | PDM compute | Free heap | Used heap | Min free |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for path in args.logs:
        windows = [window for window in parse_log(path) if "cpu_busy" in window]
        if not windows:
            raise SystemExit(f"{path}: no complete CPU profile windows")
        print(
            f"| {path.parent.name}/{path.stem} | {windows[0]['codec']} | {len(windows)} | "
            f"{central(windows, 'realtime'):.1f}% | "
            f"{central(windows, 'cpu_busy'):.1f}% | "
            f"{central(windows, 'cpu_idle'):.1f}% | "
            f"{central(windows, 'decode_core_load'):.1f}% | "
            f"{central(windows, 'pcm_output_load'):.1f}% | "
            f"{central(windows, 'pdm_load'):.1f}% | "
            f"{central(windows, 'free'):.0f} B | "
            f"{central(windows, 'used'):.0f} B | "
            f"{min(int(window['min_free']) for window in windows)} B |"
        )

    print()
    print("| Run | Stage | Wall | Decoder core | Calls/window | Max call | Rejected/window |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for path in args.logs:
        windows = [window for window in parse_log(path) if "cpu_busy" in window]
        names = sorted({
            key[len("codec_"):-len("_wall")]
            for window in windows
            for key in window
            if key.startswith("codec_") and key.endswith("_wall")
        })
        for name in names:
            print(
                f"| {path.parent.name}/{path.stem} | {name} | "
                f"{central(windows, f'codec_{name}_wall'):.1f}% | "
                f"{central(windows, f'codec_{name}_core'):.1f}% | "
                f"{central(windows, f'codec_{name}_calls'):.0f} | "
                f"{central(windows, f'codec_{name}_max'):.0f} us | "
                f"{central(windows, f'codec_{name}_rejected'):.0f} |"
            )


if __name__ == "__main__":
    main()
