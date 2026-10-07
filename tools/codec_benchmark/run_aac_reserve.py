#!/usr/bin/env python3
"""Check early AAC reservation in QEMU against an existing reference PCM WAV.

No board access. The known identical-header implicit-SBR limitation is recorded,
not accepted as full-format production qualification.
"""
import hashlib
import re
import sys
import wave
from pathlib import Path
import run_aac_bfp16 as common

EXPECTED = (
    ('HE44 first', 44100, 2), ('LC44 stereo', 44100, 2),
    ('LC22 mono', 22050, 1), ('LC48 stereo', 48000, 2),
    ('HE44 stereo', 44100, 2), ('HE48 stereo', 48000, 2),
    ('HEv2 stereo', 44100, 2), ('LC22 same header', 22050, 1),
    ('Implicit SBR core', 22050, 1), ('HEv2 restart', 44100, 2),
)


def parse_log(log):
    for marker in ('QEMU_AAC_FORMAT_PASS', 'QEMU_SMOKE_PASS',
                   'QEMU_OLED_PASS', 'QEMU_AUDIO_PASS'):
        if marker not in log:
            raise ValueError('Missing marker: ' + marker)
    rows = re.findall(r'QEMU_AAC_CASE_PASS (.*?): (\d+) Hz (\d+) ch, '
                      r'(\d+) frames, (\d+) samples, free (\d+) min (\d+)', log)
    if tuple((r[0], int(r[1]), int(r[2])) for r in rows) != EXPECTED:
        raise ValueError('Incomplete/duplicate format matrix')
    if any(min(map(int, r[3:])) <= 0 for r in rows):
        raise ValueError('Empty output or invalid heap observation')
    return dict(format_cases=[list(row) for row in rows], known_limitations=[
        'Implicit SBR/PS with unchanged ADTS headers still needs a restart.'])


def compare_pcm(reference, candidate):
    digest = hashlib.sha256()
    nonzero = False
    with wave.open(str(reference)) as a, wave.open(str(candidate)) as b:
        if a.getparams() != b.getparams() or not a.getnframes():
            raise ValueError('PCM shape/duration changed or empty output')
        while True:
            left, right = a.readframes(4096), b.readframes(4096)
            if left != right:
                raise ValueError('PCM changed')
            if not left:
                break
            nonzero |= any(left)
            digest.update(left)
        if not nonzero:
            raise ValueError('Silent output is not equivalence evidence')
        return dict(frames=a.getnframes(), channels=a.getnchannels(),
                    rate=a.getframerate(), sample_width=a.getsampwidth(),
                    max_pcm_error_lsb=0, pcm_sha256=digest.hexdigest(),
                    reference_wav_sha256=common.sha256(reference))


if __name__ == '__main__':
    parser = common.make_parser(__doc__, 'reserve')
    parser.add_argument('--reference-wav', type=Path, required=True)
    args = parser.parse_args()
    if args.input:
        parser.error('This suite uses only the retained format sequence')

    def check(log):
        result = parse_log(log)
        result.update(pcm=compare_pcm(args.reference_wav, args.output/'audio.wav'),
                      precision_pass=True, precision_limit_lsb=0, summaries=[])
        return result

    sys.exit(common.run(args, log_parser=check,
                         config_key='YORADIO_AAC_EARLY_SBR_RESERVE'))
