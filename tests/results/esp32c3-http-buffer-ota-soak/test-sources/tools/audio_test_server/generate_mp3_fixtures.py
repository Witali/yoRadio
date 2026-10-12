"""Generate original stereo MP3 controls for any board; retain encoder identity."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=130)
    args = parser.parse_args()
    if not 30 <= args.seconds <= 600:
        parser.error('Use 30..600 seconds')
    args.output.mkdir(parents=True, exist_ok=False)
    entries, commands = [], []
    for rate in (44100, 48000):
        name = f'mp3-256-{rate}-stereo'
        target = args.output / (name + '.mp3')
        source = (f'anoisesrc=color=pink:amplitude=0.15:seed=12345:sample_rate={rate}:duration={args.seconds}[noise];'
                  f'aevalsrc=0.12*sin(2*PI*997*t):s={rate}:d={args.seconds}[tone];'
                  '[noise][tone]amerge=inputs=2')
        command = ['ffmpeg', '-n', '-nostdin', '-v', 'error', '-f', 'lavfi', '-i', source,
                   '-ac', '2', '-ar', str(rate), '-c:a', 'libmp3lame', '-b:a', '256k',
                   '-write_xing', '0', '-id3v2_version', '0', '-write_id3v1', '0', str(target)]
        subprocess.run(command, check=True, timeout=90)
        raw = target.read_bytes()
        assert raw[:2] == b'\xff\xfb', 'Expected MPEG-1 Layer III without leading metadata'
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
            'stream=codec_name,sample_rate,channels:format=duration', '-of', 'json', str(target)], timeout=30))
        stream, = probe['streams']
        assert stream == dict(codec_name='mp3', sample_rate=str(rate), channels=2), probe
        duration = float(probe['format']['duration'])
        assert args.seconds <= duration < args.seconds + .1, duration
        # Decode the entire generated file, with errors made fatal.
        subprocess.run(['ffmpeg', '-v', 'error', '-xerror', '-i', str(target), '-f', 'null', '-'],
                       check=True, timeout=90)
        entries.append(dict(name=name, file=target.name, codec='mp3', profile='mp3',
            seconds=duration, rate=rate, channels=2, bits=16, mime='audio/mpeg',
            sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
        commands.append(command)
    manifest = dict(fixtures=entries, commands=commands,
        ffmpeg_version=subprocess.check_output(['ffmpeg','-version'], text=True).splitlines()[0],
        source='Original deterministic pink noise in left channel, 997 Hz tone in right channel; no broadcast material')
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Generated and independently decoded', len(entries), 'MP3 controls')


if __name__ == '__main__':
    main()
