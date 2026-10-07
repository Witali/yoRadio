"""Compile an SBR pointer-table size experiment for RV32; does not edit firmware.

First fetch the pinned reference headers with sbr_memory_layout.py. This checks
structure sizes only, not decoder equivalence or Espressif binary compatibility.
Requires pyelftools and the ESP32-C3 GCC toolchain.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from sbr_memory_layout import PROBE, REVISION, SOURCE, layouts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    reference = args.reference.resolve()
    output = args.output.resolve()
    if output == reference or reference in output.parents:
        raise ValueError('Keep experiment output outside the reference directory')
    headers = {p.name: p.read_bytes() for p in reference.glob('*.h')}
    original = headers['s_sbr_frame_data.h'].decode()
    compact = original
    for name in ('fBuf_man', 'fBuf_exp', 'fBufN_man', 'fBufN_exp'):
        compact, count = re.subn(r'(Int32\s*\*\s*' + name + r'\s*\[)64(\])',
                                r'\g<1>5\2', compact)
        if count != 1:
            raise ValueError('Unexpected reference declaration: ' + name)
    results, commands = {}, {}
    for variant in ('baseline', 'compact_smoothing_pointers'):
        folder = output / variant
        folder.mkdir(parents=True, exist_ok=True)
        for name, data in headers.items():
            if variant != 'baseline' and name == 's_sbr_frame_data.h':
                data = compact.encode()
            (folder / name).write_bytes(data)
        (folder / 'probe.cpp').write_text(PROBE)
        command = [str(args.compiler.resolve()), '-g', '-nostdlib', '-Wl,-e,0',
                   '-o', 'layout.elf', 'probe.cpp']
        subprocess.run(command, cwd=folder, check=True, capture_output=True, text=True)
        results[variant] = layouts(folder / 'layout.elf')
        commands[variant] = command
    base = results['baseline']['SBRDECODER_DATA']['bytes']
    after = results['compact_smoothing_pointers']['SBRDECODER_DATA']['bytes']
    if base != 55128 or base - after != 2 * 4 * (64 - 5) * 4:
        raise ValueError('Reference layout differs from the audited RV32 layout')
    report = {
        'source': SOURCE, 'revision': REVISION,
        'scope': 'Reference sizeof/DWARF experiment only; no modified decoder executed',
        'compiler': subprocess.check_output([str(args.compiler), '--version'], text=True).splitlines()[0],
        'commands': commands,
        'headers_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in sorted(headers.items())},
        'sbr_before_bytes': base, 'sbr_after_bytes': after,
        'potential_payload_saving_bytes': base - after,
        'layouts': results,
    }
    (output / 'layout-experiment.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('sbr_before_bytes', 'sbr_after_bytes',
                                            'potential_payload_saving_bytes')}))


if __name__ == '__main__':
    main()
