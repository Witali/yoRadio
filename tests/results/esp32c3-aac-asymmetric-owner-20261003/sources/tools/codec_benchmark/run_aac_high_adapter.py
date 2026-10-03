#!/usr/bin/env python3
"""Qualify the TLS-scoped PC18 production adapter in QEMU (no board access)."""
import hashlib
import math
import re
import struct
import sys
import wave
from pathlib import Path
import run_aac_bfp16 as common
import run_aac_compact_adapter as adapter


OWNER_BYTES_BY_LAYOUT={'pc18':47980,'four_row_smoothing':45932,
                       'scoped_low_qmf':35900,'asymmetric_channels':32744}

def parse_log(log, *, owner_bytes=47980):
    if owner_bytes not in OWNER_BYTES_BY_LAYOUT.values():
        raise ValueError('Unknown production high-history owner layout')
    result = adapter.parse_log(log)
    rows = re.findall(r'AACCOMPACT_CONCURRENT_PASS decoders=2 samples=(\d+) pcm_hash=([0-9a-f]{8})', log)
    if len(rows) != 1 or int(rows[0][0]) != result['adapter']['samples']:
        raise ValueError('Missing concurrent PCM verification')
    memory = re.findall(r'AACCOMPACT_MEMORY owner_bytes=(\d+) block_bytes=(\d+) context_bytes=(\d+)', log)
    if len(memory) != 1 or int(memory[0][0]) != owner_bytes or int(memory[0][2]) != 24:
        raise ValueError('Unexpected production owner/context size')
    result.update(experiment='production_pc18_high_history_adapter',
                  concurrent=dict(decoders=2, samples=int(rows[0][0]), pcm_hash=rows[0][1]),
                  memory=dict(zip(('owner_bytes', 'block_bytes', 'context_bytes'), map(int, memory[0]))))
    return result


def compare_pcm(reference, candidate):
    maximum = different = square_sum = samples = 0
    nonzero = False
    digest = hashlib.sha256()
    with wave.open(str(reference)) as a, wave.open(str(candidate)) as b:
        if a.getparams() != b.getparams() or not a.getnframes() or a.getsampwidth() != 2:
            raise ValueError('PCM shape/duration changed, empty or not signed-16')
        while True:
            left, right = a.readframes(4096), b.readframes(4096)
            if not left:
                break
            nonzero |= any(left)
            digest.update(right)
            for (x,), (y,) in zip(struct.iter_unpack('<h', left), struct.iter_unpack('<h', right)):
                error = abs(x-y)
                maximum = max(maximum, error)
                different += bool(error)
                square_sum += error*error
                samples += 1
        if not nonzero:
            raise ValueError('Silent reference is not precision evidence')
        return dict(frames=a.getnframes(), channels=a.getnchannels(), rate=a.getframerate(),
                    sample_width=2, samples=samples, different=different,
                    max_pcm_error_lsb=maximum, rms_error_lsb=math.sqrt(square_sum/samples),
                    pcm_sha256=digest.hexdigest(), reference_wav_sha256=common.sha256(reference))


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'high-adapter')
    parser.add_argument('--reference-wav', type=Path, required=True)
    args = parser.parse_args()
    if args.input:
        parser.error('This suite uses the retained format/lifecycle sequence')

    def check(log):
        result = parse_log(log)
        pcm = compare_pcm(args.reference_wav, args.output/'audio.wav')
        result.update(pcm=pcm, precision_pass=pcm['max_pcm_error_lsb'] <= 3,
                      precision_limit_lsb=3, summaries=[])
        return result

    sys.exit(common.run(args, log_parser=check, config_key='YORADIO_AAC_HIGH_HISTORY'))
