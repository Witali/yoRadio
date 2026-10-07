"""Passively capture the cache bench; never reset or drive boot control lines."""
import argparse
from pathlib import Path
import time

import serial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=120)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    port = serial.Serial(port=None, baudrate=115200, timeout=0.25)
    port.dtr = False
    port.rts = False
    port.port = args.port
    port.open()
    data = bytearray()
    deadline = time.monotonic() + args.timeout
    with port, args.output.open("wb") as log:
        while time.monotonic() < deadline:
            chunk = port.read(max(1, port.in_waiting))
            log.write(chunk)
            log.flush()
            data.extend(chunk)
            if b"CACHE_HW_PASS runtime=hardware" in data:
                print(f"Hardware benchmark passed; log: {args.output}")
                return
            if b"assert failed:" in data or b"Guru Meditation" in data:
                raise SystemExit(f"Firmware failure; inspect {args.output}")
    raise SystemExit(f"No completion marker within {args.timeout}s; inspect {args.output}")


if __name__ == "__main__":
    main()
