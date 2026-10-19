"""Cross-build the pinned decoder and measure retained RV32 code, not firmware fit."""
import argparse
import json
from pathlib import Path
import re
import struct
import subprocess
import tarfile

from build import HERE, PIN, run, sha


def capture(command, output):
    """Preserve exact tool output for the report and independent inspection."""
    result = subprocess.check_output([str(arg) for arg in command])
    output.write_bytes(result)
    return result.decode("utf-8", errors="replace")


def elf_sections(path):
    """Read ELF32 section flags directly so debug/relocations are not flash bytes."""
    data = path.read_bytes()
    header = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    ident, kind, machine = header[:3]
    assert ident[:6] == b"\x7fELF\x01\x01" and kind == 1 and machine == 243
    assert header[7] & 6 == 0, "Expected soft-float ABI"
    section_offset, entry_size, count, names_index = header[6], header[11], header[12], header[13]
    assert entry_size == 40 and 0 < names_index < count
    headers = [struct.unpack_from("<10I", data, section_offset + i * entry_size) for i in range(count)]
    names_header = headers[names_index]
    names = data[names_header[4]:names_header[4] + names_header[5]]
    sections = []
    for section in headers[1:]:
        name_end = names.index(0, section[0])
        sections.append(dict(name=names[section[0]:name_end].decode(), type=section[1],
                             flags=section[2], bytes=section[5]))
    allocated = [section for section in sections if section["flags"] & 2]
    return dict(elf_class=32, machine=machine, elf_flags=header[7], allocated_sections=allocated,
                code_bytes=sum(s["bytes"] for s in allocated if s["flags"] & 4),
                readonly_bytes=sum(s["bytes"] for s in allocated if not s["flags"] & 5),
                initialized_writable_bytes=sum(s["bytes"] for s in allocated if s["flags"] & 1 and s["type"] != 8),
                zero_initialized_bytes=sum(s["bytes"] for s in allocated if s["type"] == 8))


