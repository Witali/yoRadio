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
            f"| {path.parent.parent.name}/{path.stem} | {windows[0]['codec']} | {len(windows)} | "
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


if __name__ == "__main__":
    main()