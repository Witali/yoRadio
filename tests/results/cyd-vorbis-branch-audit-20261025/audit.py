"""Read every branch tip without checkout; record Ogg/Vorbis source families."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent.parent
out = root / '.build/cyd-vorbis-branches-20261025-01'
out.mkdir()
def git(*args):
    return subprocess.run(['git', '-c', 'core.longpaths=true', *args], cwd=root,
                          check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=90).stdout

rows = []
for line in git('for-each-ref', '--format=%(refname)|%(objectname)|%(symref)', 'refs/heads', 'refs/remotes').decode().splitlines():
    ref, oid, symbolic = line.split('|')
    if not symbolic:
        rows.append({'ref': ref, 'oid': oid})
oids = sorted({row['oid'] for row in rows})
source_name = re.compile(r'vorbis|oggdecoder|ivorbis|libogg|(?:^|/)(?:framing|synthesis|mdct|res012|res0)\.[ch]$', re.I)
selected = {
    'cyd_audio': 'idf/esp32-cyd2usb-native/main/audio_service.c',
    'cyd_registration': 'idf/esp32-cyd2usb-native/main/decoder_registration.c',
    'cyd_defaults': 'idf/esp32-cyd2usb-native/sdkconfig.defaults',
    'cyd_cmake': 'idf/esp32-cyd2usb-native/main/CMakeLists.txt',
    'c3_audio': 'idf/esp32c3-oled-native/main/audio_service.c',
    'c3_defaults': 'idf/esp32c3-oled-native/sdkconfig.defaults',
    'c3_cmake': 'idf/esp32c3-oled-native/main/CMakeLists.txt',
    'arduino_ogg': 'yoRadio/src/audioI2S/OggDecoder.cpp',
    'arduino_audio': 'yoRadio/src/audioI2S/Audio.cpp',
    'minimal_cmake': 'idf/esp32-cyd2usb-minimal/main/CMakeLists.txt',
    'minimal_defaults': 'idf/esp32-cyd2usb-minimal/sdkconfig.defaults',
}
def inspect(oid):
    entries = {}
    for row in git('ls-tree', '-rz', oid).split(b'\0'):
        if not row:
            continue
        header, path = row.split(b'\t', 1)
        mode, kind, blob = header.decode().split(' ')
        if kind == 'blob':
            entries[path.decode('utf-8')] = blob
    chosen = {key: {'path': path, 'blob': entries[path]} for key, path in selected.items() if path in entries}
    sources = {path: blob for path, blob in entries.items()
               if source_name.search(path) and path.lower().endswith(('.c', '.cpp', '.h', '.s'))
               and not path.startswith(('tests/', 'docs/', 'firmware/'))}
    return oid, {'selected': chosen, 'codec_sources': sources, 'tracked_files': len(entries)}

with ThreadPoolExecutor(max_workers=4) as pool:
    snapshots = dict(pool.map(inspect, oids))

blobs = {}
for snapshot in snapshots.values():
    for item in snapshot['selected'].values():
        blob = item['blob']
        if blob not in blobs:
            body = git('cat-file', 'blob', blob)
            blobs[blob] = body.decode('utf-8', errors='replace')
            (out / 'blobs').mkdir(exist_ok=True)
            (out / 'blobs' / blob).write_bytes(body)
    def content(key):
        return blobs[snapshot['selected'][key]['blob']] if key in snapshot['selected'] else ''
    snapshot['features'] = {
        'native_cyd_ogg_dispatch': 'ESP_AUDIO_SIMPLE_DEC_TYPE_OGG' in content('cyd_audio'),
        'native_cyd_decode_process': 'esp_audio_simple_dec_process' in content('cyd_audio'),
        'native_cyd_vorbis_enabled': 'CONFIG_AUDIO_DECODER_VORBIS_SUPPORT=y' in content('cyd_defaults'),
        'native_cyd_ogg_enabled': 'CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y' in content('cyd_defaults'),
        'native_c3_ogg_dispatch': 'ESP_AUDIO_SIMPLE_DEC_TYPE_OGG' in content('c3_audio'),
        'native_c3_vorbis_enabled': 'CONFIG_AUDIO_DECODER_VORBIS_SUPPORT=y' in content('c3_defaults'),
        'native_c3_ogg_enabled': 'CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y' in content('c3_defaults'),
        'minimal_vorbis_enabled': 'CONFIG_AUDIO_DECODER_VORBIS_SUPPORT=y' in content('minimal_defaults'),
        'minimal_ogg_enabled': 'CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y' in content('minimal_defaults'),
        'arduino_espressif_adapter': 'ESP_AUDIO_SIMPLE_DEC_TYPE_OGG' in content('arduino_ogg'),
    }
for row in rows:
    row['features'] = snapshots[row['oid']]['features']
report = {'created_utc': datetime.now(timezone.utc).isoformat(), 'refs': rows, 'snapshots': snapshots,
          'counts': {'local': sum(r['ref'].startswith('refs/heads/') for r in rows),
                     'remote': sum(r['ref'].startswith('refs/remotes/') for r in rows),
                     'unique_tips': len(oids), 'selected_blobs': len(blobs)},
          'source_only': True, 'runtime_executed': False}
(out / 'inventory.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(out / 'audit.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(report['counts']))
families = {}
for oid, snapshot in snapshots.items():
    key = tuple((name, item['blob']) for name, item in sorted(snapshot['selected'].items()))
    families.setdefault(key, []).extend(r['ref'] for r in rows if r['oid'] == oid)
print(json.dumps({'integration_source_families': len(families),
                  'feature_ref_counts': {key: sum(r['features'][key] for r in rows) for key in next(iter(snapshots.values()))['features']}}))
