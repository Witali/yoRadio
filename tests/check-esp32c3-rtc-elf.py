"""Check the linked RTC region and all external wake-stub dependencies."""
import argparse
from pathlib import Path
import re
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--objdump", required=True)
parser.add_argument("--build", type=Path, required=True)
args = parser.parse_args()
elf = args.build / "yoradio_esp32c3_oled_native.elf"
obj = args.build / "esp-idf/main/CMakeFiles/__idf_main.dir/rtc_wake_stub_clock.c.obj"

def dump(option, path):
    return subprocess.check_output([args.objdump, option, str(path)], text=True)

symbols = {}
for line in dump("-t", elf).splitlines():
    fields = line.split()
    if fields and re.fullmatch(r"[0-9a-fA-F]{8,16}", fields[0]):
        symbols[fields[-1]] = int(fields[0], 16)
for name in ("g_rtc_clock", "rtc_clock_wake_stub"):
    assert 0x50000000 <= symbols[name] < 0x50002000, (name, symbols.get(name))

undefined = [line.split()[-1] for line in dump("-t", obj).splitlines()
             if "*UND*" in line]
assert undefined, "Expected external ROM/RTC dependencies"
for name in undefined:
    address = symbols[name]
    allowed = 0x40000000 <= address < 0x40090000 or 0x50000000 <= address < 0x50002000
    # The only external data register used by GPIO LL is the GPIO device.
    allowed |= name == "GPIO" and 0x60000000 <= address < 0x60100000
    assert allowed, f"Wake stub refers to non-retained symbol {name} at {address:#x}"

used = 0
for line in dump("-h", elf).splitlines():
    fields = line.split()
    if len(fields) >= 5 and fields[1].startswith((".rtc", ".rtc_")):
        size, address = int(fields[2], 16), int(fields[3], 16)
        assert 0x50000000 <= address and address + size <= 0x50002000, line
        used += size
print(f"PASS: {used}/8192 RTC bytes; {len(undefined)} dependencies all RTC, ROM or GPIO MMIO")
