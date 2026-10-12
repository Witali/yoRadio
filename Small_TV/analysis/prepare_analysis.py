#!/usr/bin/env python3
"""Validate the archived Small_TV dump and prepare an analysis-only RV32 ELF.

The synthetic .bss block helps Ghidra represent global variables. Its size is
not a recovered application RAM footprint. None of these outputs is a new
firmware build or intended for flashing.
"""

import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path


EXPECTED_SHA256 = "5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4"
APP_OFFSET = 0x10000
SECTION_NAMES = [".flash.rodata", ".dram.data", ".iram.vectors", ".flash.text", ".iram.text"]
DISPLAY_RANGES = [(0x42008BD2, 0x42008C4C), (0x42008D62, 0x42008E08),
                  (0x4200917C, 0x420095C4)]


def cstring(data):
    return data.split(b"\0", 1)[0].decode("ascii")


def parse_dump(data):
    if len(data) != 0x400000 or hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Input is not the verified Small_TV dump; obtain it with git lfs pull")
    partitions = []
    for offset in range(0x8000, 0x9000, 32):
        magic, kind, subtype, start, size, label, flags = struct.unpack_from("<HBBII16sI", data, offset)
        if magic == 0xEBEB:
            if hashlib.md5(data[0x8000:offset]).digest() != data[offset+16:offset+32]:
                raise ValueError("Partition-table MD5 mismatch")
            break
        if magic != 0x50AA:
            raise ValueError("Unexpected partition-table entry")
        partitions.append({"label": cstring(label), "type": kind, "subtype": subtype,
                           "offset": start, "size": size, "flags": flags})
    if data[APP_OFFSET] != 0xE9 or data[APP_OFFSET+1] != 5:
        raise ValueError("Unexpected application image header")
    cursor = APP_OFFSET + 24
    segments = []
    checksum = 0xEF
    for index in range(5):
        address, size = struct.unpack_from("<II", data, cursor)
        cursor += 8
        payload = data[cursor:cursor+size]
        if len(payload) != size:
            raise ValueError("Truncated application segment")
        for byte in payload:
            checksum ^= byte
        segments.append({"index": index, "section": SECTION_NAMES[index],
                         "address": address, "flash_offset": cursor, "size": size,
                         "sha256": hashlib.sha256(payload).hexdigest()})
        cursor += size
    checksum_offset = APP_OFFSET + ((cursor - APP_OFFSET + 15) // 16) * 16 - 1
    if data[checksum_offset] != checksum:
        raise ValueError("ESP image checksum mismatch")
    image_end = checksum_offset + 1
    if data[APP_OFFSET+23] != 1:
        raise ValueError("Expected appended application SHA-256")
    image_hash = hashlib.sha256(data[APP_OFFSET:image_end]).digest()
    if data[image_end:image_end+32] != image_hash:
        raise ValueError("Appended application SHA-256 mismatch")
    first = segments[0]["flash_offset"]
    descriptor = data[first:first+256]
    if struct.unpack_from("<I", descriptor)[0] != 0xABCD5432:
        raise ValueError("Missing ESP-IDF application descriptor")
    app = {"offset": APP_OFFSET, "entry_point": struct.unpack_from("<I", data, APP_OFFSET+4)[0],
           "version": cstring(descriptor[16:48]), "project": cstring(descriptor[48:80]),
           "build_time": cstring(descriptor[80:96]), "build_date": cstring(descriptor[96:112]),
           "idf_version": cstring(descriptor[112:144]), "original_elf_sha256": descriptor[144:176].hex(),
           "image_sha256": image_hash.hex(), "image_size_with_digest": image_end+32-APP_OFFSET,
           "image_checksum_valid": True, "appended_sha256_valid": True}
    return {"dump_sha256": EXPECTED_SHA256, "partitions": partitions,
            "partition_table_md5_valid": True, "application": app, "segments": segments}


def make_elf(data, report):
    segments = report["segments"]
    names = SECTION_NAMES + [".bss", ".shstrtab"]
    strings = bytearray(b"\0")
    name_offsets = {}
    for name in names:
        name_offsets[name] = len(strings)
        strings.extend(name.encode() + b"\0")
    output = bytearray(0x1000)
    sections = [(0,) * 10]
    headers = []
    for segment in segments:
        output.extend(b"\0" * (-len(output) % 16))
        offset = len(output)
        payload = data[segment["flash_offset"]:segment["flash_offset"]+segment["size"]]
        output.extend(payload)
        executable = segment["index"] in (2, 3, 4)
        writable = segment["index"] == 1
        flags = 2 | (4 if executable else 0) | (1 if writable else 0)
        sections.append((name_offsets[segment["section"]], 1, flags, segment["address"],
                         offset, len(payload), 0, 0, 16, 0))
        headers.append((1, offset, segment["address"], segment["address"], len(payload),
                        len(payload), 4 | (1 if executable else 0) | (2 if writable else 0), 16))
    bss_start = segments[1]["address"] + segments[1]["size"]
    sections.append((name_offsets[".bss"], 8, 3, bss_start, 0, 0x3FCE0000-bss_start, 0, 0, 4, 0))
    strings_offset = len(output)
    output.extend(strings)
    sections.append((name_offsets[".shstrtab"], 3, 0, 0, strings_offset, len(strings), 0, 0, 1, 0))
    output.extend(b"\0" * (-len(output) % 4))
    section_offset = len(output)
    for section in sections:
        output.extend(struct.pack("<10I", *section))
    ident = b"\x7fELF\x01\x01\x01" + bytes(9)
    output[:52] = struct.pack("<16sHHIIIIIHHHHHH", ident, 2, 243, 1,
                             report["application"]["entry_point"], 52, section_offset, 1,
                             52, 32, len(headers), 40, len(sections), len(sections)-1)
    for index, header in enumerate(headers):
        output[52+32*index:84+32*index] = struct.pack("<8I", *header)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump", type=Path, default=Path(__file__).resolve().parents[1] / "full-flash.bin")
    parser.add_argument("--output", type=Path, default=Path(".build/small-tv-reverse"))
    parser.add_argument("--objdump", type=Path, help="Optional RISC-V GNU objdump executable")
    args = parser.parse_args()
    data = args.dump.read_bytes()
    report = parse_dump(data)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "image-map.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (args.output / "factory-analysis.elf").write_bytes(make_elf(data, report))
    display_lines = []
    for segment in report["segments"]:
        path = args.output / f"segment-{segment['index']}-{segment['address']:08x}.bin"
        path.write_bytes(data[segment["flash_offset"]:segment["flash_offset"]+segment["size"]])
        if args.objdump and segment["index"] in (2, 3, 4):
            result = subprocess.run([str(args.objdump.resolve()), "-D", "-b", "binary", "-m", "riscv:rv32",
                                     "--adjust-vma="+hex(segment["address"]), str(path)],
                                    check=True, capture_output=True, text=True)
            (args.output / f"segment-{segment['index']}.disasm.txt").write_text(result.stdout, encoding="utf-8")
            for line in result.stdout.splitlines():
                match = re.match(r"([0-9a-f]+):", line)
                if match and any(start <= int(match[1], 16) < end for start, end in DISPLAY_RANGES):
                    display_lines.append(line)
    if display_lines:
        (args.output / "display-disassembly.txt").write_text(
            "# RISC-V GNU objdump excerpts from the verified Small_TV dump\n"
            "# Runtime addresses; no firmware writes or execution performed.\n\n" +
            "\n".join(display_lines) + "\n", encoding="utf-8")
    print(json.dumps({"dump_sha256_valid": True, "partition_md5_valid": True,
                      "app_checksum_valid": True, "app_sha256_valid": True,
                      "segments": len(report["segments"]), "output": str(args.output)}))


if __name__ == "__main__":
    main()
