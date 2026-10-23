"""Qualify captured native C3 baseline observations without starting a target."""
import hashlib,json,sys
from pathlib import Path

root=Path(__file__).resolve().parent.parent
out=root/'.build/c3-vorbis-format-baseline-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
protocol=root/'.build/c3-vorbis-format-protocol-prep-01'
assert sha(protocol/'pins.json')=='6d119f8b0b064e280ca91191142174ea771cc9021072dfdba8a311099366b667'
protocol_pins=json.loads((protocol/'pins.json').read_text())
for name,row in protocol_pins['files'].items():
    assert (protocol/name).stat().st_size==row['bytes'] and sha(protocol/name)==row['sha256'],name
assert json.loads((protocol/'host-tests.command.json').read_text())['exit_status']==0
prep=root/'.build/c3-vorbis-format-project-prep-01'
assert sha(prep/'pins.json')=='a433b95841ae724549fb845058d61da3c12b01167efa7f9ca748ed46ecca970d'
pins=json.loads((prep/'pins.json').read_text())
for row in pins['files']:
    assert (prep/row['relative']).stat().st_size==row['bytes'] and sha(prep/row['relative'])==row['sha256']
for row in pins['external_inputs']:
    assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
context=json.loads((out/'macro-context.json').read_text())
for relative,digest in context['build_outputs'].items(): assert sha(out/relative)==digest,relative
for relative,digest in context['reviewed_sources'].items(): assert sha(out/relative)==digest,relative
for name,row in context['frozen_inputs'].items(): assert sha(name)==sha(out/row['snapshot'])==row['sha256']
post=json.loads((out/'postbuild-observations.json').read_text())
for relative,digest in post['flash_inputs'].items(): assert sha(out/relative)==digest,relative
assert sha(out/'build/flasher_args.json')==post['recipe_sha256']
records={}
for name in ('setup-macros','symbols','qemu-machine-help','merge','qemu'):
    path=out/(name+'.json')
    row=json.loads(path.read_text())
    assert row['status']=='TERMINAL' and type(row['returncode']) is int and row['returncode']==0
    assert row['runner_sha256']=='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
    assert sha(row['argv'][0])==row['executable_sha256']
    for log,identity in row['logs'].items(): assert Path(log).stat().st_size==identity['bytes'] and sha(log)==identity['sha256']
    records[name]={'record':str(path.relative_to(out)),'sha256':sha(path),'returncode':row['returncode']}
qemu=json.loads((out/'qemu.json').read_text())
assert '-snapshot' in qemu['argv'] and qemu['argv'][qemu['argv'].index('-nic')+1]=='none'
assert (out/'qemu-flash.bin').stat().st_size==4194304
header=out/'sources/project/main/fixture.h'
assert sha(header)==sha(protocol/'fixture.h')=='839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
assert sha(out/'sources/project/main/main.c')==sha(protocol/'source_main.c')=='ecc9ba589a02f6587fbc2474bff510dd0eb768c84d8fbc5518a631458750b31a'
assert sha(out/'variant/vorbis_repair/setup.c')=='d9393371872a3ffb292a9693ba254a7e3c5ac8646701166f0ae7260024e5c53b'
sys.path.insert(0,str(protocol))
from c3_vorbis_format_protocol import validate_log
log=(out/'qemu.stdout.log').read_text()+'\n'+(out/'qemu.stderr.log').read_text()
observed=validate_log(log,'baseline',None,header.read_text(),returncode=qemu['returncode'],timed_out=qemu['status']!='TERMINAL')
report=dict(schema='c3-public-vorbis-format-baseline-qualification-v1',result='REGRESSION_REPRODUCED',
    completed=True,regression_reproduced=True,format_acceptance_qualified=False,passed=False,
    scope='public raw format baseline only; no radio/Ogg/reset/OOM/resource/physical qualification',
    observed=observed,exact_pair_pcm_bytes=272640+2*1089792,commands=records,
    source_pins_sha256=sha(prep/'pins.json'),protocol_pins_sha256=sha(protocol/'pins.json'),
    setup_sha256=sha(out/'variant/vorbis_repair/setup.c'),flash_sha256=sha(out/'qemu-flash.bin'),
    qualification_script_sha256=sha(__file__),target_live=False)
with (out/'baseline-qualification.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(report,indent=2)+'\n')
state_path=root/'.build/c3-vorbis-format-root-state-01.json'
state=json.loads(state_path.read_text())
state.update(target_live=False,sdk_build_completed=True,baseline_regression_reproduced=True,
             baseline_qualification=str((out/'baseline-qualification.json').relative_to(root)),
             format_acceptance_qualified=False,
             next='Fresh reviewed C3 candidate source/pins, independent acceptance and exact old-guard control; canonical C3 unchanged')
state_path.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:report[k] for k in ('result','observed','exact_pair_pcm_bytes','format_acceptance_qualified')}))
