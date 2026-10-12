"""Download public FFmpeg fixtures and record independently decoded duration.

Downloads remain in the chosen local media cache; do not commit the audio.
TLS verification remains enabled. No device access or firmware changes.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

from common import require
from public_streams import public_url

SOURCES = {
    'flac': 'https://samples.ffmpeg.org/A-codecs/lossless/luckynight.flac',
    'opus': 'https://samples.ffmpeg.org/A-codecs/opus/testvector01.ogg',
    'vorbis': 'https://samples.ffmpeg.org/ogg/Vorbis/coyote.ogg',
}
MAX_BYTES = 32 * 1024 * 1024


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.output
    require(not root.exists(), 'Use a new output directory; preserve prior evidence')
    (root / 'media').mkdir(parents=True)

    def probe(item):
        name, url = item
        path = root / 'media' / (name + Path(url).suffix)
        with urlopen(public_url(url), timeout=20) as response:
            final = public_url(response.geturl())
            require(response.status == 200, 'Expected HTTP 200')
            blob = response.read(MAX_BYTES + 1)
            require(0 < len(blob) <= MAX_BYTES, 'Oversized/empty fixture')
            expected = response.headers.get('Content-Length')
            require(expected is not None and int(expected) == len(blob), 'Incomplete response')
            headers = {k: response.headers.get(k) for k in ('Content-Length', 'Content-Type', 'Last-Modified', 'ETag')}
        path.write_bytes(blob)
        command = ['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries',
                   'stream=codec_name,profile,sample_rate,channels,bits_per_raw_sample,bits_per_sample:format=duration',
                   '-of', 'json', str(path)]
        value = json.loads(subprocess.run(command, capture_output=True, timeout=30, check=True).stdout)
        require(len(value['streams']) == 1, 'Expected one audio stream')
        stream = value['streams'][0]
        require(stream['codec_name'] == name, 'Wrong source codec')
        channels, rate = int(stream['channels']), int(stream['sample_rate'])
        decoded = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path),
            '-map', '0:a:0', '-c:a', 'pcm_s16le', '-f', 's16le', '-'],
            capture_output=True, timeout=40, check=True).stdout
        require(len(decoded) % (channels * 2) == 0, 'Incomplete PCM frame')
        frames = len(decoded) // (channels * 2)
        result = dict(url=url, resolved_url=final, tls_verify=True, headers=headers,
            bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(), ffprobe=value,
            pcm_s16_sha256=hashlib.sha256(decoded).hexdigest(), decoded_frames=frames,
            decoded_seconds=frames/rate, spec=dict(codec=name, rate=rate, channels=channels,
                bits=16, label='FLAC' if name == 'flac' else 'OGG', seconds=frames/rate))
        (root / (name + '-reference.json')).write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(dict(codec=name, bytes=len(blob), spec=result['spec'])), flush=True)
        return name, result

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        references = dict(pool.map(probe, SOURCES.items()))
    version = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    (root / 'references.json').write_text(json.dumps(dict(ffmpeg_version=version, sources=references), indent=2)+'\n')


if __name__ == '__main__':
    main()
