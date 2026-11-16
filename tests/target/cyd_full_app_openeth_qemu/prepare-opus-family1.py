"""Generate a sustained surround Opus workload and record independent libopus PCM metrics."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
RATE = 48000
SECONDS = 14
# The host decoder returns WAVE order. The output task receives Vorbis order.
LAYOUTS = {4: ('quad', (0, 1, 2, 3)),
           6: ('5.1', (0, 2, 1, 4, 5, 3)),
           8: ('7.1', (0, 2, 1, 6, 7, 4, 5, 3))}
FREQUENCIES = (211, 463, 337, 73, 853, 983, 593, 719)
AMPLITUDES = ('0.035', '0.041', '0.038', '0.056', '0.050', '0.053', '0.044', '0.047')


def channel_metrics(samples):
    energy = crossings = previous = 0
    for sample in samples:
        energy += sample * sample
        if sample:
            current = 1 if sample > 0 else -1
            crossings += bool(previous and current != previous)
            previous = current
    return dict(energy=energy, crossings=crossings)


def maximum_page_bytes(body):
    maximum = 0
    offset = 0
    while offset < len(body):
        if body[offset:offset + 4] != b'OggS' or offset + 27 > len(body):
            raise RuntimeError('Invalid Ogg page boundary')
        header_end = offset + 27 + body[offset + 26]
        page_end = header_end + sum(body[offset + 27:header_end])
        if header_end > len(body) or page_end > len(body):
            raise RuntimeError('Incomplete Ogg page')
        maximum = max(maximum, page_end - offset)
        offset = page_end
    return maximum


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--packet-ms', type=int, choices=(20, 120), required=True)
    parser.add_argument('--channels', type=int, choices=LAYOUTS, default=8)
    parser.add_argument('--ogg-page-ms', type=int, choices=(200, 1000), default=1000)
    parser.add_argument('--ffmpeg', default='ffmpeg')
    parser.add_argument('--ffprobe', default='ffprobe')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        parser.error('use a fresh directory under the project .build')
    output.mkdir(parents=True)

    channels = args.channels
    wave_layout, vorbis_order = LAYOUTS[channels]
    fixture = output / 'family1.ogg'
    signals = '|'.join(f'{amplitude}*sin(2*PI*{frequency}*t)'
                       for amplitude, frequency in zip(AMPLITUDES[:channels], FREQUENCIES))
    subprocess.run([
        args.ffmpeg, '-nostdin', '-v', 'error', '-xerror', '-f', 'lavfi', '-i',
        f'aevalsrc={signals}:s={RATE}:d={SECONDS}:c={wave_layout}',
        '-map_metadata', '-1', '-c:a', 'libopus', '-mapping_family', '1',
        '-b:a', '512k', '-vbr', 'off', '-frame_duration', str(args.packet_ms),
        '-fflags', '+bitexact', '-page_duration', str(args.ogg_page_ms * 1000), str(fixture),
    ], check=True)
    info = json.loads(subprocess.check_output([
        args.ffprobe, '-v', 'error', '-select_streams', 'a:0',
        '-show_streams', '-show_packets',
        '-show_entries', 'stream=codec_name,channels,channel_layout,sample_rate:packet=duration',
        '-of', 'json', str(fixture),
    ]))
    stream, = info['streams']
    if (stream['codec_name'], stream['sample_rate'], stream['channels'], stream['channel_layout']) != (
            'opus', str(RATE), channels, wave_layout):
        raise RuntimeError('Unexpected creator stream geometry')
    durations = [row['duration'] for row in info['packets']]
    samples_per_packet = args.packet_ms * 48
    if not durations or any(duration != samples_per_packet for duration in durations[:-1]) or not (
            0 < durations[-1] <= samples_per_packet):
        raise RuntimeError('Encoded packets lack the requested duration')
    pcm = subprocess.check_output([
        args.ffmpeg, '-nostdin', '-v', 'error', '-xerror', '-c:a', 'libopus',
        '-i', str(fixture), '-map', '0:a:0', '-c:a', 'pcm_s16le', '-f', 's16le', '-',
    ])
    frames = RATE * SECONDS
    if len(pcm) != frames * channels * 2:
        raise RuntimeError('Unexpected decoded length after Ogg Opus trimming')
    samples = array('h')
    samples.frombytes(pcm)
    if sys.byteorder != 'little':
        samples.byteswap()
    body = fixture.read_bytes()
    reference = dict(
        file=fixture.name,
        sha256=hashlib.sha256(body).hexdigest(),
        bytes=len(body),
        frames=frames,
        channels=channels,
        packet_ms=args.packet_ms,
        packets=len(durations),
        ogg_page_ms=args.ogg_page_ms,
        max_page_bytes=maximum_page_bytes(body),
        reference_pcm_sha256=hashlib.sha256(pcm).hexdigest(),
        metrics=[channel_metrics(samples[channel::channels]) for channel in vorbis_order],
        ffmpeg_version=subprocess.check_output([args.ffmpeg, '-version'], text=True).splitlines()[0],
    )
    (output / 'fixture.json').write_text(json.dumps(reference, indent=2) + '\n', encoding='utf-8')
    print(f'Prepared {channels}-channel Family 1, {args.packet_ms} ms, '
          f'{len(durations)} packets and {frames} frames')


if __name__ == '__main__':
    main()
