"""Resolve implicit AAC PS using the independent, unquantized FAAD probe.

FFprobe can advertise HE-AACv2 for mono SBR without PS. A source capture is
temporary; only its hash, frame count and decoder statistics are retained.
The command is an explicit local JSON argv list, never supplied by a server.
"""
import json
from pathlib import Path
import subprocess
import tempfile

from common import require, sha


def adts_frames(data):
    offset = frames = 0
    while offset < len(data):
        h = data[offset:offset+7]
        require(len(h) == 7 and h[0] == 255 and h[1] & 0xf6 == 0xf0,
                'Incomplete ADTS reference capture')
        size = ((h[3] & 3) << 11) | (h[4] << 3) | (h[5] >> 5)
        require(not h[6] & 3 and size >= (7 if h[1] & 1 else 9)
                and offset+size <= len(data), 'Invalid ADTS reference frame')
        offset += size
        frames += 1
    require(frames > 0, 'Empty AAC reference')
    return frames


def verified_spec(spec, result, frames):
    require(result.get('scope') == 0 and result.get('frames') == frames
            and frames >= 10 and result.get('samples', 0) > 0
            and result.get('square_signal', 0) > 0,
            'Missing complete, unquantized, non-silent FAAD reference')
    require(result.get('rate') == spec['rate'] and result.get('channels') in (1, 2),
            'Reference decoders disagree on rate or channels')
    ps = result.get('ps_frames')
    require(isinstance(ps, int) and 0 <= ps <= frames, 'Invalid PS evidence')
    if spec['profile'] == 'LC':
        require(ps == 0 and result['channels'] == spec['channels'],
                'Reference decoders disagree on LC format')
        return dict(spec)
    require(spec['profile'] in ('HE-AAC', 'HE-AACv2'), 'Not an SBR reference')
    if ps:
        require(result['channels'] == 2, 'PS requires stereo output')
        return dict(spec, profile='HE-AACv2', label='HE-AACv2 ', source_channels=2)
    # FAAD reports one source/output channel for genuine HE mono; the native
    # radio and FFmpeg may duplicate it. Keep the probed PCM shape separate.
    return dict(spec, profile='HE-AAC', label='HE-AAC ', source_channels=result['channels'])


def probe_aac(url, spec, command, ffmpeg='ffmpeg'):
    require(isinstance(command, list) and command and all(isinstance(v, str) for v in command),
            'AAC reference command must be a nonempty JSON argv list')
    require(any('{input}' in v or '{input_wsl}' in v for v in command),
            'AAC reference command requires an input placeholder')
    with tempfile.TemporaryDirectory(prefix='yoradio-aac-reference-') as folder:
        source = Path(folder)/'reference.aac'
        capture = subprocess.run([ffmpeg, '-v', 'error', '-rw_timeout', '15000000',
            '-tls_verify', '1', '-i', url, '-t', '5', '-map', '0:a:0',
            '-c:a', 'copy', '-f', 'adts', str(source)], capture_output=True, timeout=35)
        require(capture.returncode == 0, 'Could not capture the verified AAC reference')
        data = source.read_bytes()
        frames = adts_frames(data)
        wsl_path = ''
        if any('{input_wsl}' in v for v in command):
            wsl_path = subprocess.check_output(['wsl.exe', '--exec', 'wslpath', '-a',
                                               source.as_posix()], text=True, timeout=10).strip()
        argv = [v.replace('{input_wsl}', wsl_path).replace('{input}', str(source)) for v in command]
        decoded = subprocess.run(argv, capture_output=True, timeout=30)
        require(decoded.returncode == 0, 'Independent AAC reference decoder failed')
        result = json.loads(decoded.stdout)
        resolved = verified_spec(spec, result, frames)
        return dict(spec=resolved, ffprobe_spec=spec, input_sha256=sha(data),
                    input_bytes=len(data), frames=frames, faad=result,
                    command_sha256=sha(json.dumps(command).encode()),
                    scope='Five-second live-source observation; no acoustic or PCM-equivalence claim')
