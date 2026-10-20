"""Complete the host-only frame proof and materialize the public raw target data."""
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
from prepare_reference import HERE, ROOT, Bits, digest, packets, patch_id, setup_summary

reference = HERE / 'reference'
original_report = json.loads((reference / 'report.json').read_text())
ffmpeg = next(Path(path) for path in original_report['tools'] if Path(path).name == 'ffmpeg.exe')
ffprobe = ffmpeg.with_name('ffprobe.exe')
report = dict(target_executed=False, production_changed=False, commands=[], generated={},
              reference_report_sha256=digest((reference / 'report.json').read_bytes()),
              reference_preparer_sha256=digest((HERE / 'prepare_reference.py').read_bytes()))


def run(name, argv):
    p = subprocess.run(list(map(str, argv)), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
    (HERE / (name + '.stdout.log')).write_bytes(p.stdout)
    (HERE / (name + '.stderr.log')).write_bytes(p.stderr)
    report['commands'].append(dict(name=name, argv=list(map(str, argv)), exit=p.returncode,
        stdout_sha256=digest(p.stdout), stderr_sha256=digest(p.stderr)))
    assert p.returncode == 0, p.stderr.decode(errors='replace')
    return p.stdout


accounting = json.loads(run('frame-accounting', [ffprobe, '-v', 'error', '-show_packets', '-show_frames',
    '-show_entries', 'packet=pts,dts,duration,flags,side_data_list:frame=pts,nb_samples', '-of', 'json',
    reference / 'long8192-rate192000.ogg']))['packets_and_frames']
frames = [x for x in accounting if x['type'] == 'frame']
packet_info = [x for x in accounting if x['type'] == 'packet']
assert len(packet_info) == 68 and len(frames) == 67
assert packet_info[0]['duration'] == 128 and frames[0]['nb_samples'] == 2112
assert [x['nb_samples'] for x in frames].count(4096) == 65
last = next(x for x in packet_info[-1]['side_data_list'] if x['side_data_type'] == 'Skip Samples')
assert last['skip_samples'] == 0 and last['discard_padding'] == 128
assert frames[-1]['nb_samples'] == 3968 and sum(x['nb_samples'] for x in frames) == 272320
report['container_accounting'] = dict(first_packet_nominal_duration=128, first_packet_pcm_frames=0,
    first_output_samples=2112, full4096_output_frames=65, final_output_samples=3968,
    skip_samples=0, final_discard_padding=128, output_samples_per_channel=272320,
    raw_complete_packet_samples_per_channel=272448,
    note='Observed final container trimming; not raw decoder output or an initial PCM skip. No Ogg API is used by the target harness.')

encoder = (reference / 'encoder-192000.ogg').read_bytes()
normal_path = HERE / 'normal2048-rate48000.ogg'
normal_path.write_bytes(patch_id(encoder, 48000))
report['normal_positive_control'] = dict(sha256=digest(normal_path.read_bytes()), decode={})
for decoder in ('vorbis', 'libvorbis'):
    pcm = HERE / ('normal2048-rate48000-%s.s16le' % decoder)
    run('normal-decode-' + decoder, [ffmpeg, '-nostdin', '-hide_banner', '-loglevel', 'warning',
        '-err_detect', 'explode', '-c:a', decoder, '-i', normal_path, '-map', '0:a:0',
        '-c:a', 'pcm_s16le', '-f', 's16le', pcm])
    data = pcm.read_bytes()
    assert len(data) > 16384 and any(data)
    report['normal_positive_control']['decode'][decoder] = dict(bytes=len(data), sha256=digest(data),
                                                               nonzero_bytes=sum(x != 0 for x in data))

values = packets((reference / 'long8192-rate192000.ogg').read_bytes())
normal_values = packets(normal_path.read_bytes())
assert [x['data'] for x in values[1:]] == [x['data'] for x in normal_values[1:]]
info = values[0]['data'][7:]
setup = values[2]['data'][7:]
summary = setup_summary(setup, 2)
mode_flags = []
offsets, audio = [0], bytearray()
for row in values[3:]:
    b = Bits(row['data'])
    assert b.get(1) == 0
    mode_flags.append(summary['modes'][b.get((len(summary['modes'])-1).bit_length())])
    audio.extend(row['data'])
    offsets.append(len(audio))
short_bits = info[21] & 15
encoder_long_bits = normal_values[0]['data'][28] >> 4
assert short_bits == 8 and encoder_long_bits == 11


def raw_sizes(long_bits):
    return [0] + [((1 << (long_bits if mode_flags[i-1] else short_bits)) +
                   (1 << (long_bits if mode_flags[i] else short_bits))) for i in range(1, len(mode_flags))]


sizes8192, sizes2048 = raw_sizes(13), raw_sizes(encoder_long_bits)
assert sum(sizes8192) == 1089792 and sizes8192.count(16384) == 66
assert sum(sizes2048) == 272640


def array(kind, name, data):
    lines = [','.join(str(x) for x in data[i:i+32]) for i in range(0, len(data), 32)]
    return 'static const ' + kind + ' ' + name + '[] = {\n' + ',\n'.join(lines) + '\n};\n'


header = '#pragma once\n#include <stdint.h>\n'
header += array('uint8_t', 'fixture_info', info)
header += array('uint8_t', 'fixture_setup', setup)
header += array('uint8_t', 'fixture_packets', audio)
header += array('uint32_t', 'fixture_offsets', offsets)
header += array('uint8_t', 'fixture_long_mode', mode_flags)
header += f'#define FIXTURE_PACKETS {len(mode_flags)}U\n#define FIXTURE_SHORT_BITS {short_bits}U\n'
header += f'#define FIXTURE_ENCODER_LONG_BITS {encoder_long_bits}U\n'
header += f'#define FIXTURE_RAW8192_BYTES {sum(sizes8192)}U\n#define FIXTURE_RAW2048_BYTES {sum(sizes2048)}U\n'
header += f'#define FIXTURE_FULL8192_PACKETS {sizes8192.count(16384)}U\n'
(HERE / 'project/main/fixture.h').write_text(header, encoding='utf-8')
shutil.copyfile(ROOT / 'tests/target/cyd_vorbis_qemu/sdkconfig.defaults', HERE / 'project/sdkconfig.defaults')
report['raw_fixture'] = dict(packets=len(mode_flags), long_mode_packets=sum(mode_flags),
    short_mode_packets=len(mode_flags)-sum(mode_flags), setup_sha256=digest(setup),
    audio_concatenated_sha256=digest(audio), full8192_pcm_packets=66,
    expected_raw8192_bytes=sum(sizes8192), expected_raw2048_bytes=sum(sizes2048))
for path in [*sorted((HERE / 'project').rglob('*')), HERE / 'finish_preparation.py']:
    if path.is_file(): report['generated'][str(path.relative_to(HERE))] = digest(path.read_bytes())
report['pins_unchanged'] = all(digest(Path(path).read_bytes()) == sha for path, sha in original_report['pins'].items())
assert report['pins_unchanged']
assert all(digest(Path(path).read_bytes()) == sha for path, sha in original_report['tools'].items())
(HERE / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(prepared=True, target_executed=False, raw_fixture=report['raw_fixture'],
                      container_accounting=report['container_accounting'])))
