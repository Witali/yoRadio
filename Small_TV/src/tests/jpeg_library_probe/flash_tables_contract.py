"""Compare every real upstream 12-bit table entry and non-flat lossy image bytes."""
import argparse
import json
from pathlib import Path

from qualify import command, decode, sha


def main():
    """Verify the flash-table change without using generated formulas as the oracle."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-build", type=Path, required=True)
    parser.add_argument("--candidate-build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    builds = [json.loads((path / "build.json").read_text())
              for path in (args.reference_build, args.candidate_build)]
    assert builds[0]["variant"] == "upstream" and not builds[0].get("flash_tables")
    assert builds[1]["variant"] == "adapted" and builds[1]["flash_tables"]
    reference, candidate = [Path(row["executable"]) for row in builds]
    for record, exe in zip(builds, (reference, candidate)):
        assert sha(exe.read_bytes()) == record["executable_sha256"]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures = output / "fixtures"
    fixtures.mkdir()
    target_reference, target_candidate = output / "reference.raw", output / "candidate.raw"
    cases, failures = [], []
    modes = ("baseline420", "baseline422", "baseline444", "progressive420", "progressive422",
             "progressive444", "gray-baseline", "gray-progressive", "cmyk-baseline",
             "cmyk-progressive", "ycck-baseline", "ycck-progressive")
    for mode in modes:
        for quality in (83, 100):
            for width, height in ((240, 240), (239, 237)):
                name = f"rich-{mode}-q{quality}-{width}x{height}"
                image = fixtures / (name + ".jpg")
                made = command([reference, "generate", image, f"rich-{mode}-q{quality}", 12,
                                width, height, 1, 0, 0])
                assert made.returncode == 0, made.stderr.decode(errors="replace")
                ref = decode(reference, image, target_reference)
                assert ref["passed"], (name, ref)
                expected = target_reference.read_bytes()
                result = decode(candidate, image, target_candidate, 65536, 1)
                assert result["passed"], (name, result)
                assert target_candidate.read_bytes() == expected, name
                cases.append(dict(name=name, fixture_sha256=sha(image.read_bytes()),
                                  expected_sha256=sha(expected), upstream=ref, candidate=result))
        print("12-bit non-flat pixels:", mode, "passed", flush=True)

    # Inspect the actual tables installed by jpeg_start_decompress.  The host-only
    # helper reads private pointers using the pinned C source's own type layout;
    # it never calls the copied initializer or the Python table generator.
    image = fixtures / "rich-baseline420-q100-240x240.jpg"
    dumps = []
    for name, exe in (("upstream", reference), ("candidate", candidate)):
        range_output, color_output = output / (name + "-range.bin"), output / (name + "-color.bin")
        made = command([exe, "dump-tables", image, range_output, color_output])
        state = json.loads(made.stdout)
        assert made.returncode == 0 and state["passed"] and state["library_pool_final"] == 0, state
        assert range_output.stat().st_size == 45056
        assert color_output.stat().st_size == 65536
        dumps.append(dict(name=name, range_sha256=sha(range_output.read_bytes()),
                          color_sha256=sha(color_output.read_bytes()), state=state))
    assert dumps[0]["range_sha256"] == dumps[1]["range_sha256"]
    assert dumps[0]["color_sha256"] == dumps[1]["color_sha256"]

    for mode in ("baseline420", "progressive444", "cmyk-progressive", "ycck-progressive"):
        original = fixtures / f"rich-{mode}-q83-240x240.jpg"
        data = original.read_bytes()
        for cut in (16, len(data) // 2, len(data) - 2):
            image = fixtures / f"invalid-{mode}-cut{cut}.jpg"
            image.write_bytes(data[:cut])
            ref = decode(reference, image, target_reference)
            result = decode(candidate, image, target_candidate, 65536, 1)
            assert not ref["passed"] and not result["passed"], (image.name, ref, result)
            failures.append(dict(name=image.name, fixture_sha256=sha(image.read_bytes()),
                                 upstream=ref, candidate=result))
    report = dict(schema_version=1, status="passed", all_functionality_verified=False,
                  builds=builds, cases=cases, truncated_cases=failures, table_dumps=dumps,
                  table_entries=dict(range=22528, cr_r=4096, cb_b=4096, cr_g=4096, cb_g=4096),
                  runner_sha256=sha(Path(__file__).read_bytes()),
                  decode_helper_sha256=sha(Path(__file__).with_name("qualify.py").read_bytes()),
                  scope="Host-only exact tables and 12-bit lossy pixels/pool budget. No device fit, NOR backing, firmware integration or complete JPEG conformance claim.")
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Flash tables match all 38912 upstream entries;", len(cases), "lossy images and",
          len(failures), "truncated inputs passed.", flush=True)


if __name__ == "__main__":
    main()
