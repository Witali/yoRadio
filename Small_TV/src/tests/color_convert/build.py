"""Build the production color module for host tests and standalone RV32 execution."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
INPUTS = (HERE / "build.py", HERE / "CMakeLists.txt", HERE / "bridge.c",
          PROJECT / "app/include/color_convert.h", PROJECT / "app/media/color_convert.c")


def sha(path):
    """Freeze both source bytes and compiled products, not timestamps."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Cross-compile the exact same allocation-free module with the C2 compiler."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--toolchain-bin", type=Path, required=True)
    parser.add_argument("--cmake", default="cmake")
    parser.add_argument("--ninja", default="ninja")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    inputs = {path.relative_to(PROJECT).as_posix(): sha(path) for path in INPUTS}

    def run(command, name):
        """Keep compiler/linker diagnostics and reject unresolved symbols normally."""
        result = subprocess.run([str(arg) for arg in command], capture_output=True)
        (output / name).write_bytes(result.stdout + result.stderr)
        result.check_returncode()
        return result.stdout.decode(errors="replace")

    host = output / "host"
    run([args.cmake, "-S", HERE, "-B", host, "-G", "Ninja", "-DCMAKE_BUILD_TYPE=Release",
         "-DCMAKE_TRY_COMPILE_CONFIGURATION=Release", f"-DCMAKE_MAKE_PROGRAM={args.ninja}"], "host-configure.log")
    run([args.cmake, "--build", host], "host-build.log")
    library = host / "color_contract.dll"
    if not library.exists():
        library = host / "libcolor_contract.so"
    binaries = args.toolchain_bin.resolve()
    suffix = ".exe" if (binaries / "riscv32-esp-elf-gcc.exe").exists() else ""

    def tool(name):
        """Keep compiler, linker and size tools from the same selected SDK."""
        return binaries / ("riscv32-esp-elf-" + name + suffix)

    specs = binaries.parent / "riscv32-esp-elf/lib/picolibc.specs"
    flags = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-Os", "-march=rv32imc_zicsr_zifencei",
             "-mabi=ilp32", "-mtune=esp-base", "-ffunction-sections", "-fdata-sections", "-fstack-usage",
             f"-specs={specs.as_posix()}"]
    obj, elf = output / "color.o", output / "color.elf"
    run([tool("gcc"), *flags, "-I" + str(PROJECT / "app/include"), "-c",
         PROJECT / "app/media/color_convert.c", "-o", obj], "rv32-compile.log")
    # No libc stubs: all required symbols must resolve in the real object.
    run([tool("ld"), "--no-undefined", "--gc-sections", "-e", "color_convert_row_rgb565",
         "-Ttext=0x42018000", obj, "-o", elf], "rv32-link.log")
    sizes = run([tool("size"), "-A", elf], "rv32-sections.txt")
    run([tool("nm"), "--print-size", elf], "rv32-symbols.txt")
    run([tool("gcc"), "--version"], "rv32-compiler.txt")
    stack = (output / "color.su").read_text()
    for line in stack.splitlines():
        assert int(line.split("\t")[1]) <= 256, line
    assert inputs == {path.relative_to(PROJECT).as_posix(): sha(path) for path in INPUTS}
    record = dict(status="host_and_rv32_build_passed", source_hashes=inputs,
                  host_library=str(library), host_sha256=sha(library),
                  rv32_elf=str(elf), rv32_sha256=sha(elf), rv32_flags=flags,
                  rv32_sections=sizes, stack_usage=stack,
                  scope="Standalone converter only, not a production firmware or total stack proof.")
    (output / "build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("Host and RV32 color module built; no unresolved-symbol stubs.")


if __name__ == "__main__":
    main()
