"""Compare pinned JPEG builds and measure pool limits without claiming device support."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import subprocess
import time


def sha(data):
    """Identify fixture, output and executable bytes independently of file names."""
    return hashlib.sha256(data).hexdigest()


def command(args):
    """Run one bounded host operation and retain diagnostics on expected failures."""
    return subprocess.run([str(arg) for arg in args], capture_output=True, timeout=30)


def decode(exe, image, target, budget=0, backing=0, smoothing=0, quantize=0):
    """Enforce cleanup and the real pool cap on successful and failed decodes."""
    started = time.perf_counter()
    result = command([exe, "decode", image, target, budget, backing, smoothing, quantize])
    record = json.loads(result.stdout)
    record.update(exit_code=result.returncode, stderr=result.stderr.decode(errors="replace"),
                  host_seconds=time.perf_counter() - started)
    assert result.returncode in (0, 1), record
    assert record["library_pool_final"] == 0, record
    assert record["stores_opened"] == record["stores_closed"], record
    assert not budget or record["library_pool_peak"] <= budget, record
    assert record["passed"] == (result.returncode == 0), record
    record["raw_sha256"] = sha(target.read_bytes())
    return record


def known_samples(width, height, channels, precision, transform=0):
    """Derive exact samples without using JPEG code; point transforms discard LSBs."""
    values = [(((x * 17 + y * 31 + channel * 47) & ((1 << precision) - 1)) >> transform) << transform
              for y in range(height) for x in range(width) for channel in range(channels)]
    return bytes(values) if precision <= 8 else array("H", values).tobytes()


def main():
    """Test image equivalence, all lossless precisions/predictors, and bounded failure.

    FIXED_TEST: optional unbounded modes record pool tradeoffs; smaller reserves
    can add chunk overhead.  Actual bounded decode cases retain their hard cap.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-build", type=Path, required=True)
    parser.add_argument("--candidate-build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    builds = [json.loads((path / "build.json").read_text())
              for path in (args.reference_build, args.candidate_build)]
    reference, candidate = [Path(record["executable"]) for record in builds]
    for record, exe in zip(builds, (reference, candidate)):
        assert sha(exe.read_bytes()) == record["executable_sha256"]
        assert record["upstream_commit"] == "c85e6b905bf237038faa936dab160ebfc5da0344"
    assert builds[0]["variant"] == "upstream" and builds[1]["variant"] == "adapted"
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures = output / "fixtures"
    fixtures.mkdir()
    target_reference, target_candidate = output / "reference.raw", output / "candidate.raw"
    matrix = [("baseline", 8), ("baseline", 12), ("progressive420", 8),
              ("progressive444", 8), ("gray-progressive", 8), ("cmyk-progressive", 8),
              ("ycck-progressive", 8), ("arith", 8), ("arith-progressive", 8),
              ("progressive420", 12)]
    matrix += [(f"lossless-{color}", bits) for color in ("gray", "rgb", "cmyk")
               for bits in (2, 4, 8, 12, 16)]
    resources, lossless, negatives, controls, budget_failures = [], [], [], [], []

    def generate(name, mode, bits, width=240, height=240, predictor=1, transform=0, restart=0):
        """Use only upstream's encoder; both decoders receive exactly those bytes."""
        image = fixtures / (name + ".jpg")
        result = command([reference, "generate", image, mode, bits, width, height,
                          predictor, transform, restart])
        assert result.returncode == 0, result.stderr.decode(errors="replace")
        return image

    for mode, bits in matrix:
        name = f"{mode}-{bits}"
        image = generate(name, mode, bits)
        ref = decode(reference, image, target_reference)
        assert ref["passed"], ref
        expected = target_reference.read_bytes()
        channels = 1 if "gray" in mode else 4 if "cmyk" in mode or "ycck" in mode else 3
        if "lossless" in mode:
            assert expected == known_samples(240, 240, channels, bits)
        row = dict(name=name, fixture_sha256=sha(image.read_bytes()), upstream=ref, candidate={})
        for label, budget, backing in (("unlimited", 0, 0), ("64k-no-backing", 65536, 0),
                                       ("64k-backing", 65536, 1)):
            result = decode(candidate, image, target_candidate, budget, backing)
            if result["passed"]:
                assert target_candidate.read_bytes() == expected, (name, label)
                result["matches_upstream_pixels"] = True
            if label == "unlimited":
                assert result["passed"], result
            if label == "64k-backing" and (bits == 8 or "lossless" in mode or builds[1].get("flash_tables")):
                assert result["passed"], (name, label, result)
            if "lossless" in mode and budget:
                assert result["passed"] and result["stores_opened"] == 0, (name, label, result)
            row["candidate"][label] = result
        resources.append(row)
        print(name, {label: (r["passed"], r["library_pool_peak"], r["backing_capacity"])
                     for label, r in row["candidate"].items()}, flush=True)

    # Exhaust every legal precision and predictor, with zero/middle/max point
    # transforms.  Odd dimensions and deterministic restart intervals cover row
    # boundaries without claiming the full cross product of JPEG syntax.
    for bits in range(2, 17):
        for predictor in range(1, 8):
            for color, channels in (("gray", 1), ("rgb", 3), ("cmyk", 4)):
                for transform in sorted({0, bits // 2, bits - 1}):
                    name = f"lossless-{color}-{bits}-p{predictor}-t{transform}"
                    # Upstream lossless requires an integral number of MCU rows.
                    restart = 62 if (bits + predictor + transform) % 2 else 0
                    image = generate(name, f"lossless-{color}", bits, 31, 17,
                                     predictor, transform, restart)
                    expected = known_samples(31, 17, channels, bits, transform)
                    ref = decode(reference, image, target_reference)
                    result = decode(candidate, image, target_candidate, 65536)
                    assert ref["passed"] and result["passed"], (name, ref, result)
                    assert target_reference.read_bytes() == expected, name
                    assert target_candidate.read_bytes() == expected, name
                    lossless.append(dict(name=name, fixture_sha256=sha(image.read_bytes()),
                                         expected_sha256=sha(expected), restart=restart,
                                         upstream=ref, candidate=result))
        print("lossless precision", bits, "passed", flush=True)

    # Keep optional behavior that still needs range tables/five-row windows.
    for name, smoothing, quantize in (("lossless-gray-8", 0, 1), ("lossless-rgb-12", 0, 1),
                                      ("progressive420-8", 1, 0), ("gray-progressive-8", 1, 0)):
        image = fixtures / (name + ".jpg")
        ref = decode(reference, image, target_reference, smoothing=smoothing, quantize=quantize)
        result = decode(candidate, image, target_candidate, smoothing=smoothing, quantize=quantize)
        assert result["passed"] == ref["passed"], (name, ref, result)
        if result["passed"]:
            assert target_reference.read_bytes() == target_candidate.read_bytes(), name
            if builds[1].get("compact_pools"):
                # These API controls use unlimited full-image buffers and can
                # need more pool headers.  They prove unchanged output/cleanup,
                # not a blanket memory reduction for optional preview modes.
                pass
            elif builds[1].get("flash_tables") and "12" in name:
                assert result["library_pool_peak"] < ref["library_pool_peak"], name
            else:
                assert result["library_pool_peak"] == ref["library_pool_peak"], name
        controls.append(dict(name=name, smoothing=smoothing, quantize=quantize,
                             upstream=ref, candidate=result,
                             pool_delta_bytes=result["library_pool_peak"] - ref["library_pool_peak"],
                             memory_limit_bytes=None))

    for budget in (12000, 24000, 32000, 40000, 48000, 56000):
        for name in ("progressive420-8", "cmyk-progressive-8", "lossless-rgb-16"):
            image = fixtures / (name + ".jpg")
            result = decode(candidate, image, target_candidate, budget, 1)
            if result["passed"]:
                ref = decode(reference, image, target_reference)
                assert ref["passed"] and target_candidate.read_bytes() == target_reference.read_bytes()
            budget_failures.append(dict(name=name, budget=budget, candidate=result))

    for name in ("baseline-8", "progressive420-8", "lossless-rgb-16", "cmyk-progressive-8"):
        data = (fixtures / (name + ".jpg")).read_bytes()
        for cut in (2, 16, len(data) // 2, len(data) - 2):
            image = fixtures / f"invalid-{name}-cut{cut}.jpg"
            image.write_bytes(data[:cut])
            ref = decode(reference, image, target_reference)
            result = decode(candidate, image, target_candidate)
            assert not ref["passed"] and not result["passed"], (name, cut, ref, result)
            negatives.append(dict(name=image.name, fixture_sha256=sha(image.read_bytes()),
                                  upstream=ref, candidate=result))

    report = dict(schema_version=1, status="host_qualification_passed", all_functionality_verified=False,
                  builds=builds, runner_sha256=sha(Path(__file__).read_bytes()),
                  resource_cases=resources, lossless_cases=lossless, negative_cases=negatives,
                  optional_mode_controls=controls, budget_sweep=budget_failures,
                  scope="Host library-pool measurement and byte equivalence only. Excludes output-row/session/stdio/stack/SDK memory, RV32 binary size, NOR storage/wear, HTTP/LCD, and complete JPEG conformance.",
                  missing_device_work=["full firmware link and total heap/stack measurement",
                                       "bounded persistent backing store with NOR semantics",
                                       "format conversion and factory pixel compatibility",
                                       "I/O faults and decoder reuse after failure",
                                       "HTTP/storage/display gates and production regression/soak"])
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Host qualification passed:", len(resources), "resource cases,", len(lossless),
          "lossless cases,", len(negatives), "invalid inputs; device support is unproven.", flush=True)


if __name__ == "__main__":
    main()
