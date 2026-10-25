"""Publish the source-only branch inventory and explicit ancestry queries."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parent.parent
source = root / '.build/cyd-vorbis-branches-20261025-01'
out = root / 'tests/results/cyd-vorbis-branch-audit-20261025'
out.mkdir(parents=True)
report = json.loads((source / 'inventory.json').read_bytes())
for snapshot in report['snapshots'].values():
    for key in ('cyd_defaults', 'c3_defaults', 'minimal_defaults'):
        if key not in snapshot['selected']:
            continue
        text = (source / 'blobs' / snapshot['selected'][key]['blob']).read_text(encoding='utf-8')
        prefix = {'cyd_defaults': 'native_cyd', 'c3_defaults': 'native_c3', 'minimal_defaults': 'minimal'}[key]
        for feature, setting in (('vorbis', 'CONFIG_AUDIO_DECODER_VORBIS_SUPPORT'),
                                 ('ogg', 'CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT')):
            assert snapshot['features'][prefix + '_' + feature + '_enabled'] == bool(re.search('^' + setting + '=y$', text, re.M))

queries = [
    ['log', '--all', '--not', 'HEAD', '--regexp-ignore-case', '--extended-regexp', '--grep=ogg|vorbis', '--format=%H|%s'],
    ['log', '--all', '--not', 'HEAD', '--format=%H|%s', '--',
     'yoRadio/src/audioI2S/OggDecoder.cpp', 'yoRadio/src/audioI2S/OggDecoder.h',
     'idf/esp32-cyd2usb-native/main/vorbis_repair', 'idf/esp32c3-oled-native/main/vorbis_repair'],
]
answers = []
for query in queries:
    result = subprocess.run(['git', '-c', 'core.longpaths=true', *query], cwd=root,
                            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    assert not result.stdout and not result.stderr
    answers.append({'argv': ['git', '-c', 'core.longpaths=true', *query], 'exit_status': result.returncode,
                    'stdout': '', 'stderr': ''})
report['ancestry_queries'] = answers
report['scope'] = 'All local and remote branch tips after successful fetch of both remotes; static source/configuration/ancestry evidence only. No build, decode, conformance or physical playback execution.'
(out / 'inventory.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
stream = io.StringIO(newline='')
columns = ['ref', 'oid', *next(iter(report['snapshots'].values()))['features']]
writer = csv.DictWriter(stream, fieldnames=columns, lineterminator='\n')
writer.writeheader()
for row in report['refs']:
    writer.writerow({'ref': row['ref'], 'oid': row['oid'], **row['features']})
(out / 'branches.csv').write_text(stream.getvalue(), encoding='utf-8', newline='')
(out / 'audit.py').write_bytes((source / 'audit.py').read_bytes())
(out / 'save.py').write_bytes(Path(__file__).read_bytes())
(out / '.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof\n', encoding='ascii')
pins = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in out.iterdir() if path.is_file() and path.name != 'identity.json'}
(out / 'identity.json').write_text(json.dumps(pins, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'saved': True, **report['counts'], 'missing_topic_or_decoder_path_commits': 0}))
