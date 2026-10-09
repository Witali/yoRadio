"""Prepare a matched 0/4/4/0 switching comparison from the audited controller."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
prior=Path('tests/results/esp32c3-flac-input-growth-20261009')
source=prior/'physical.py'
text=source.read_text()
text=text.replace('Matched FLAC queue growth A/B/A, switching and AAC TLS recovery.',
                  'Matched 0/4/4/0 switching, EOF and HE-AACv2 TLS comparison.')
text=text.replace('.build/c3-flac-input-growth-20261009','.build/c3-switch-capacity-control-20261009')
start=text.index("    for label,variant in (('flac-control-before'")
end=text.index("    save('settings-after-tests.json'",start)
text=text[:start]+"""    for trial,variant in (('control-1','0'),('expanded-1','4'),('expanded-2','4'),('control-2','0')):
        activate(variant,trial)
        run_phase(trial+'-switch',variant,'switch',['--case','flac-level8',
            '--case','he-48000-stereo','--case','hev2-44100-stereo','--cycles','3'],timeout=210)
        run_phase(trial+'-eof',variant,'eof',['--case','flac-level8','--case','hev2-44100-stereo',
            '--eof-protocol','https',*tls],timeout=240)
        run_phase(trial+'-records',variant,None,[],timeout=165,records=True)
"""+text[end:]
compile(text,str(ROOT/'physical.py'),'exec')
(ROOT/'physical.py').write_text(text)
for name in ('build-audit.json','case-catalog.json'):(ROOT/name).write_bytes((prior/name).read_bytes())
# Source identity is inherited from a committed byte-exact archive; do not
# duplicate all codec/font sources in every follow-up.
references={prior.as_posix():dict(index_sha256=hashlib.sha256((prior/'index.json').read_bytes()).hexdigest())}
(ROOT/'references.json').write_text(json.dumps(references,indent=2)+'\n')
for directory in ('tools/esp32c3_tests','tools/audio_test_server'):
    for path in Path(directory).glob('*.py'):
        expected=json.loads((prior/'sources.json').read_text())[path.as_posix()]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,path
print('Prepared four matched boot sequences and protected restoration')
