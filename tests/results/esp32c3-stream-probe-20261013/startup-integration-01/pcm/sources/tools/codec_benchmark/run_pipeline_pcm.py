"""Compare real C3 mixed-codec PCM against independently decoded segments in QEMU.

Uses the benchmark flash input and production decoder/PCM queue/output task.
The test-only output sink captures before resampling/gain/DMA, without timing claims.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from audio_test_server.fixtures import load_fixtures

CAPTURE = re.compile(r'PIPE_PCM seq=(\d+) offset=(\d+) rate=(\d+) channels=(\d+) hex=([0-9a-f]+)')
END = re.compile(r'PIPE_PCM_END generation=(\d+) bytes=(\d+) chunks=(\d+) flushes=(\d+)')
FIXTURE_PACKETS = 64
# These corpus files are MPEG-1 Layer III, AAC-LC and full-rate HE-AAC/HE-AACv2.
PCM_FRAMES_PER_PACKET = {'mp3-320': 1152, 'lc-48000-stereo': 1024,
                         'he-48000-stereo': 2048, 'hev2-44100-stereo': 2048}


def canonical(parts):
    """Join adjacent same-layout spans; packet sizes are not PCM boundaries."""
    result = []
    for rate, channels, pcm in parts:
        if result and result[-1][:2] == (rate, channels):
            result[-1][2].extend(pcm)
        else:
            result.append((rate, channels, bytearray(pcm)))
    return [(r, c, bytes(p)) for r, c, p in result]


def parse_capture(log):
    if re.search(r'assert failed|Guru Meditation|CORRUPT HEAP|decode failed|decode error|allocation failed|buffer stalled|decoder made no input progress', log):
        raise ValueError('Runtime failure in capture')
    parts = []; count = size = terminals = 0
    for line in log.splitlines():
        if line.startswith('PIPE_PCM '):
            m = CAPTURE.fullmatch(line)
            if not m or terminals:
                raise ValueError('Malformed or post-terminal PCM')
            sequence, offset, rate, channels = map(int, m.groups()[:4])
            pcm = bytes.fromhex(m[5])
            if (sequence != count or offset != size or not 8000 <= rate <= 192000
                    or channels not in (1, 2) or not 0 < len(pcm) <= 128
                    or len(pcm) % (channels * 2)):
                raise ValueError('Missing, reordered or invalid PCM span')
            parts.append((rate, channels, pcm)); count += 1; size += len(pcm)
        elif line.startswith('PIPE_PCM_END'):
            m = END.fullmatch(line)
            if not m or int(m[1]) == 0 or terminals or tuple(map(int, m.groups()[1:])) != (size, count, 1) or not size:
                raise ValueError('Missing PCM or invalid EOF counts')
            terminals += 1
    if terminals != 1 or not any(any(pcm) for _, _, pcm in parts):
        raise ValueError('Incomplete or entirely silent capture')
    return canonical(parts)


def describe(candidate):
    return dict(bytes=sum(len(pcm) for _, _, pcm in candidate),
                layouts=[dict(rate=r, channels=c, bytes=len(p), sha256=hashlib.sha256(p).hexdigest())
                         for r, c, p in canonical(candidate)])


def compare(reference, candidate):
    if canonical(reference) != canonical(candidate):
        raise ValueError('PCM samples, order, length or layout differ')
    return dict(exact=True, **describe(candidate))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--qemu', required=True, help='WSL path to Espressif RISC-V QEMU')
    p.add_argument('--bios', required=True, help='WSL QEMU firmware directory')
    a = p.parse_args(); a.build = a.build.resolve(); a.output = a.output.resolve()
    a.output.mkdir(parents=True, exist_ok=False)
    cfg = (a.build / 'sdkconfig').read_text()
    for setting in ('CONFIG_YORADIO_QEMU=y', 'CONFIG_YORADIO_FRAME_ROUTER=y',
                    'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions-codec-benchmark.csv"'):
        if setting not in cfg: raise ValueError('Wrong capture configuration: ' + setting)
    cache = (a.build / 'CMakeCache.txt').read_text()
    for option in ('YORADIO_QEMU_PIPELINE_PCM_TEST', 'YORADIO_CODEC_BENCHMARK'):
        if not re.search(r'^'+option+r':[^=]+=ON$', cache, re.M):
            raise ValueError('Missing test-only CMake option: ' + option)
    report = dict(scope=__doc__, cases={}, fixtures={},
        app_sha256=hashlib.sha256((a.build/'yoradio_esp32c3_oled_native.bin').read_bytes()).hexdigest(),
        sdkconfig_sha256=hashlib.sha256((a.build/'sdkconfig').read_bytes()).hexdigest(),
        ffprobe=subprocess.check_output(['ffprobe','-version'],text=True).splitlines()[0])
    sources = [Path(__file__).resolve(), ROOT/'tests/native/qemu_pipeline_pcm_capture.c']
    sources += [ROOT/'idf/esp32c3-oled-native/main'/name for name in
                ('CMakeLists.txt','audio_service.c','stream_probe.h','stream_frames.h',
                 'stream_tags.h','stream_encoded_router.h','native_aac_decoder.c','audio_completion.h',
                 'stream_start.h','stream_staging.h','stream_confirm.h','adaptive_input.c','adaptive_input.h')]
    report['startup_confirmation'] = 'CONFIG_YORADIO_STREAM_CONFIRM=y' in cfg
    report['source_sha256'] = {s.relative_to(ROOT).as_posix(): hashlib.sha256(s.read_bytes()).hexdigest()
                               for s in sources}
    def save():
        (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    flash = a.output/'flash.bin'
    merge = [sys.executable,'-m','esptool','--chip','esp32c3','merge-bin','-o',str(flash),
             '--flash-mode','dio','--flash-freq','80m','--flash-size','4MB','--pad-to-size','4MB']
    for offset, name in [('0x0','bootloader/bootloader.bin'),('0x8000','partition_table/partition-table.bin'),
                         ('0x10000','yoradio_esp32c3_oled_native.bin')]:
        merge += [offset,str(a.build/name)]
    (a.output/'merge.log').write_bytes(subprocess.check_output(merge,stderr=subprocess.STDOUT))
    guest = subprocess.check_output(['wsl.exe','--exec','wslpath','-a',str(a.output)],text=True).strip()
    command = ['wsl.exe','--exec','timeout','--kill-after=2','240',a.qemu,'-M','esp32c3',
        '-nographic','-no-reboot','-snapshot','-icount','shift=0,align=off,sleep=off',
        '-L',a.bios,'-drive',f'file={guest}/flash.bin,if=mtd,format=raw']
    report['command'] = command
    def capture(name, data):
        report['fixtures'][name] = dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        if not 0 < len(data) + 16 <= 0x220000: raise ValueError('Fixture exceeds partition')
        with flash.open('r+b') as f:
            f.seek(0x190000); f.write(struct.pack('<4I',0x59434658,0,len(data),0)+data)
        log_path = a.output/(name+'.log')
        with log_path.open('wb') as log:
            run = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,timeout=250)
        if run.returncode: raise ValueError('QEMU failed: '+name)
        text = log_path.read_text(errors='strict')
        if f'Codec fixture complete: {len(data)}/{len(data)} bytes' not in text:
            raise ValueError('Incomplete encoded delivery: '+name)
        result = parse_capture(text)
        (a.output/(name+'.pcm.gz')).write_bytes(gzip.compress(b''.join(p for _,_,p in result),mtime=0))
        report['cases'][name] = dict(captured=True, **describe(result)); save()
        print('CAPTURE',name,report['cases'][name]['bytes'],flush=True)
        return result
    try:
        fixtures = load_fixtures(); segments = {}; references = {}
        for name in ('mp3-320','lc-48000-stereo','he-48000-stereo','hev2-44100-stereo'):
            data = fixtures[name]['data']
            raw = subprocess.run(['ffprobe','-v','error','-show_packets','-show_entries',
                'packet=pos,size','-of','json','-i','pipe:0'],input=data,capture_output=True,check=True)
            packets = json.loads(raw.stdout)['packets']
            if len(packets) < FIXTURE_PACKETS: raise ValueError('Fixture too short')
            last = packets[FIXTURE_PACKETS - 1]
            end = int(last['pos']) + int(last['size'])
            segments[name] = data[:end]
            references[name] = capture(name,segments[name])
            expected_bytes = FIXTURE_PACKETS * PCM_FRAMES_PER_PACKET[name] * fixtures[name]['channels'] * 2
            shape = [(r,c,len(p)) for r,c,p in references[name]]
            if shape != [(fixtures[name]['rate'], fixtures[name]['channels'], expected_bytes)]:
                raise ValueError('Reference lost samples or has wrong PCM layout: '+name)
            report['cases'][name]['reference_shape_verified'] = True
        if report['startup_confirmation']:
            for name, prefix, target in (
                ('false-mp3-before-he-aac', b'\xff\xfb\x90\0'+bytes(28), 'he-48000-stereo'),
                ('false-aac-before-mp3', b'\xff\xf1\x4c\x80\x01\x9f\xfc'+bytes(25), 'mp3-320'),
            ):
                observed = capture(name, prefix+segments[target])
                report['cases'][name] = compare(references[target], observed); save()
                print('EXACT', name, flush=True)
        # ID3v1/v1.1 is metadata after a complete MP3 stream/track. Include
        # sync-shaped values to ensure none of its 128 bytes reach a decoder.
        mp3_tail = b'TAG' + (b'ID3\xff\xfb\x90\x00\xff\xf1' * 14)[:125].ljust(125,b'\0')
        observed = capture('id3v1-mp3', segments['mp3-320'] + mp3_tail)
        report['cases']['id3v1-mp3'] = compare(references['mp3-320'], observed); save()
        print('EXACT id3v1-mp3', flush=True)
        for sequence in [('mp3-320','he-48000-stereo','mp3-320'),
                         ('lc-48000-stereo','mp3-320','hev2-44100-stereo')]:
            expected = [part for name in sequence for part in references[name]]
            for tagged in (False, True):
                name = ('tagged-' if tagged else 'mixed-') + '-'.join(sequence)
                tag = b'ID3\x04\x00\x00\x00\x00\x00\x08'+b'\xff\xfb\x90\x00'*2 if tagged else b''
                observed = capture(name,b''.join(tag+segments[n] for n in sequence))
                report['cases'][name] = compare(expected,observed); save()
                print('EXACT',name,flush=True)
            name = 'id3v1-' + '-'.join(sequence)
            observed = capture(name, b''.join(segments[n] + (mp3_tail if n == 'mp3-320' else b'')
                                             for n in sequence))
            report['cases'][name] = compare(expected, observed); save()
            print('EXACT', name, flush=True)
        report['passed'] = True
    except Exception as error:
        report['passed'] = False; report['error'] = str(error); raise
    finally:
        save()


if __name__ == '__main__': main()
