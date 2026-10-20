"""Exercise JPEG fatal errors and reuse the same object, without claiming device fit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
PIN = "c85e6b905bf237038faa936dab160ebfc5da0344"
OPERATIONS = ("alloc", "open", "read", "write", "seek", "input", "output")


def sha(path):
    """Bind fixture, probe and output evidence to actual bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    """Capture bounded subprocess diagnostics; a crash is never an expected error."""
    return subprocess.run([str(arg) for arg in command], capture_output=True, timeout=30)


def points(count, exhaustive):
    """Cover every small-image call, and boundary/middle calls for full-size images."""
    if exhaustive:
        return range(1, count + 1)
    return sorted({i for center in (1, (count + 1) // 2, count)
                   for i in range(center - 1, center + 2) if 1 <= i <= count})


def main():
    """REQUESTED_CHANGE: prove cleanup and recovery after real partial transfers.

    Allocation failures are swept both once (the pool manager may retry) and
    persistently from the selected call.  Only a failed jpeg_CreateDecompress
    permits recreating the object; all later failures must reuse it after abort.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-build", type=Path, required=True)
    parser.add_argument("--candidate-build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = (args.reference_build, args.candidate_build)
    builds = [json.loads((path / "build.json").read_text(encoding="utf-8")) for path in paths]
    for record in builds:
        assert record["upstream_commit"] == PIN
        assert sha(Path(record["executable"])) == record["executable_sha256"]
        assert all(sha(HERE / name) == digest for name, digest in record["probe_inputs"].items())
    assert builds[0]["variant"] == "upstream" and builds[1]["variant"] == "adapted"
    assert builds[1]["flash_tables"] and builds[1]["compact_pools"]
    reference, candidate = [Path(b["executable"]) for b in builds]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures = output / "fixtures"
    fixtures.mkdir()
    bad, good, expected = [output / name for name in ("fault.raw", "recovery.raw", "expected.raw")]
    cases, negative, transitions = [], [], []
    matrix = [("rich-gray-q83", 8, 31, 17), ("rich-422-q83", 12, 31, 17),
              ("rich-cmyk-progressive-q83", 8, 31, 17),
              ("rich-ycck-progressive-q83", 12, 31, 17),
              ("rich-arith-progressive-q83", 8, 31, 17)]
    matrix += [("lossless-rgb", bits, 31, 17) for bits in (2, 12, 16)]
    matrix += [("rich-baseline-q83", 8, 240, 240),
               ("rich-progressive420-q83", 12, 240, 240),
               ("rich-ycck-progressive-q83", 12, 240, 240),
               ("rich-cmyk-progressive-q83", 8, 240, 240)]
    started = time.perf_counter()

    def exercise(image, expected_sha, kind="none", ordinal=0, persistent=0, recovery=None):
        """One child performs both phases; inspect pixels, pool cap and every handle."""
        bad.unlink(missing_ok=True)
        good.unlink(missing_ok=True)
        command = [candidate, "reuse", image, bad, good, 65536, 1, kind, ordinal, persistent]
        if recovery is not None:
            command.append(recovery)
        result = run(command)
        assert result.returncode == 0, (command, result.returncode, result.stdout, result.stderr)
        record = json.loads(result.stdout)
        first, second = record["first"], record["recovery"]
        assert second["passed"] and second["fault_hits"] == 0, record
        assert second["reused_object"] or kind == "alloc", record
        assert sha(good) == expected_sha, record
        assert record["library_pool_final"] == 0, record
        assert record["stores_opened"] == record["stores_closed"], record
        for phase in (first, second):
            assert phase["library_pool_peak"] <= 65536, record
            assert phase["stores_opened"] == phase["stores_closed"], record
        if kind != "none":
            assert first["fault_hits"] >= 1, record
            if not persistent:
                assert first["fault_hits"] == 1, record
            if first["passed"]:
                assert kind == "alloc" and not persistent, record
                assert sha(bad) == expected_sha, record
            else:
                assert first["error"] == record["expected_error"] != 0, record
        record.update(operation=kind, ordinal=ordinal, persistent=bool(persistent),
                      recovery_sha256=sha(good), first_output_sha256=sha(bad) if bad.exists() else None)
        return record

    for mode, bits, width, height in matrix:
        name = f"{mode}-{bits}-{width}x{height}"
        image = fixtures / (name + ".jpg")
        result = run([reference, "generate", image, mode, bits, width, height, 1, 0, 0])
        assert result.returncode == 0, result.stderr
        result = run([reference, "decode", image, expected, 0, 0])
        assert result.returncode == 0, result.stderr
        expected_sha = sha(expected)
        control = exercise(image, expected_sha)
        assert control["first"]["passed"], control
        row = dict(name=name, fixture_sha256=sha(image), expected_sha256=expected_sha,
                   width=width, height=height, precision=bits, control=control, faults=[])
        for kind in OPERATIONS:
            count = control["first"]["visits"][kind]
            exhaustive = width < 240 or kind in ("alloc", "open")
            for ordinal in points(count, exhaustive):
                for persistent in ((0, 1) if kind == "alloc" else (0,)):
                    record = exercise(image, expected_sha, kind, ordinal, persistent)
                    row["faults"].append(record)
        cases.append(row)
        # A strict parser error also must permit a new header on the same object.
        data = image.read_bytes()
        for cut in (2, len(data) // 2, len(data) - 2):
            damaged = fixtures / f"invalid-{name}-cut{cut}.jpg"
            damaged.write_bytes(data[:cut])
            record = exercise(damaged, expected_sha, recovery=image)
            assert not record["first"]["passed"] and record["first"]["error"] != 0, record
            negative.append(dict(name=damaged.name, fixture_sha256=sha(damaged), result=record))
        print(name, len(row["faults"]), "faults and 3 damaged-input recoveries passed", flush=True)

    # Cross precision, coding and color changes exercise persistent table/source state.
    for before, after in zip(cases, cases[1:] + cases[:1]):
        result = exercise(fixtures / (before["name"] + ".jpg"), after["expected_sha256"],
                          recovery=fixtures / (after["name"] + ".jpg"))
        assert result["first"]["passed"] and result["recovery"]["reused_object"], result
        assert result["first_output_sha256"] == before["expected_sha256"], result
        transitions.append(dict(before=before["name"], after=after["name"], result=result))
    total = sum(len(case["faults"]) for case in cases)
    counts = {kind: sum(f["operation"] == kind for c in cases for f in c["faults"])
              for kind in OPERATIONS}
    assert all(counts.values()), counts
    report = dict(schema_version=1, status="host_fault_reuse_passed", all_functionality_verified=False,
                  builds=builds, runner_sha256=sha(Path(__file__)), fixture_cases=cases,
                  damaged_input_recoveries=negative, format_transitions=transitions,
                  fault_cases=total, faults_by_operation=counts, host_seconds=time.perf_counter() - started,
                  scope="Host library pools and stdio fault/abort/reuse only. All small-image I/O ordinals and all allocation/open ordinals; boundary/middle I/O ordinals for 240x240. No NOR semantics, production adapter, total RAM/stack, HTTP or LCD acceptance.")
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(total, "injected-fault recoveries passed; physical device support remains unproven.", flush=True)


if __name__ == "__main__":
    main()
