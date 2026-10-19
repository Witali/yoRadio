"""Check non-flat JPEGs against the pinned library and a separate Pillow decoder."""
import argparse
import json
from pathlib import Path
import shutil

from PIL import Image, ImageFile, features
import PIL

from qualify import decode, sha


def main():
    """Cover actual baseline/restart fixtures and independently encoded progressive color."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-build", type=Path, required=True)
    parser.add_argument("--candidate-build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    builds = [json.loads((path / "build.json").read_text())
              for path in (args.reference_build, args.candidate_build)]
    reference, candidate = [Path(record["executable"]) for record in builds]
    for exe, record in zip((reference, candidate), builds):
        assert sha(exe.read_bytes()) == record["executable_sha256"]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures = output / "fixtures"
    fixtures.mkdir()
    for image in (Path(__file__).resolve().parent.parent / "fixtures" / "jpeg").glob("*.jpg"):
        shutil.copyfile(image, fixtures / image.name)
    # The source contains saturated colors and high-frequency blocks, not a
    # constant DC-only image.  This encoder is distinct from the 3.2.0 probe.
    ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, 1024 * 1024)
    rgb = bytes((x * 17 + y * 31 + c * 47 + (x ^ y) * 9) & 255
                for y in range(240) for x in range(240) for c in range(3))
    original = Image.frombytes("RGB", (240, 240), rgb)
    for mode in ("RGB", "L", "CMYK"):
        for progressive in (False, True):
            for subsampling in ((0, 1, 2) if mode == "RGB" else (0,)):
                name = f"pillow-{mode}-p{int(progressive)}-s{subsampling}.jpg"
                original.convert(mode).save(fixtures / name, quality=83, optimize=True,
                                            progressive=progressive, subsampling=subsampling)
    target_reference, target_candidate = output / "reference.raw", output / "candidate.raw"
    rows = []
    for image in sorted(fixtures.glob("*.jpg")):
        with Image.open(image) as decoded:
            decoded.load()
            expected = decoded.tobytes()
            # Adobe CMYK JPEG samples are inverted; Pillow exposes conventional
            # CMYK bytes, whereas libjpeg's JCS_CMYK exposes the stored polarity.
            if decoded.mode == "CMYK" and decoded.info.get("adobe_transform") == 0:
                expected = bytes(255 - value for value in expected)
            assert decoded.mode in ("RGB", "L", "CMYK"), decoded.mode
        ref = decode(reference, image, target_reference)
        result = decode(candidate, image, target_candidate, 65536, 1)
        assert ref["passed"] and result["passed"], (image.name, ref, result)
        assert target_reference.read_bytes() == expected, (image.name, "Pillow/upstream pixels differ")
        assert target_candidate.read_bytes() == expected, (image.name, "candidate pixels differ")
        rows.append(dict(name=image.name, fixture_sha256=sha(image.read_bytes()),
                         expected_sha256=sha(expected), upstream=ref, candidate=result))
    report = dict(status="passed", all_functionality_verified=False, cases=rows,
                  pillow_version=PIL.__version__, pillow_libjpeg_turbo=features.version("libjpeg_turbo"),
                  encoder_maxblock=ImageFile.MAXBLOCK,
                  runner_sha256=sha(Path(__file__).read_bytes()),
                  decode_helper_sha256=sha(Path(__file__).with_name("qualify.py").read_bytes()),
                  executable_sha256=[sha(exe.read_bytes()) for exe in (reference, candidate)],
                  scope="8-bit non-flat host pixels only; no physical display or firmware integration.")
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Independent Pillow/upstream/candidate pixels passed:", len(rows), "JPEGs.")


if __name__ == "__main__":
    main()
