"""Compare production RGB565 conversion with independent pixels and factory RV32 code."""
import argparse
from array import array
import ctypes as C
import hashlib
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent


def sha(path):
    """Bind the source, library, executable instructions and fixtures to real bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(rgb):
    """Define RGB565 as three truncated fields independently of the C shifts."""
    r, g, b = rgb
    return (r // 8) * 2048 + (g // 4) * 32 + b // 8


def expected(samples, precision, format):
    """Use full-range floating-point rounding as an independent integer-code oracle.

    The source maximum is odd, so these divisions cannot land on an exact half;
    Python's tie-to-even rule and the C half-up rule therefore agree here.
    """
    maximum = 2 ** precision - 1
    channels = (1, 3, 4, 4)[format]
    result = array("H")
    for start in range(0, len(samples), channels):
        values = samples[start:start + channels]
        if format == 0:
            values = values * 3
        elif format in (2, 3):
            if format == 2:
                values = [maximum - value for value in values]
            values = [round(value * values[3] / maximum) for value in values[:3]]
        result.append(packed([round(value * 255 / maximum) for value in values]))
    return result


def sample_bytes(samples, precision):
    """Match the documented native-endian row ABI without depending on alignment."""
    return bytes(samples) if precision <= 8 else array("H", samples).tobytes()


def main():
    """Check exact factory helpers, every gray sample and real decoded JPEG rows."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--dependency-root", type=Path, required=True)
    parser.add_argument("--python-modules", type=Path, action="append", default=[])
    parser.add_argument("--jpeg-build", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for path in args.python_modules:
        sys.path.insert(0, str(path.resolve()))
    from PIL import Image, features
    import PIL
    from machine_oracle import Machine, SCRATCH, UNICORN_VERSION
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    build = json.loads((args.build / "build.json").read_text())
    assert build["status"] == "host_and_rv32_build_passed"
    for name, digest in build["source_hashes"].items():
        assert sha(PROJECT / name) == digest, name
    assert sha(Path(build["host_library"])) == build["host_sha256"]
    assert sha(Path(build["rv32_elf"])) == build["rv32_sha256"]
    runner_hash = sha(Path(__file__))
    lib = C.CDLL(build["host_library"])
    lib.color_test_row.argtypes = [C.c_void_p, C.c_size_t, C.c_size_t, C.c_uint,
                                  C.c_int, C.c_void_p, C.c_size_t]
    lib.color_test_row.restype = C.c_bool
    lib.color_test_pack.argtypes = [C.c_uint32]
    lib.color_test_pack.restype = C.c_uint16
    lib.color_test_expand.argtypes = [C.c_uint16]
    lib.color_test_expand.restype = C.c_uint32
    started = time.perf_counter()

    def convert(raw, pixels, precision, format, unaligned=False):
        """Surround output with sentinels and exercise optional unaligned input."""
        source = C.create_string_buffer((b"!" if unaligned else b"") + raw)
        destination = (C.c_uint16 * (pixels + 2))()
        destination[0], destination[-1] = 0xa55a, 0x5aa5
        assert lib.color_test_row(C.byref(source, 1 if unaligned else 0), len(raw), pixels,
                                  precision, format, C.byref(destination, 2), pixels)
        assert (destination[0], destination[-1]) == (0xa55a, 0x5aa5)
        return array("H", destination[1:-1])

    machine = Machine("factory", dependency_root=args.dependency_root)
    manifest = json.loads((PROJECT / "reference/assembly/manifest.json").read_text())
    code_hashes = {}
    for record in manifest["functions"]:
        if int(record["start"], 16) in (0x42008a34, 0x42008a6a, 0x42008a96):
            start, stop = (int(record[key], 16) for key in ("start", "stop"))
            code = bytes(machine.cpu.mem_read(start, stop - start))
            assert hashlib.sha256(code).hexdigest() == record["code_sha256"]
            code_hashes[record["start"]] = record["code_sha256"]
    assert len(code_hashes) == 3
    # Execute the literal factory wrapper and its unpack helper for every RGB565.
    for value in range(65536):
        rgb = machine.call(0x42008a6a, value)
        assert lib.color_test_expand(value) == rgb
        assert lib.color_test_pack(rgb) == value
    random_values = random.Random(0x42008a96)
    vectors = {(value, 0, 0) for value in range(256)}
    vectors |= {(0, value, 0) for value in range(256)}
    vectors |= {(0, 0, value) for value in range(256)}
    vectors |= set(itertools.product((0, 1, 3, 7, 8, 127, 248, 255), repeat=3))
    vectors |= {tuple(random_values.randrange(256) for _ in range(3)) for _ in range(2048)}
    for rgb in sorted(vectors):
        reference = machine.call(0x42008a96, *rgb)
        assert lib.color_test_pack((rgb[0] << 16) | (rgb[1] << 8) | rgb[2]) == reference == packed(rgb)
    assert not machine.executed_adapters, machine.executed_adapters
    print("Literal factory: 65536 expansions and", len(vectors), "pack vectors passed", flush=True)
    # Load the actual standalone RV32 converter alongside the unchanged helpers.
    machine.load(Path(build["rv32_elf"]))
    row_cases, rv32_cases, sample_count = [], [], 0

    def check(name, samples, precision, format, rv32=True):
        """Check a whole host row, then real RV32 instructions on bounded slices."""
        nonlocal sample_count
        raw = sample_bytes(samples, precision)
        channels = (1, 3, 4, 4)[format]
        pixels = len(samples) // channels
        reference = expected(samples, precision, format)
        assert convert(raw, pixels, precision, format) == reference, name
        assert convert(raw, pixels, precision, format, True) == reference, (name, "unaligned")
        digest = hashlib.sha256(reference.tobytes()).hexdigest()
        row_cases.append(dict(name=name, pixels=pixels, precision=precision, format=format,
                              sample_sha256=hashlib.sha256(raw).hexdigest(), rgb565_sha256=digest))
        sample_count += len(samples)
        if rv32:
            count = min(pixels, 240)
            for offset in sorted({0, max(0, pixels // 2 - count // 2), pixels - count}):
                part = raw[offset * channels * (2 if precision > 8 else 1):
                           (offset + count) * channels * (2 if precision > 8 else 1)]
                source_address, target_address = SCRATCH + 0x10001, SCRATCH + 0x20002
                machine.cpu.mem_write(source_address, part)
                machine.cpu.mem_write(target_address - 2, b"\x5a\xa5" + b"\xcc" * (count * 2) + b"\xa5\x5a")
                result = machine.call(machine.symbols['color_convert_row_rgb565'], source_address,
                                      len(part), count, precision, format, target_address, count)
                assert result == 1, (name, offset)
                actual = bytes(machine.cpu.mem_read(target_address, count * 2))
                assert actual == reference[offset:offset + count].tobytes(), (name, offset, "RV32 pixels")
                assert bytes(machine.cpu.mem_read(target_address - 2, 2)) == b"\x5a\xa5"
                assert bytes(machine.cpu.mem_read(target_address + count * 2, 2)) == b"\xa5\x5a"
                rv32_cases.append(dict(name=name, offset=offset, pixels=count, rgb565_sha256=hashlib.sha256(actual).hexdigest()))

    for bits in range(2, 17):
        maximum = 2 ** bits - 1
        check(f"gray-all-{bits}", list(range(maximum + 1)), bits, 0)
        values = sorted({0, 1, maximum // 2, maximum // 2 + 1, maximum - 1, maximum})
        rgb = [component for sample in itertools.product(values, repeat=3) for component in sample]
        check(f"rgb-boundaries-{bits}", rgb, bits, 1)
        cmyk = [component for sample in itertools.product(values, repeat=4) for component in sample]
        for format in (2, 3):
            check(f"cmyk-boundaries-{bits}-{format}", cmyk, bits, format)
    cmyk = [component for c in range(256) for k in range(256)
            for component in (c, 255 - c, (c + k) % 256, k)]
    check("cmyk-eight-bit-all-channel-black-pairs", cmyk, 8, 2)
    from PIL import Image
    pillow = Image.frombytes("CMYK", (256, 256), bytes(cmyk)).convert("RGB")
    assert convert(bytes(cmyk), 65536, 8, 2) == array("H", map(packed, pillow.getdata()))
    print(len(row_cases), "sample rows and", len(rv32_cases), "actual RV32 rows passed", flush=True)

    invalid = []
    source, destination = C.create_string_buffer(bytes(range(32))), (C.c_uint16 * 20)(*([0xa55a] * 20))
    maximum_size = C.c_size_t(-1).value
    bad_arguments = [
        (None, 3, 1, 8, 1, destination, 1),
        (source, 3, 1, 8, 1, None, 1),
        (source, 3, 0, 8, 1, destination, 1),
        (source, 2, 1, 8, 1, destination, 1),
        (source, 3, 1, 8, 1, destination, 0),
        (source, 3, 1, 8, -1, destination, 1),
        (source, 3, 1, 8, 4, destination, 1),
        (source, 3, 1, 1, 1, destination, 1),
        (source, 6, 1, 17, 1, destination, 1),
        (source, maximum_size, maximum_size, 16, 3, destination, maximum_size),
        (source, maximum_size, maximum_size // 2 + 1, 8, 0, destination, maximum_size),
        (source, 6, 2, 8, 1, source, 2),
        (source, 6, 2, 8, 1, C.byref(source, 4), 2)]
    for index, arguments in enumerate(bad_arguments):
        before = bytes(destination), bytes(source)
        assert not lib.color_test_row(*arguments), index
        assert (bytes(destination), bytes(source)) == before, index
        invalid.append(f"arguments-{index}")
    for bits in range(2, 16):
        if bits == 8:
            continue
        for format, channels in enumerate((1, 3, 4, 4)):
            # The last sample is invalid: an early output row must remain untouched.
            values = [0] * (channels * 2 - 1) + [2 ** bits]
            raw = sample_bytes(values, bits)
            data = C.create_string_buffer(raw)
            before = bytes(destination)
            assert not lib.color_test_row(data, len(raw), 2, bits, format, destination, 2)
            assert bytes(destination) == before
            invalid.append(f"sample-range-{bits}-{format}")
    print(len(invalid), "invalid rows rejected without output writes", flush=True)

    # uintptr_t/size_t are 32-bit on the device.  Host checks alone cannot prove
    # overflow rejection under that ABI, so execute these failure paths too.
    rv32_invalid = []
    source_address, target_address = SCRATCH + 0x11001, SCRATCH + 0x21002
    source_bytes = bytes(range(32))
    bad_rv32_arguments = [
        (0, 3, 1, 8, 1, target_address, 1),
        (source_address, 3, 1, 8, 1, 0, 1),
        (source_address, 3, 0, 8, 1, target_address, 1),
        (source_address, 2, 1, 8, 1, target_address, 1),
        (source_address, 3, 1, 8, 1, target_address, 0),
        (source_address, 3, 1, 8, -1, target_address, 1),
        (source_address, 3, 1, 8, 4, target_address, 1),
        (source_address, 3, 1, 0, 1, target_address, 1),
        (source_address, 3, 1, 1, 1, target_address, 1),
        (source_address, 6, 1, 17, 1, target_address, 1),
        (source_address, 0xffffffff, 0xffffffff, 16, 3, target_address, 0xffffffff),
        (source_address, 0xffffffff, 0x80000000, 8, 0, target_address, 0xffffffff),
        (0xfffffffe, 3, 1, 8, 1, target_address, 1),
        (source_address, 3, 1, 8, 1, 0xffffffff, 1),
        (source_address, 6, 2, 8, 1, source_address, 2),
        (source_address, 6, 2, 8, 1, source_address + 4, 2)]
    for index, arguments in enumerate(bad_rv32_arguments):
        machine.cpu.mem_write(source_address, source_bytes)
        machine.cpu.mem_write(target_address - 2, b"\xa5" * 44)
        assert machine.call(machine.symbols['color_convert_row_rgb565'], *arguments) == 0, index
        assert bytes(machine.cpu.mem_read(source_address, 32)) == source_bytes
        assert bytes(machine.cpu.mem_read(target_address - 2, 44)) == b"\xa5" * 44
        rv32_invalid.append(f"arguments-{index}")
    for bits in range(2, 16):
        if bits == 8:
            continue
        for format, channels in enumerate((1, 3, 4, 4)):
            raw = sample_bytes([0] * (channels * 2 - 1) + [2 ** bits], bits)
            machine.cpu.mem_write(source_address, raw)
            machine.cpu.mem_write(target_address - 2, b"\xa5" * 8)
            result = machine.call(machine.symbols['color_convert_row_rgb565'], source_address,
                                  len(raw), 2, bits, format, target_address, 2)
            assert result == 0, (bits, format)
            assert bytes(machine.cpu.mem_read(target_address - 2, 8)) == b"\xa5" * 8
            rv32_invalid.append(f"sample-range-{bits}-{format}")
    print(len(rv32_invalid), "invalid RV32 rows rejected, including 32-bit pointer/size wrap", flush=True)

    jpeg_build = json.loads((args.jpeg_build / "build.json").read_text())
    jpeg_exe = Path(jpeg_build["executable"])
    assert sha(jpeg_exe) == jpeg_build["executable_sha256"]
    images = []
    for folder in args.fixtures:
        for image in sorted(folder.glob("*.jpg")):
            if image.name.startswith("invalid-"):
                continue
            target = output / "decoded.raw"
            result = subprocess.run([str(jpeg_exe), "decode", str(image), str(target), "65536", "1"],
                                    capture_output=True, timeout=30)
            assert result.returncode == 0, (image.name, result.stderr)
            decoded = json.loads(result.stdout)
            raw = target.read_bytes()
            bits, channels = decoded["precision"], decoded["channels"]
            if channels == 4:
                # Synthetic fixtures here use a real Adobe APP14 marker; YCCK has
                # already been converted to CMYK by the library, exactly once.
                assert b"Adobe" in image.read_bytes()
                format = 3
            else:
                format = 0 if channels == 1 else 1
            samples = list(raw) if bits <= 8 else list(array("H", raw))
            reference = expected(samples, bits, format)
            assert convert(raw, decoded["width"] * decoded["height"], bits, format) == reference, image.name
            independent = None
            if bits == 8:
                with Image.open(image) as opened:
                    pillow = opened.convert("RGB")
                    independent = array("H", map(packed, pillow.getdata()))
                assert reference == independent, (image.name, "Pillow RGB565")
            images.append(dict(name=image.name, fixture_sha256=sha(image), width=decoded["width"],
                               height=decoded["height"], precision=bits, format=format,
                               rgb565_sha256=hashlib.sha256(reference.tobytes()).hexdigest(),
                               independent_pillow=independent is not None))
    assert images and any(v["independent_pillow"] for v in images)
    assert not machine.executed_adapters
    assert runner_hash == sha(Path(__file__))
    report = dict(status="color_conversion_passed", all_functionality_verified=False, build=build,
                  runner_sha256=runner_hash, machine_oracle_sha256=sha(HERE / "machine_oracle.py"),
                  factory_elf_sha256=machine.source_sha, factory_code_hashes=code_hashes,
                  factory_expand_cases=65536, factory_pack_cases=len(vectors), row_cases=row_cases,
                  samples_checked=sample_count, rv32_cases=rv32_cases, invalid_cases=invalid,
                  rv32_invalid_cases=rv32_invalid,
                  jpeg_images=images, jpeg_build=jpeg_build, pillow_version=PIL.__version__,
                  pillow_libjpeg_turbo=features.version("libjpeg_turbo"), unicorn_version=UNICORN_VERSION,
                  host_seconds=time.perf_counter() - started,
                  scope="Pure color conversion and literal RV32 factory helpers, not new codec integration, ICC color management, LCD transport or production acceptance.")
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Color conversion passed:", len(images), "JPEGs; display integration remains separate.", flush=True)


if __name__ == "__main__":
    main()
