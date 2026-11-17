"""Bound static Xtensa frames without claiming total runtime stack depth."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
# The original full-application decoder frame was 1744 bytes. Keeping its
# frame below 2 KiB protects the raw Opus path from the Ogg staging array.
LIMITS = {'decoder_task': 2048, 'ogp_decode_word_page': 2304}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--objdump', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output.exists():
        raise ValueError('Use a fresh report under the current worktree .build')
    output.parent.mkdir(parents=True, exist_ok=True)
    elf, objdump = args.elf.resolve(strict=True), args.objdump.resolve(strict=True)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(passed=False, scope='static windowed-ABI compiler frames',
                  physical_tested=False, total_stack_depth_verified=False,
                  elf_sha256=sha(elf), objdump_sha256=sha(objdump),
                  maximum_frame_bytes=LIMITS, frame_bytes={})
    try:
        header = elf.read_bytes()[:20]
        if header[:6] != b'\x7fELF\x01\x01' or struct.unpack_from('<H', header, 18)[0] != 94:
            raise ValueError('Expected a little-endian 32-bit Xtensa ELF')
        for name, maximum in LIMITS.items():
            child = subprocess.run([str(objdump), '-d', '--disassemble=' + name, str(elf)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if child.returncode:
                raise ValueError('The installed objdump failed')
            text = child.stdout.decode('utf-8', errors='replace')
            match = re.search(r'<' + re.escape(name) + r'>:\s*\n\s*[0-9a-f]+:\s+'
                              r'[0-9a-f]+\s+entry\s+a1,\s*(0x[0-9a-f]+|[0-9]+)', text)
            if not match:
                raise ValueError('Missing windowed-ABI entry for ' + name)
            frame = int(match.group(1), 0)
            report['frame_bytes'][name] = frame
            if not 0 < frame <= maximum:
                raise ValueError(name + ' exceeds its static frame budget')
        report['passed'] = True
    except (ValueError, OSError, struct.error) as error:
        report['reason'] = str(error)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(passed=report['passed'], frame_bytes=report['frame_bytes'],
                          reason=report.get('reason'))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
