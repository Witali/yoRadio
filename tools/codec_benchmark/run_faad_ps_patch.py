#!/usr/bin/env python3
"""Build and measure the supplied PS storage patch against pinned upstream FAAD.

Outputs raw PCM only into the ignored experiment directory. No board access.
"""
from array import array
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tarfile

from run_faad_history_comparison import ROOT, REVISION, ARCHIVE_SHA256, digest, host_path, host_command

PATCH = ROOT / "tools/codec_benchmark/patches/faad2-packed-ps-history-supplied.patch"
PATCH_SHA256 = "44bc82a60793946a9477da17d841abf8444da80a279aa7ae48e4005cb49cdbd1"
PROBE = ROOT / "tools/codec_benchmark/faad_decode_probe.c"


def compare_pcm(base, candidate, frames):
    a, b = array('h'), array('h')
    a.frombytes(base.read_bytes()); b.frombytes(candidate.read_bytes())
    if sys.byteorder != "little":
        a.byteswap(); b.byteswap()
    if len(a) != len(b) or not a:
        raise ValueError("PCM shape differs")
    stats = [dict(hist={}, square=0, signal=0, signed=0) for _ in range(2)]
    offset = 0
    for frame in frames:
        count, channels = frame[1], frame[3]
        if channels not in (1,2) or count % channels or offset + count > len(a):
            raise ValueError("Invalid frame shape")
        for n in range(count):
            x, y = a[offset+n], b[offset+n]
            stat = stats[n % channels]
            delta = y-x; error = abs(delta)
            stat['hist'][error] = stat['hist'].get(error,0)+1
            stat['square'] += error*error; stat['signal'] += x*x; stat['signed'] += delta
        offset += count
    if offset != len(a): raise ValueError("PCM length disagrees with frame trace")
    rows = []
    for ch,stat in enumerate(stats):
        hist, square, signal, signed = (stat[k] for k in ('hist','square','signal','signed'))
        if not hist: continue
        count = sum(hist.values())
        rows.append(dict(channel=ch, samples=count, maximum=max(hist),
                         different=count-hist.get(0, 0), over_two=sum(v for k,v in hist.items() if k>2),
                         over_five=sum(v for k,v in hist.items() if k>5), square_error=square,
                         square_signal=signal, signed_error=signed, rms_lsb=math.sqrt(square/count),
                         histogram={str(k): v for k,v in sorted(hist.items())}))
    return rows


