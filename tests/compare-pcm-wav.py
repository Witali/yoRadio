"""Require byte-identical captured PCM for an unchanged deterministic fixture run."""
import argparse
import hashlib
import json
from pathlib import Path
import wave

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('baseline', type=Path)
parser.add_argument('candidate', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
digest = hashlib.sha256()
nonzero = False
with wave.open(str(args.baseline)) as a, wave.open(str(args.candidate)) as b:
    assert a.getparams() == b.getparams(), 'Different PCM layout/duration'
    assert a.getnframes() > 0, 'Empty output'
    while True:
        left, right = a.readframes(4096), b.readframes(4096)
        assert left == right, 'PCM samples differ'
        if not left:
            break
        nonzero |= any(left)
        digest.update(left)
    assert nonzero, 'Silent output is not a decoder equivalence check'
    result = dict(result='PASS', comparison='byte-for-byte',
                  frames=a.getnframes(), channels=a.getnchannels(),
                  sample_width=a.getsampwidth(), rate=a.getframerate(),
                  pcm_sha256=digest.hexdigest())
if args.output:
    args.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