def main():
    """Compile a fresh source export and retain only decode roots with section GC."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--toolchain-bin", type=Path, required=True)
    parser.add_argument("--cmake", default="cmake")
    parser.add_argument("--ninja", default="ninja")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    inputs = {name: sha(HERE / name) for name in
              ("rv32_footprint.py", "footprint.c", "build.py", "libjpeg-turbo-3.2.0-bounded.patch", "UPSTREAM.json")}
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=args.source, text=True).strip()
    if actual != PIN:
        raise ValueError(f"Expected upstream {PIN}, got {actual}")
    archive = output / "upstream.tar"
    run(["git", "archive", "--format=tar", f"--output={archive}", PIN], args.source)
    upstream = json.loads((HERE / "UPSTREAM.json").read_text())
    assert sha(archive) == upstream["source_archive_sha256"]
    source = output / "source"
    source.mkdir()
    with tarfile.open(archive) as stream:
        stream.extractall(source, filter="data")
    patch = HERE / "libjpeg-turbo-3.2.0-bounded.patch"
    assert sha(patch) == upstream["patch_sha256"]
    run(["git", "apply", "--check", patch], source)
    run(["git", "apply", patch], source)
    for name in ("jdmaster.c", "jdcoefct.c"):
        assert "Small TV modifications" in (source / "src" / name).read_text()
    binaries = args.toolchain_bin.resolve()
    suffix = ".exe" if (binaries / "riscv32-esp-elf-gcc.exe").exists() else ""

    def tool(name):
        """Use the exact selected compiler's sibling binutils, avoiding PATH mixes."""
        return binaries / ("riscv32-esp-elf-" + name + suffix)

    specs = binaries.parent / "riscv32-esp-elf" / "lib" / "picolibc.specs"
    if not specs.exists():
        raise FileNotFoundError(specs)
    flags = ["-march=rv32imc_zicsr_zifencei", "-mabi=ilp32", "-mtune=esp-base", "-Os",
             "-ffunction-sections", "-fdata-sections", "-fstack-usage", "-fno-jump-tables",
             "-fno-tree-switch-conversion", "-D__PICOLIBC_ERRNO_FUNCTION=__errno", f"-specs={specs.as_posix()}"]
    toolchain = output / "rv32-toolchain.cmake"
    toolchain.write_text("\n".join([
        "set(CMAKE_SYSTEM_NAME Generic)", "set(CMAKE_SYSTEM_PROCESSOR riscv32)",
        "set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)",
        f'set(CMAKE_C_COMPILER "{tool("gcc").as_posix()}")',
        f'set(CMAKE_AR "{tool("ar").as_posix()}")',
        f'set(CMAKE_RANLIB "{tool("ranlib").as_posix()}")',
        f'set(CMAKE_C_FLAGS_INIT "{" ".join(flags)}")',
        'set(CMAKE_C_FLAGS_RELEASE "-Os -DNDEBUG")', ""]), encoding="utf-8", newline="\n")
    library_build = output / "library"
    cmake_flags = [f"-DCMAKE_TOOLCHAIN_FILE={toolchain}", "-DCMAKE_BUILD_TYPE=Release",
                   "-DENABLE_SHARED=OFF", "-DENABLE_STATIC=ON", "-DWITH_SIMD=OFF",
                   "-DWITH_TURBOJPEG=OFF", "-DWITH_TOOLS=OFF", "-DWITH_TESTS=OFF"]
    run([args.cmake, "-S", source, "-B", library_build, "-G", "Ninja",
         f"-DCMAKE_MAKE_PROGRAM={args.ninja}", *cmake_flags])
    run([args.cmake, "--build", library_build, "--target", "jpeg-static", "--parallel", "2"])
    library = library_build / "libjpeg.a"
    entry_object = output / "footprint.o"
    run([tool("gcc"), *flags, "-DJPEG_STATIC", "-I" + str(source / "src"),
         "-I" + str(library_build), "-c", HERE / "footprint.c", "-o", entry_object])
    linked = output / "decoder-retained.o"
    # Relocatable link intentionally retains undefined libc/libgcc symbols.  It
    # cannot be booted and does not hide those dependencies behind fake stubs.
    link_flags = ["-r", "--gc-sections", "-e", "jpeg_footprint_entry", "-Map=" + str(output / "decoder.map")]
    run([tool("ld"), *link_flags, entry_object, library, "-o", linked])
    symbols = capture([tool("nm"), "--defined-only", linked], output / "symbols.txt")
    unresolved = capture([tool("nm"), "-u", linked], output / "unresolved.txt")
    capture([tool("readelf"), "-h", "-A", linked], output / "elf-architecture.txt")
    capture([tool("size"), "-A", linked], output / "sections.txt")
    binutils_summary = capture([tool("size"), linked], output / "size-summary.txt")
    version = capture([tool("gcc"), "--version"], output / "compiler.txt")
    required = ("jpeg_read_header", "jpeg_start_decompress", "jpeg_read_scanlines",
                "jpeg12_read_scanlines", "jpeg16_read_scanlines", "jinit_arith_decoder",
                "jinit_phuff_decoder", "jinit_lhuff_decoder")
    symbol_names = {line.split()[-1] for line in symbols.splitlines() if line.split()}
    assert all(name in symbol_names for name in required), set(required) - symbol_names
    assert "jpeg_CreateCompress" not in symbol_names, "Encoder unexpectedly retained"
    # Static helper names repeat across translation units and sample precisions.
    # Match the input object AND function in the non-discarded linker map, rather
    # than treating every same-named .su function as retained code.
    memory_map = (output / "decoder.map").read_text().split("Linker script and memory map", 1)[1]
    retained_pairs = {(member, function) for function, member in re.findall(
        r"^ \.text\.(\S+)\s+0x[0-9a-fA-F]+\s+0x[0-9a-fA-F]+\s+[^\n]*libjpeg\.a\(([^)]+)\)",
        memory_map, re.MULTILINE)}
    assert retained_pairs, "Missing non-discarded input sections in linker map"
    stack = []
    for path in list(library_build.rglob("*.su")) + list(output.glob("*.su")):
        for line in path.read_text().splitlines():
            match = re.match(r"(.+):(\d+):(\d+):(.+)\t(\d+)\t(.+)", line)
            member = path.name.removesuffix(".su") + ".obj"
            retained = match and ((member, match[4]) in retained_pairs or
                                  (path.name == "footprint.su" and match[4] == "jpeg_footprint_entry"))
            if retained:
                stack.append(dict(source=match[1], object=member, line=int(match[2]), function=match[4],
                                  bytes=int(match[5]), kind=match[6]))
    assert stack, "Missing compiler stack-usage diagnostics"
    sizes = elf_sections(linked)
    summary_fields = binutils_summary.splitlines()[1].split()
    assert int(summary_fields[0]) == sizes["code_bytes"] + sizes["readonly_bytes"]
    assert int(summary_fields[1]) == sizes["initialized_writable_bytes"]
    assert int(summary_fields[2]) == sizes["zero_initialized_bytes"]
    if inputs != {name: sha(HERE / name) for name in inputs}:
        raise ValueError("Footprint inputs changed during compilation")
    record = dict(schema_version=1, status="rv32_cross_compile_passed", all_functionality_verified=False,
                  upstream_commit=PIN, source_archive_sha256=sha(archive), patch_sha256=sha(patch),
                  source_hashes=inputs, compiler=version.strip(), compiler_sha256=sha(tool("gcc")),
                  specs_sha256=sha(specs), c_flags=flags, cmake_flags=cmake_flags, link_flags=link_flags,
                  library_sha256=sha(library), retained_object_sha256=sha(linked),
                  roots_verified=list(required), sizes=sizes,
                  largest_retained_function_frames=sorted(stack, key=lambda row: row["bytes"], reverse=True)[:20],
                  unresolved_symbols=unresolved.splitlines(),
                  scope="Link-only RV32IMC soft-float decoder measurement. Includes default JPEG errors and memory manager. Excludes final app/link relaxation, libc/libgcc, flash storage adapter, heap, complete call-chain/SDK stack and all runtime acceptance.")
    (output / "report.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Retained RV32 decoder:", sizes["code_bytes"], "code bytes,", sizes["readonly_bytes"],
          "read-only bytes; runtime, total stack and final firmware fit remain unverified.")


if __name__ == "__main__":
    main()
