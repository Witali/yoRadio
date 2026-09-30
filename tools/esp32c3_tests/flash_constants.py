"""Collect read-only source and ELF evidence for a manual Flash constant audit.

Requires pyelftools (included in the ESP-IDF Python environment). Counts and
attribute hits are an inventory, not proof that an object is immutable or safe
with the cache disabled. The linker map, not an nm letter, decides placement.
No source, build configuration, or device state is changed.
"""

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

from elftools.elf.elffile import ELFFile


SOURCE_SUFFIXES = {".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".ino", ".s", ".inc", ".ld", ".lf"}
ATTRIBUTES = re.compile(r"\b(?:DRAM_ATTR|DRAM_STR|RTC_DATA_ATTR|RTC_RODATA_ATTR|RTC_NOINIT_ATTR|IRAM_ATTR|PROGMEM|ICACHE_RODATA_ATTR)\b")
# Preserve literal tokens while removing comments, including C++ raw strings.
TOKENS = re.compile(r'R"([^ ()\\\t\r\n]{0,16})\(.*?\)\1"|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*.*?\*/', re.S)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path, rows, columns):
    with path.open("w", encoding="utf-8", newline="") as output:
        # Quote trailing spaces in actual string literals instead of trimming
        # evidence or producing misleading whitespace errors in a Git diff.
        writer = csv.DictWriter(output, fieldnames=columns, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def map_inputs(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    text = text.split("Linker script and memory map", 1)[1]
    text = text.split("Cross Reference Table", 1)[0]
    pattern = re.compile(
        r"^ (\.[^\s]+)(?:\s*\n)?[ \t]+(0x[0-9a-f]+)[ \t]+(0x[0-9a-f]+)[ \t]+([^\n]+)",
        re.M,
    )
    rows = []
    for match in pattern.finditer(text):
        name, address, size, owner = match.groups()
        if ".a(" not in owner and not owner.endswith((".obj", ".o")):
            continue
        address, size = int(address, 16), int(size, 16)
        if address:
            # Linker string pooling can reduce an input to zero bytes, or grow
            # one input with strings from other objects. Retain both identities.
            before = re.match(r"\s*\n\s*(0x[0-9a-f]+) \(size before relaxing\)", text[match.end():])
            rows.append(dict(input_section=name, address=address, bytes=size,
                             bytes_before_relaxing=int(before[1], 16) if before else size,
                             owner=owner.strip().replace("\\", "/")))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    build = args.build.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    description = json.loads((build / "project_description.json").read_text())
    elf_path = build / description["app_elf"]
    map_path = elf_path.with_suffix(".map")
    commands_path = build / "compile_commands.json"
    commands = json.loads(commands_path.read_text())
    compiled = {Path(command["file"]).resolve() for command in commands}
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    tracked_sources = {root / name for name in tracked if Path(name).suffix.lower() in SOURCE_SUFFIXES}
    idf = Path(description["idf_path"]).resolve()

    def label(path):
        path = path.resolve()
        for prefix, replacement in ((root, ""), (idf, "<IDF>/"), (idf.parent, "<DEPENDENCIES>/")):
            if path.is_relative_to(prefix):
                return replacement + path.relative_to(prefix).as_posix()
        return path.as_posix()

    def normalize_owner(owner):
        return owner.replace(root.as_posix() + "/", "<REPO>/").replace(idf.as_posix() + "/", "<IDF>/").replace(idf.parent.as_posix() + "/", "<DEPENDENCIES>/")

    inventory = []
    for path in sorted(tracked_sources | compiled, key=label):
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        contents = path.read_text(encoding="utf-8", errors="replace")
        clean = TOKENS.sub(lambda m: "\n" * m[0].count("\n") if m[0].startswith(("//", "/*")) else m[0], contents)
        literal_count = sum(m[0].startswith(('"', 'R"')) for m in TOKENS.finditer(clean))
        attributes = ";".join(f"{number}:{','.join(ATTRIBUTES.findall(line))}" for number, line in enumerate(clean.splitlines(), 1) if ATTRIBUTES.search(line))
        inventory.append(dict(path=label(path), tracked=path in tracked_sources,
                              translation_unit=path in compiled, bytes=path.stat().st_size,
                              lines=len(contents.splitlines()), sha256=digest(path),
                              string_tokens=literal_count, placement_hits=attributes))
    write_csv(args.output / "source-inventory.csv", inventory, list(inventory[0]))

    sections, symbols, strings = [], [], []
    inputs = map_inputs(map_path)
    with elf_path.open("rb") as source:
        elf = ELFFile(source)
        for section in elf.iter_sections():
            if section["sh_flags"] & 2 and section["sh_size"]:
                sections.append(dict(name=section.name, address=section["sh_addr"], bytes=section["sh_size"], type=section["sh_type"]))
        for row in inputs:
            section = next((s for s in sections if s["address"] <= row["address"] < s["address"] + s["bytes"] and row["address"] + row["bytes"] <= s["address"] + s["bytes"]), None)
            row["output_section"] = section["name"] if section else "unmapped"
            row["owner"] = normalize_owner(row["owner"])
        for symbol in elf.get_section_by_name(".symtab").iter_symbols():
            index = symbol["st_shndx"]
            if symbol["st_info"]["type"] != "STT_OBJECT" or not symbol["st_size"] or not isinstance(index, int):
                continue
            section = elf.get_section(index)
            if not section["sh_flags"] & 2:
                continue
            value = symbol["st_value"]
            owner = next((r["owner"] for r in inputs if r["address"] <= value < r["address"] + r["bytes"]), "")
            symbols.append(dict(name=symbol.name, address=f"0x{value:08x}", bytes=symbol["st_size"], section=section.name, owner=owner))
        for section in elf.iter_sections():
            if section.name not in (".dram0.data", ".iram0.data", ".rtc.data"):
                continue
            for match in re.finditer(rb"[\x20-\x7e]{5,}\x00", section.data()):
                value = section["sh_addr"] + match.start()
                owner = next((r for r in inputs if r["address"] <= value < r["address"] + r["bytes"]), {})
                strings.append(dict(address=f"0x{value:08x}", bytes=len(match[0]), section=section.name,
                                    input_section=owner.get("input_section", ""), map_container=owner.get("owner", ""),
                                    text=match[0][:-1].decode("ascii")))
    write_csv(args.output / "elf-objects.csv", sorted(symbols, key=lambda s: (s["section"], s["address"])), list(symbols[0]))
    ram_inputs = [r for r in inputs if r["output_section"].startswith((".dram", ".iram", ".rtc")) and not r["output_section"].endswith("text")]
    write_csv(args.output / "ram-input-sections.csv", ram_inputs, list(inputs[0]))
    if strings:
        write_csv(args.output / "ram-string-runs.csv", strings, list(strings[0]))
    summary = dict(source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
                   project_version=description["project_version"], idf_version=description["git_revision"],
                   build=label(build), elf_sha256=digest(elf_path), map_sha256=digest(map_path),
                   config_sha256=digest(Path(description["config_file"])),
                   compile_commands_sha256=digest(commands_path),
                   tracked_source_files=sum(r["tracked"] for r in inventory),
                   compiled_source_files=sum(r["translation_unit"] for r in inventory),
                   compiled_tracked_files=sum(r["translation_unit"] and r["tracked"] for r in inventory),
                   tracked_groups=dict(Counter(r["path"].split("/")[0] for r in inventory if r["tracked"])),
                   sections=sections,
                   ram_input_payload_bytes=sum(r["bytes"] for r in ram_inputs),
                   ram_string_run_bytes=sum(r["bytes"] for r in strings),
                   limitations=["Source inventory is a lexical scan, not a C/C++ parser or a mutability proof.",
                                "translation_unit means a compiler input, not proof its sections survive linking; headers are not translation units.",
                                "Compiler options, conditional includes and uncompiled branches need manual review.",
                                "ASCII runs can include nonstrings or string suffixes; counts are not safe savings.",
                                "String pooling merges multiple source owners into one map container. See zero-size inputs and bytes_before_relaxing; these are not extra savings.",
                                "Input payload counts exclude padding; aliases in the symbol list must not be added twice.",
                                "Binary-only SDK implementations are audited through the ELF/map, not nonexistent source."])
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("source_commit", "tracked_source_files", "compiled_source_files", "elf_sha256", "ram_string_run_bytes")}, indent=2))


if __name__ == "__main__":
    main()
