"""Generate and independently audit complete synthetic 120 ms Ogg Opus input.

Only a fresh ignored capture directory is written. Installing software, native
MCU builds, flashing and publication are deliberately outside this generator.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'tests/fixtures/esp32c3_calibration/flac-level8.flac'
SOURCE_SHA = 'd9a54de9e470158428bb340d2278baa6a36a5f5571ea8083af390ec46ca39aad'
PLAYBACK_BYTES = 2112000


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def crc(page):
    value = 0
    for byte in page:
        value ^= byte << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def opus_packet(packet):
    """RFC 6716 section 3 framing and 48 kHz frame/packet duration."""
    need(packet, 'nonempty audio packet')
    toc, code = packet[0], packet[0] & 3
    config = toc >> 3
    samples = (120 << (config & 3)) if config >= 16 else (
        (960 if config & 1 else 480) if config >= 12 else ((480 << (config & 3)) if config & 3 < 3 else 2880))
    at, end = 1, len(packet)

    def size():
        nonlocal at
        need(at < end, 'complete Opus frame length')
        first = packet[at]
        at += 1
        if first < 252:
            return first
        need(at < end, 'complete extended Opus frame length')
        result = first + 4 * packet[at]
        at += 1
        return result

    if code == 0:
        sizes = [end - at]
    elif code == 1:
        need((end - at) % 2 == 0, 'two equal CBR frames')
        sizes = [(end - at) // 2] * 2
    elif code == 2:
        first = size()
        sizes = [first, end - at - first]
    else:
        need(at < end, 'Opus code 3 count byte')
        control = packet[at]
        at += 1
        count = control & 63
        need(0 < count <= 48 and count * samples <= 5760, 'at most 120 ms per legal Opus packet')
        if control & 64:
            padding = 0
            while True:
                need(at < end, 'complete Opus padding extent')
                extra = packet[at]
                at += 1
                padding += 254 if extra == 255 else extra
                if extra != 255:
                    break
            end -= padding
            need(end >= at, 'Opus padding within packet')
        if control & 128:
            sizes = [size() for _ in range(count - 1)]
            sizes.append(end - at - sum(sizes))
        else:
            need((end - at) % count == 0, 'code 3 equal CBR frame lengths')
            sizes = [(end - at) // count] * count
    need(all(0 <= item <= 1275 for item in sizes) and sum(sizes) == end - at, 'legal complete Opus frame extents')
    return dict(mode='CELT' if config >= 16 else ('hybrid' if config >= 12 else 'SILK'),
                stereo=bool(toc & 4), frames=len(sizes), samples=len(sizes) * samples,
                samples_per_frame=samples, bytes=len(packet), frame_bytes=sizes)


def audit(body):
    """Strict single-stream fixture audit, including continuation and CRCs."""
    pages, packets, unfinished = [], [], bytearray()
    at, serial, raw_frames = 0, None, 0
    page_packets = []
    while at < len(body):
        need(at + 27 <= len(body) and body[at:at+5] == b'OggS\x00', 'complete Ogg v0 page header')
        flags, segments = body[at + 5], body[at + 26]
        need(at + 27 + segments <= len(body), 'complete Ogg lacing table')
        lacing = body[at + 27:at + 27 + segments]
        end = at + 27 + segments + sum(lacing)
        need(end <= len(body), 'complete Ogg page payload')
        page = body[at:end]
        checksum = int.from_bytes(page[22:26], 'little')
        need(crc(page[:22] + bytes(4) + page[26:]) == checksum, 'every Ogg CRC')
        current_serial = int.from_bytes(page[14:18], 'little')
        if serial is None:
            serial = current_serial
        need(current_serial == serial and int.from_bytes(page[18:22], 'little') == len(pages), 'one consecutive logical stream')
        need(bool(flags & 1) == bool(unfinished), 'packet continuation flags match lacing')
        need(bool(flags & 2) == (not pages) and not flags & ~7, 'only initial BOS and known flags')
        position = 27 + segments
        completed_audio = 0
        for length in lacing:
            unfinished.extend(page[position:position + length])
            position += length
            if length < 255:
                packet = bytes(unfinished)
                unfinished.clear()
                packets.append(packet)
                if len(packets) > 2:
                    measured = opus_packet(packet)
                    raw_frames += measured['samples']
                    page_packets.append(measured)
                    completed_audio += 1
        granule = int.from_bytes(page[6:14], 'little')
        if completed_audio and not flags & 4:
            need(granule == raw_frames, 'zero initial granule offset without skipped audio')
        need(not flags & 4 or end == len(body), 'EOS only on final page')
        pages.append(dict(sequence=len(pages), flags=flags, granule=granule,
                          encoded_bytes=len(page), completed_audio=completed_audio,
                          decoded_frames_through_page=raw_frames))
        at = end
    need(pages and pages[-1]['flags'] & 4 and not unfinished and len(packets) > 2, 'complete terminal packet/page')
    head = packets[0]
    need(len(head) == 19 and head[:9] == b'OpusHead\x01' and head[9] == 2 and
         int.from_bytes(head[12:16], 'little') == 48000 and head[16:19] == bytes(3),
         '48 kHz stereo family-0 zero-gain Opus identification')
    need(packets[1].startswith(b'OpusTags'), 'Opus comment packet')
    preskip = int.from_bytes(head[10:12], 'little')
    eos = pages[-1]['granule']
    previous = max((row['granule'] for row in pages[:-1] if row['completed_audio']), default=0)
    need(previous <= eos <= raw_frames and eos >= preskip, 'legal terminal granule bounds')
    need(all(row['mode'] == 'CELT' and row['stereo'] and row['samples_per_frame'] == 960 and
             row['frames'] == 6 and row['samples'] == 5760 for row in page_packets), 'every packet is six 20 ms CELT frames')
    return dict(pages=pages, page_count=len(pages), all_page_crcs_valid=True,
                audio_packet_count=len(page_packets), packet_samples=dict(Counter(str(row['samples']) for row in page_packets)),
                packet_duration_ms=120, samples_per_packet=5760, channels=2, sample_rate=48000,
                raw_frames=raw_frames, preskip=preskip, eos_granule=eos,
                initial_granule_offset=0, tail_frames=raw_frames-eos,
                playback_frames=eos-preskip, playback_pcm16_bytes=(eos-preskip)*4,
                maximum_packet_pcm16_bytes=max(row['samples'] for row in page_packets)*4,
                maximum_packet_encoded_bytes=max(row['bytes'] for row in page_packets), packets=page_packets)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--ffmpeg', type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and out != ROOT / '.build' and not out.exists(), 'fresh ignored capture')
    tool = (args.ffmpeg or Path(shutil.which('ffmpeg.exe') or '')).resolve()
    need(tool.is_file() and sha(SOURCE.read_bytes()) == SOURCE_SHA, 'installed FFmpeg and pinned synthetic lossless source')
    out.mkdir(parents=True)
    shutil.copyfile(__file__, out / 'generate.py')
    report = dict(passed=False, completed=False, native_decoder_tested=False, resize_retry_qualified=False,
                  physical_device=False, external_network=False, commands=[],
                  source=dict(path=SOURCE.relative_to(ROOT).as_posix(), bytes=SOURCE.stat().st_size, sha256=SOURCE_SHA),
                  generator_sha256=sha(Path(__file__).read_bytes()),
                  tool=dict(name=tool.name, sha256=sha(tool.read_bytes()), libopus_version_reported=False))

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def run(name, argv):
        argv = list(map(str, argv))
        row = dict(name=name, argv=[tool.name, *argv], state='starting')
        report['commands'].append(row)
        save()
        with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
            child = subprocess.Popen([str(tool), *argv], stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            row.update(state='running', pid=child.pid)
            save()
            try:
                child.wait(timeout=60)
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=15)
                row.update(state='complete', exit_status=child.returncode)
        for stream in ('stdout', 'stderr'):
            row[stream + '_sha256'] = sha((out / (name + '.' + stream + '.log')).read_bytes())
        save()
        need(child.returncode == 0, 'actual FFmpeg child terminal zero: ' + name)

    try:
        run('version', ['-version'])
        run('encoder-help', ['-hide_banner', '-h', 'encoder=libopus'])
        run('source-decode', ['-nostdin', '-hide_banner', '-loglevel', 'warning', '-i', SOURCE,
            '-map', '0:a:0', '-c:a', 'pcm_s16le', '-f', 's16le', out / 'source.pcm'])
        source_pcm = (out / 'source.pcm').read_bytes()
        need(len(source_pcm) == PLAYBACK_BYTES, 'complete original 11-second source without shortening')
        report['source_pcm'] = dict(bytes=len(source_pcm), sha256=sha(source_pcm), frames=len(source_pcm)//4)
        encoded = []
        for name in ('encode', 'repeat-encode'):
            destination = out / (name + '.ogg')
            run(name, ['-nostdin', '-hide_banner', '-loglevel', 'warning', '-f', 's16le', '-ar', '48000',
                '-ac', '2', '-i', out / 'source.pcm', '-map', '0:a:0', '-map_metadata', '-1',
                '-c:a', 'libopus', '-b:a', '510k', '-vbr', 'off', '-application', 'audio',
                '-frame_duration', '120', '-fflags', '+bitexact', '-flags:a', '+bitexact', '-f', 'ogg', destination])
            encoded.append(destination.read_bytes())
        need(encoded[0] == encoded[1], 'repeated encoding with same pinned tool is byte identical')
        measured = audit(encoded[0])
        need(measured['playback_pcm16_bytes'] == PLAYBACK_BYTES and measured['maximum_packet_pcm16_bytes'] == 23040,
             'full playback timeline and deliberate output capacity boundary')
        fixture = out / 'stereo-510-120ms.ogg'
        fixture.write_bytes(encoded[0])
        run('libopus-playback', ['-nostdin', '-hide_banner', '-loglevel', 'warning', '-c:a', 'libopus',
            '-i', fixture, '-map', '0:a:0', '-c:a', 'pcm_s16le', '-f', 's16le', out / 'playback.pcm'])
        playback = (out / 'playback.pcm').read_bytes()
        need(len(playback) == PLAYBACK_BYTES, 'independent libopus wrapper playback has complete standard length')
        report.update(fixture=dict(file=fixture.name, bytes=len(encoded[0]), sha256=sha(encoded[0])),
                      audit=measured, playback=dict(bytes=len(playback), sha256=sha(playback)),
                      repeated_encoding_byte_identical=True)
        need(sha(tool.read_bytes()) == report['tool']['sha256'] and sha(SOURCE.read_bytes()) == SOURCE_SHA and
             sha(Path(__file__).read_bytes()) == report['generator_sha256'], 'generator, tool and source immutable')
        report.update(passed=True, completed=True)
        print(json.dumps(dict(passed=True, fixture=report['fixture'], audio_packets=measured['audio_packet_count'],
                             packet_pcm_bytes=23040, playback_bytes=len(playback), native_decoder_tested=False)))
    except BaseException as error:
        report.update(failure_type=type(error).__name__, failure=str(error))
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
