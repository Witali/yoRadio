"""Illustrate G.711 quantization on all 16-bit values; this is NOT an SBR test.

Uses Python 3.12's audioop (removed in Python 3.13). No extra package is needed
in the pinned ESP-IDF Python 3.12 environment.
"""
import argparse
import audioop
import json
from pathlib import Path
import struct
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    samples = list(range(-32768, 32768))
    # audioop uses native-endian samples; match that convention explicitly.
    raw = struct.pack('=65536h', *samples)
    results = {}
    for name, encode, decode in (
        ('mu-law', audioop.lin2ulaw, audioop.ulaw2lin),
        ('A-law', audioop.lin2alaw, audioop.alaw2lin),
    ):
        restored = struct.unpack('=65536h', decode(encode(raw, 2), 2))
        errors = [abs(a - b) for a, b in zip(samples, restored)]
        peak = max(errors)
        index = errors.index(peak)
        results[name] = {
            'max_absolute_error': peak,
            'input_at_first_max': samples[index],
            'output_at_first_max': restored[index],
            'samples_exceeding_one_lsb': sum(error > 1 for error in errors),
            'sample_30000_output': restored[30000 + 32768],
        }
    report = {
        'scope': 'Illustrative G.711 round trip of every signed 16-bit input; NOT an SBR simulation',
        'implementation': 'Python audioop', 'python_version': sys.version.split()[0],
        'inputs': len(samples), 'pcm_bits': 16, 'results': results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', newline='\n')
    print(json.dumps(results))


if __name__ == '__main__':
    main()
