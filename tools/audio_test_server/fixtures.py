"""Synthetic audio assets shared by C3, CYD, ESP8266 and other players."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEQUENCES = {'changing': ['lc-44100-stereo','lc-48000-stereo','he-48000-stereo','hev2-44100-stereo'],
             'implicit-sbr': ['lc-22050-mono','hev2-44100-stereo','lc-48000-stereo']}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_fixtures(extra_manifest=None):
    """Original synthetic audio for any HTTP audio client; verify source bytes."""
    result = {}
    folder = ROOT / 'tests/fixtures/esp32c3_calibration'
    for spec in json.loads((folder / 'manifest.json').read_text())['fixtures']:
        name = Path(spec['file']).stem
        data = (folder / spec['file']).read_bytes()
        require(sha(data) == spec['sha256'], f'Fixture hash mismatch: {name}')
        codec = spec['codec']
        result[name] = dict(data=data, seconds=11, rate=48000, channels=2, bits=16,
            codec=codec, profile='AAC-LC' if codec == 'aac' else codec,
            mime={'aac':'audio/aac', 'mp3':'audio/mpeg', 'flac':'audio/flac',
                  'vorbis':'audio/ogg', 'opus':'audio/ogg'}[codec], sha256=sha(data))
    folder = ROOT / 'tests/fixtures/aac_stream_format'
    for name, spec in json.loads((folder / 'manifest.json').read_text())['files'].items():
        data = (folder / name).read_bytes()
        require(sha(data) == spec['sha256'], f'Fixture hash mismatch: {name}')
        pos = frames = 0
        while pos < len(data):
            require(pos + 7 <= len(data) and data[pos] == 255, 'Invalid ADTS fixture')
            size = ((data[pos+3] & 3) << 11) | (data[pos+4] << 3) | (data[pos+5] >> 5)
            require(size >= 7 and pos + size <= len(data), 'Invalid ADTS length')
            frames += (data[pos+6] & 3) + 1
            pos += size
        aot = spec['audio_object_type']
        seconds = frames * (1024 if aot == 2 else 2048) / spec['sample_rate']
        # A finite ~12 s ADTS file, long enough to observe actual playback/EOF.
        repeats = max(1, round(12 / seconds))
        payload = data * repeats
        result[Path(name).stem] = dict(data=payload, seconds=seconds * repeats,
            rate=spec['sample_rate'], channels=spec['channels'], bits=16,
            codec='aac', profile={2:'AAC-LC', 5:'HE-AAC', 29:'HE-AACv2'}[aot],
            mime='audio/aac', sha256=sha(payload), source_sha256=sha(data))
    for name, sequence in SEQUENCES.items():
        payload = b''.join(result[n]['data'] for n in sequence)
        result[name] = dict(data=payload, seconds=sum(result[n]['seconds'] for n in sequence),
            segments=[result[n] for n in sequence], sequence=sequence, codec='aac',
            mime='audio/aac', sha256=sha(payload))
    if extra_manifest:
        manifest_path = Path(extra_manifest).resolve()
        for entry in json.loads(manifest_path.read_text())['fixtures']:
            path = (manifest_path.parent / entry['file']).resolve()
            require(path.is_relative_to(manifest_path.parent), 'Fixture escapes manifest directory')
            require(entry['name'] not in result and '/' not in entry['name'], 'Duplicate/invalid fixture name')
            data = path.read_bytes()
            require(sha(data) == entry['sha256'], 'Generated fixture hash mismatch')
            require(entry['seconds'] > 0, 'Missing fixture duration')
            result[entry['name']] = dict(entry, data=data)
    return result