def run(output, archive, recordings):
    output.mkdir(parents=True, exist_ok=True)
    if digest(archive) != ARCHIVE_SHA256:
        raise ValueError("Pinned FAAD archive differs")
    if digest(PATCH) != PATCH_SHA256:
        raise ValueError("Supplied patch differs from the retained input")
    source = output / f"faad2-{REVISION}"
    # Reset only the pinned extracted files. Remove the one patch-added header
    # before reapplying. No recursive deletion and no firmware/vendor mutation.
    if (source / "libfaad/packed_complex.h").exists():
        (source / "libfaad/packed_complex.h").unlink()
    with tarfile.open(archive) as bundle:
        bundle.extractall(output, filter="data")
    command = ["git", "apply", "--recount", "--directory=" + source.relative_to(ROOT).as_posix(), str(PATCH)]
    applied = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    (output / "apply.log").write_text(applied.stdout+applied.stderr, encoding="utf-8")
    pristine = archive.parent / f"faad2-{REVISION}"
    with tarfile.open(archive) as bundle:
        for entry in bundle.getmembers():
            if entry.isfile() and (archive.parent / entry.name).read_bytes() != bundle.extractfile(entry).read():
                raise ValueError("Pristine comparison source was changed")
    commands = {}
    def build(mode):
        src = pristine if mode == "baseline" else source
        cmd = ["gcc", "-O2", "-fno-strict-aliasing", "-ffloat-store", "-DFIXED_POINT=1", "-DAPPLY_DRC",
               "-DHAVE_INTTYPES_H=1", "-DHAVE_MEMCPY=1", "-DHAVE_STRING_H=1", "-DHAVE_STRINGS_H=1",
               "-DHAVE_SYS_STAT_H=1", "-DHAVE_SYS_TYPES_H=1", "-DHAVE_LRINTF=1", '-DPACKAGE_VERSION="comparison"']
        if mode == "packed": cmd += ["-DFAAD_PACKED_PS_HISTORY=1"]
        cmd += ["-I"+host_path(src / "include"), "-I"+host_path(src / "libfaad"),
                "-I"+host_path(ROOT / "idf/esp32c3-oled-native/main")]
        cmd += [host_path(p) for p in sorted((src / "libfaad").glob("*.c"))]
        cmd += [host_path(PROBE), "-lm", "-o", host_path(output / mode)]
        commands[mode] = cmd
        with (output / f"build-{mode}.log").open("w") as log:
            subprocess.run(host_command(cmd), stdout=log, stderr=subprocess.STDOUT, check=True)
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(build, ("baseline", "disabled", "packed")))
    inputs = {p.stem: p for p in sorted((ROOT / "tests/fixtures/aac_stream_format").glob("*.aac"))}
    inputs.update({n: recordings / f"{n}.aac" for n in ("abba64", "groovesalad16", "groovesalad32", "groovesalad64", "groovesalad128")})
    results = []
    for name, path in inputs.items():
        repeat = 2 if path.parent != recordings else 1
        runs = {}
        for mode in ("baseline", "disabled", "packed"):
            prefix = output / f"{name}-{mode}"
            cmd = [host_path(output / mode), host_path(path), host_path(prefix), str(repeat)]
            process = subprocess.run(host_command(cmd), text=True, capture_output=True, check=True)
            (output / f"{name}-{mode}.log").write_text(process.stdout+process.stderr, encoding="utf-8")
            runs[mode] = json.loads(process.stdout)
            runs[mode].update(pcm_sha256=digest(prefix.with_suffix(".pcm")), frames_sha256=digest(prefix.with_suffix(".frames")))
        base = output / f"{name}-baseline"
        shape = base.with_suffix('.frames').read_text()
        for mode in ("disabled", "packed"):
            if (output / f"{name}-{mode}.frames").read_text() != shape:
                raise ValueError("Frame shape/PS activation differs")
        if runs["baseline"]["pcm_sha256"] != runs["disabled"]["pcm_sha256"]:
            raise ValueError("Patch-disabled PCM changed")
        frames = [list(map(int,line.split())) for line in shape.splitlines()]
        if name in ("abba64", "hev2-44100-stereo") and not runs["packed"]["ps_frames"]:
            raise ValueError("Required PS not exercised")
        if runs["baseline"]["ps_info_bytes"] - runs["packed"]["ps_info_bytes"] != 9600:
            raise ValueError("PS struct saving differs")
        errors = compare_pcm(base.with_suffix('.pcm'), output / f"{name}-packed.pcm", frames)
        row = dict(input=name, input_sha256=digest(path), repeats=repeat, runs=runs, channels=errors,
                   output_layouts=sorted({(f[2],f[3]) for f in frames if f[1]}))
        results.append(row)
        print(name, "max", max(r['maximum'] for r in errors), "PS frames", runs['packed']['ps_frames'], flush=True)
    result = {"patch_sha256": digest(PATCH), "source_revision": REVISION, "source_archive_sha256": digest(archive),
              "probe_sha256": digest(PROBE), "reference_quantizer_sha256": digest(ROOT/'idf/esp32c3-oled-native/main/packed_complex14.h'),
              "compiler": subprocess.check_output(host_command(['gcc','--version']), text=True).splitlines()[0],
              "build_commands": commands, "rows": results, "ps_struct_saving_bytes": 9600,
              "note": "Actual supplied PS-only storage patch; host fixed-point test, no C3 port/CPU qualification"}
    (output / 'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'.build/faad-ps-patch-20261001')
    parser.add_argument('--archive',type=Path,default=ROOT/f'.build/faad2-comparison/faad2-{REVISION}.tar.gz')
    parser.add_argument('--recordings',type=Path,default=ROOT/'.build/aac-bfp16-real-20260930/inputs')
    args=parser.parse_args()
    run(args.output.resolve(),args.archive.resolve(),args.recordings.resolve())
