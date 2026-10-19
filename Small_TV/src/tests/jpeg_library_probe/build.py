"""Build an isolated, pinned host JPEG probe without changing the source checkout."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

PIN = "c85e6b905bf237038faa936dab160ebfc5da0344"
HERE = Path(__file__).resolve().parent


def sha(path):
    """Hash bytes used by the build, including the patch and compiler products."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, cwd=None):
    """Keep compiler diagnostics visible and fail on the first failed command."""
    subprocess.run([str(arg) for arg in command], cwd=cwd, check=True)


def main():
    """Export the exact upstream tree, optionally patch it, and build the host tool."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cmake", default="cmake")
    parser.add_argument("--ninja", default="ninja")
    parser.add_argument("--adapted", action="store_true")
    args = parser.parse_args()
    input_names = ("probe.c", "probe_memory.c", "probe_memory.h", "CMakeLists.txt",
                   "libjpeg-turbo-3.2.0-bounded.patch", "build.py")
    build_inputs = {name: sha(HERE / name) for name in input_names}
    source = args.source.resolve()
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if actual != PIN:
        raise ValueError(f"Expected upstream {PIN}, got {actual}")
    # git archive reads committed bytes, never local changes or generated wrappers.
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    archive = output / "upstream.tar"
    run(["git", "archive", "--format=tar", f"--output={archive}", PIN], source)
    exported = output / "source"
    exported.mkdir()
    with tarfile.open(archive) as stream:
        stream.extractall(exported, filter="data")
    patch = HERE / "libjpeg-turbo-3.2.0-bounded.patch"
    if args.adapted:
        run(["git", "apply", "--check", patch], exported)
        run(["git", "apply", patch], exported)
        for name in ("jdmaster.c", "jdcoefct.c"):
            if "Small TV modifications" not in (exported / "src" / name).read_text():
                raise ValueError(f"Patch did not modify {name}")
    library_build = output / "library"
    flags = ["-DCMAKE_BUILD_TYPE=Release", "-DCMAKE_TRY_COMPILE_CONFIGURATION=Release",
             "-DENABLE_SHARED=OFF", "-DENABLE_STATIC=ON",
             "-DWITH_SIMD=OFF", "-DWITH_TURBOJPEG=OFF", "-DWITH_TOOLS=OFF", "-DWITH_TESTS=OFF"]
    run([args.cmake, "-S", exported, "-B", library_build, "-G", "Ninja",
         f"-DCMAKE_MAKE_PROGRAM={args.ninja}", *flags])
    run([args.cmake, "--build", library_build, "--target", "jpeg-static", "--parallel", "2"])
    library = library_build / "jpeg-static.lib"
    if not library.exists():
        library = library_build / "libjpeg.a"
    probe_build = output / "probe"
    run([args.cmake, "-S", HERE, "-B", probe_build, "-G", "Ninja",
         f"-DCMAKE_MAKE_PROGRAM={args.ninja}", "-DCMAKE_BUILD_TYPE=Release",
         "-DCMAKE_TRY_COMPILE_CONFIGURATION=Release",
         f"-DJPEG_SOURCE={exported}", f"-DJPEG_BUILD={library_build}", f"-DJPEG_LIBRARY={library}"])
    run([args.cmake, "--build", probe_build, "--parallel", "2"])
    executable = probe_build / "jpeg_probe.exe"
    if not executable.exists():
        executable = probe_build / "jpeg_probe"
    if build_inputs != {name: sha(HERE / name) for name in input_names}:
        raise ValueError("Probe inputs changed during compilation")
    record = dict(library="libjpeg-turbo", version="3.2.0", upstream_commit=PIN,
                  variant="adapted" if args.adapted else "upstream", cmake_flags=flags,
                  source_archive_sha256=sha(archive), patch_sha256=sha(patch) if args.adapted else None,
                  probe_inputs=build_inputs,
                  executable=str(executable), executable_sha256=sha(executable),
                  library_sha256=sha(library),
                  adapted_sources={name: sha(exported / "src" / name)
                                   for name in ("jdmaster.c", "jdcoefct.c")},
                  scope="Host build only; not ESP32-C2 integration or upstream regression acceptance.")
    (output / "build.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
