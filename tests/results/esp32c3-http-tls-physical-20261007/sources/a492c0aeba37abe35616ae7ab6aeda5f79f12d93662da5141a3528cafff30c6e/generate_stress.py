"""Generate long, high-bitrate stereo fixtures for any HTTP audio player.

Uses fixed-seed noise plus independent tones, explicit 16-bit PCM, and the
same encoder settings as the retained 11-second C3 calibration files. This
avoids confusing unsupported 24-bit input with a transport throughput test.
The existing 24-bit qualification fixtures remain separate, unresolved cases.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ENCODERS = {
    'mp3': ('mp3', 'audio/mpeg', ['-c:a', 'libmp3lame', '-b:a', '320k', '-write_xing', '0']),
    'flac': ('flac', 'audio/flac', ['-c:a', 'flac', '-compression_level', '8']),
    'vorbis': ('ogg', 'audio/ogg', ['-c:a', 'libvorbis', '-q:a', '10']),
    'opus': ('ogg', 'audio/ogg', ['-c:a', 'libopus', '-b:a', '510k', '-vbr', 'off',
                              '-application', 'audio', '-frame_duration', '20']),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--codec', choices=tuple(ENCODERS), nargs='+', default=list(ENCODERS))
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    args = parser.parse_args()
    if args.seconds < 43:
        parser.error('Use at least 43 seconds for a 40-second load observation')
    if args.output.exists():
        parser.error('Use a new output directory to preserve previous fixtures')
    args.output.mkdir(parents=True)
    source = args.output/'source-48k-stereo-s16.wav'
    duration = args.seconds
    filters = [
        f'anoisesrc=color=white:amplitude=0.34:sample_rate=48000:duration={duration}:seed=12345[nl]',
        f'anoisesrc=color=pink:amplitude=0.34:sample_rate=48000:duration={duration}:seed=67890[nr]',
        f'sine=frequency=997:sample_rate=48000:duration={duration}:beep_factor=2[tl]',
        f'sine=frequency=1601:sample_rate=48000:duration={duration}:beep_factor=2[tr]',
        "[nl][tl]amix=inputs=2:weights='0.72 0.28':normalize=0[left]",
        "[nr][tr]amix=inputs=2:weights='0.72 0.28':normalize=0[right]",
        '[left][right]amerge=inputs=2,alimiter=limit=0.95[out]',
    ]
    command = [args.ffmpeg, '-n', '-hide_banner', '-loglevel', 'error',
               '-filter_complex', ';'.join(filters), '-map', '[out]', '-ar', '48000',
               '-ac', '2', '-c:a', 'pcm_s16le', str(source)]
    subprocess.run(command, check=True)
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = dict(generator=subprocess.check_output([args.ffmpeg, '-version'], text=True).splitlines()[0],
                    source_sha256=digest(source), source_filter=filters, source_bits=16, fixtures=[])
    for codec in args.codec:
        extension, mime, options = ENCODERS[codec]
        name = f'stress-{codec}-48000-2ch-16bit-{duration}s'
        output = args.output/(name+'.'+extension)
        subprocess.run([args.ffmpeg, '-n', '-hide_banner', '-loglevel', 'error',
                        '-i', str(source), '-map', '0:a:0', *options, str(output)], check=True)
        probe = json.loads(subprocess.check_output([args.ffprobe, '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=sample_rate,channels,bits_per_raw_sample:format=duration',
            '-of', 'json', str(output)]))
        stream = probe['streams'][0]
        bits = int(stream.get('bits_per_raw_sample') or 16) if codec == 'flac' else 16
        if bits != 16 or int(stream['sample_rate']) != 48000 or int(stream['channels']) != 2:
            raise ValueError('Unexpected encoded source layout')
        seconds = float(probe['format']['duration'])
        manifest['fixtures'].append(dict(name=name, file=output.name, seconds=seconds,
            rate=48000, channels=2, bits=16, codec=codec, mime=mime, profile=codec,
            sha256=digest(output), bytes=output.stat().st_size,
            average_kbps=output.stat().st_size*8/seconds/1000, encoder_options=options))
        (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        print(name, flush=True)


if __name__ == '__main__':
    main()
