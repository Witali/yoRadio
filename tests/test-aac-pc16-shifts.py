#!/usr/bin/env python3
"""Compile and run the actual PC16 arithmetic/storage test with UBSan.

Uses WSL GCC on Windows or native GCC on Linux; does not access a board.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def host_path(path):
    path = path.resolve()
    return "/mnt/" + path.drive[0].lower() + path.as_posix()[2:] if sys.platform == "win32" else str(path)


def execute(args):
    prefix = ["wsl.exe", "--exec"] if sys.platform == "win32" else []
    return subprocess.check_output(prefix + args, text=True)


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / "tests/native/aac_pc16_shifts_test.c"
    header = ROOT / "idf/esp32c3-oled-native/main/packed_complex16.h"
    executable = output / "pc16-shifts-test"
    command = ["gcc", "-O2", "-std=c11", "-Wall", "-Wextra", "-Werror", "-pedantic",
               "-fsanitize=undefined", "-fno-sanitize-recover=all",
               "-I" + host_path(header.parent), host_path(source), "-o", host_path(executable)]
    execute(command)
    result = json.loads(execute([host_path(executable)]))
    result["provenance"] = {
        "compiler": execute(["gcc", "--version"]).splitlines()[0], "command": command,
        "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (header, source, Path(__file__))}}
    report = output / "result.json"
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "provenance"}, indent=2))
    print(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/aac-pc16-shifts")
    run(parser.parse_args().output.resolve())
