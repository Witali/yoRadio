"""Host-only format fixture preparation. Never builds firmware or runs a target."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from vorbis_packets import packets
from run_vorbis_lifecycle import ogg_crc  # Pure CRC function only; no lifecycle runs.


class Bits:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def get(self, n):
        if n < 0 or self.pos + n > len(self.data) * 8:
            raise ValueError('truncated setup')
        value = 0
        for shift in range(n):
            value |= ((self.data[self.pos // 8] >> (self.pos % 8)) & 1) << shift
            self.pos += 1
        return value

    def skip(self, n):
        if n < 0 or self.pos + n > len(self.data) * 8:
            raise ValueError('truncated setup lookup')
        self.pos += n


def setup_summary(data, channels):
    """Read public Vorbis I setup fields, not any decoder state/layout."""
    b = Bits(data)
    books = b.get(8) + 1
    for _ in range(books):
        assert b.get(24) == 0x564342
        dim, entries = b.get(16), b.get(24)
        assert dim and entries
        if b.get(1):
            length, current = b.get(5) + 1, 0
            while current < entries:
                assert length <= 32
                count = b.get((entries - current).bit_length())
                assert current + count <= entries
                current += count
                length += 1
        else:
            sparse = b.get(1)
            for _ in range(entries):
                if not sparse or b.get(1):
                    b.get(5)
        lookup = b.get(4)
        assert lookup <= 2
        if lookup:
            b.get(32); b.get(32)
            width = b.get(4) + 1
            b.get(1)
            if lookup == 1:
                lo, hi = 1, entries + 1
                while hi - lo > 1:
                    mid = (hi + lo) // 2
                    if mid ** dim <= entries: lo = mid
                    else: hi = mid
                count = lo
            else:
                count = entries * dim
            b.skip(count * width)
    for _ in range(b.get(6) + 1):
        assert b.get(16) == 0
    floors = []
    floor_count = b.get(6) + 1
    for _ in range(floor_count):
        kind = b.get(16)
        floors.append(kind)
        assert kind == 1, 'Fixture must use floor1 only; rate independence is not assumed for floor0'
        classes = [b.get(4) for _ in range(b.get(5))]
        dimensions = []
        for _ in range(max(classes, default=-1) + 1):
            dimensions.append(b.get(3) + 1)
            subclasses = b.get(2)
            if subclasses: assert b.get(8) < books
            for _ in range(1 << subclasses):
                book = b.get(8) - 1
                assert book < books
        b.get(2)
        width = b.get(4)
        for cls in classes:
            for _ in range(dimensions[cls]): b.get(width)
    residue_count = b.get(6) + 1
    residues = []
    for _ in range(residue_count):
        kind, begin, end = b.get(16), b.get(24), b.get(24)
        assert kind <= 2 and begin <= end
        partition, classes, book = b.get(24) + 1, b.get(6) + 1, b.get(8)
        assert book < books
        cascades = []
        for _ in range(classes):
            low = b.get(3)
            high = b.get(5) if b.get(1) else 0
            cascades.append(low | (high << 3))
        for cascade in cascades:
            for bit in range(8):
                if cascade & (1 << bit): assert b.get(8) < books
        residues.append(dict(type=kind, begin=begin, end=end, partition=partition))
    mappings = b.get(6) + 1
    for _ in range(mappings):
        assert b.get(16) == 0
        submaps = b.get(4) + 1 if b.get(1) else 1
        if b.get(1):
            for _ in range(b.get(8) + 1):
                magnitude, angle = b.get((channels - 1).bit_length()), b.get((channels - 1).bit_length())
                assert magnitude != angle and magnitude < channels and angle < channels
        assert b.get(2) == 0
        if submaps > 1:
            for _ in range(channels): assert b.get(4) < submaps
        for _ in range(submaps):
            assert b.get(8) == 0
            assert b.get(8) < floor_count
            assert b.get(8) < residue_count
    modes = []
    for _ in range(b.get(6) + 1):
        long = b.get(1)
        assert b.get(16) == b.get(16) == 0
        assert b.get(8) < mappings
        modes.append(long)
    assert b.get(1) == 1
    assert b.get(len(data) * 8 - b.pos) == 0
    return dict(codebooks=books, floors=floors, residues=residues, modes=modes)


def patch_id(source, rate, long_bits=None):
    """Alter identification fields only and repair affected Ogg page CRC."""
    data = bytearray(source)
    assert data[:4] == b'OggS' and data[5] & 2
    count = data[26]
    start = 27 + count
    end = start + sum(data[27:start])
    assert data[27] == 30 and data[start:start+7] == b'\x01vorbis'
    struct.pack_into('<I', data, start + 12, rate)
    if long_bits is not None:
        data[start + 28] = (long_bits << 4) | (data[start + 28] & 15)
    data[22:26] = bytes(4)
    struct.pack_into('<I', data, 22, ogg_crc(data[:end]))
    return bytes(data)


def digest(data): return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--ffmpeg', type=Path, required=True)
    p.add_argument('--ffprobe', type=Path, required=True)
    args = p.parse_args()
    out = HERE / 'reference'
    out.mkdir(exist_ok=False)
    report = dict(target_executed=False, production_changed=False, commands=[], tools={}, pins={})
    for tool in (args.ffmpeg, args.ffprobe, Path(sys.executable)):
        report['tools'][str(tool.resolve())] = digest(tool.read_bytes())
    names = [
        'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c',
        'idf/esp32-cyd2usb-native/main/vorbis_repair/output.c',
        'idf/esp32-cyd2usb-native/main/vorbis_repair/simple.c',
        'idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h',
        'idf/esp32-cyd2usb-native/main/compat/vorbis_repair/enable.cmake',
        'tests/run-cyd-vorbis-qemu.py', 'tools/codec_benchmark/vorbis_packets.py',
        'tools/codec_benchmark/run_vorbis_lifecycle.py',
        'tests/fixtures/esp32c3_calibration/vorbis-q10.ogg',
    ]
    names += [str(ROOT.parents[1] / '.idf/esp-adf-libs/esp_audio_codec' / tail) for tail in (
        'lib/esp32/libesp_audio_codec.a', 'lib/esp32/libesp_audio_simple_dec.a',
        'include/decoder/impl/esp_vorbis_dec.h', 'include/decoder/esp_audio_dec.h')]
    report['pins'] = {str((ROOT / name).resolve()): digest((ROOT / name).read_bytes()) for name in names}
    save = lambda: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    def run(name, argv):
        proc = subprocess.run(list(map(str, argv)), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        (out / (name + '.stdout.log')).write_bytes(proc.stdout)
        (out / (name + '.stderr.log')).write_bytes(proc.stderr)
        report['commands'].append(dict(name=name, argv=list(map(str, argv)), exit=proc.returncode,
                                       stdout_sha256=digest(proc.stdout), stderr_sha256=digest(proc.stderr)))
        save()
        assert proc.returncode == 0, (name, proc.stderr.decode(errors='replace'))
        return proc.stdout
    run('ffmpeg-version', [args.ffmpeg, '-version'])
    run('ffprobe-version', [args.ffprobe, '-version'])
    run('decoders', [args.ffmpeg, '-hide_banner', '-decoders'])
    encoded = out / 'encoder-192000.ogg'
    run('encode', [args.ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'warning', '-f', 'lavfi', '-i',
        'aevalsrc=0.28*sin(2*PI*997*t)+0.17*sin(2*PI*3821*t)|0.31*sin(2*PI*1601*t)+0.13*sin(2*PI*6127*t):s=192000:d=0.35',
        '-map_metadata', '-1', '-c:a', 'libvorbis', '-q:a', '4', '-f', 'ogg', str(encoded)])
    source = encoded.read_bytes()
    original_packets = packets(source)
    original_id = original_packets[0]['data']
    summary = setup_summary(original_packets[2]['data'][7:], original_id[11])
    short_bits, original_long = original_id[28] & 15, original_id[28] >> 4
    report['encoder_identification'] = dict(rate=struct.unpack_from('<I', original_id, 12)[0],
        channels=original_id[11], short=1 << short_bits, long=1 << original_long)
    report['setup'] = summary
    audio = [x['data'] for x in original_packets[3:]]
    flags = []
    for packet in audio:
        b = Bits(packet)
        assert b.get(1) == 0
        mode = b.get((len(summary['modes']) - 1).bit_length())
        assert mode < len(summary['modes'])
        flags.append(summary['modes'][mode])
        if flags[-1]: b.get(1); b.get(1)
    assert sum(flags) > 2, 'Must decode real long-mode audio packets'
    report['audio_packets'] = dict(count=len(audio), long_modes=sum(flags), short_modes=len(flags)-sum(flags),
        concatenated_sha256=digest(b''.join(audio)))
    # The encoder's Ogg terminal granule describes its original MDCT size. A larger
    # legal MDCT changes natural raw sample counts. Remove only that final crop by
    # setting its granule to the actual public block-overlap accounting below.
    raw_samples = sum(((1 << (13 if flags[i-1] else short_bits)) +
                       (1 << (13 if flags[i] else short_bits))) // 4 for i in range(1, len(flags)))
    fixture_source = bytearray(source)
    pos = 0
    while pos < len(fixture_source):
        count = fixture_source[pos+26]
        end = pos + 27 + count + sum(fixture_source[pos+27:pos+27+count])
        if fixture_source[pos+5] & 4:
            struct.pack_into('<q', fixture_source, pos+6, raw_samples)
            fixture_source[pos+22:pos+26] = bytes(4)
            struct.pack_into('<I', fixture_source, pos+22, ogg_crc(fixture_source[pos:end]))
        pos = end
    report['fixture_construction'] = dict(encoder_natural_8192=original_long == 13,
        long_exponent_edit=original_long != 13, eos_granule=raw_samples,
        note='Encoder source remains separate; setup and every audio packet are unchanged. All rate variants share identical pages except identification sample-rate and that page CRC.')
    expected_pcm = {}
    report['variants'] = {}
    for rate in (192000, 64000, 63999, 48000):
        path = out / ('long8192-rate%d.ogg' % rate)
        data = patch_id(fixture_source, rate, 13)
        path.write_bytes(data)
        values = packets(data)
        assert values[1:] == packets(bytes(fixture_source))[1:]
        assert values[2]['data'] == original_packets[2]['data']
        assert [v['data'] for v in values[3:]] == audio
        info = run('probe-%d' % rate, [args.ffprobe, '-v', 'error', '-show_entries',
            'stream=codec_name,sample_rate,channels:format=duration', '-of', 'json', path])
        assert json.loads(info)['streams'][0]['sample_rate'] == str(rate)
        variant = dict(sha256=digest(data), size=len(data), decode={})
        report['variants'][str(rate)] = variant
        for decoder in ('vorbis', 'libvorbis'):
            pcm = out / ('long8192-rate%d-%s.s16le' % (rate, decoder))
            run('decode-%d-%s' % (rate, decoder), [args.ffmpeg, '-nostdin', '-hide_banner', '-loglevel',
                'warning', '-err_detect', 'explode', '-c:a', decoder, '-i', path, '-map', '0:a:0',
                '-c:a', 'pcm_s16le', '-f', 's16le', pcm])
            decoded = pcm.read_bytes()
            assert len(decoded) > 16384 and any(decoded)
            if decoder not in expected_pcm: expected_pcm[decoder] = decoded
            assert decoded == expected_pcm[decoder], 'Rate-only variants must decode byte-exact within the same independent decoder'
            variant['decode'][decoder] = dict(bytes=len(decoded), samples_per_channel=len(decoded)//4,
                                             sha256=digest(decoded), nonzero_bytes=sum(x != 0 for x in decoded))
    report['host_reference_complete'] = True
    report['cross_decoder_pcm_exact_required'] = False
    report['target_vendor_high8192_acceptance'] = 'PENDING: no SDK build or target execution authorized in this preparation'
    report['current_pins_unchanged'] = all(digest(Path(path).read_bytes()) == sha for path, sha in report['pins'].items())
    assert report['current_pins_unchanged']
    save()
    print(json.dumps(dict(reference_complete=True, output=str(out), encoder=report['encoder_identification'],
        audio_packets=report['audio_packets'], raw_samples=raw_samples,
        pcm={decoder:dict(bytes=len(value), sha256=digest(value)) for decoder,value in expected_pcm.items()})))


if __name__ == '__main__':
    main()
