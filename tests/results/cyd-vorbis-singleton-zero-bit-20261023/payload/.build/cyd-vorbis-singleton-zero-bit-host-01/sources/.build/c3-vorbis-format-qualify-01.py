"""Qualify captured C3 acceptance/control using native logs and actual receipts."""
import argparse,hashlib,json,re,struct,sys
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('case',choices=('acceptance','old-guard'))
args=p.parse_args()
root=Path(__file__).resolve().parent.parent
out=root/('.build/c3-vorbis-format-'+args.case+'-01')
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
protocol=root/'.build/c3-vorbis-format-protocol-prep-01'
assert sha(protocol/'pins.json')=='6d119f8b0b064e280ca91191142174ea771cc9021072dfdba8a311099366b667'
protocol_pins=json.loads((protocol/'pins.json').read_text())
for name,row in protocol_pins['files'].items():
    assert (protocol/name).stat().st_size==row['bytes'] and sha(protocol/name)==row['sha256'],name
assert json.loads((protocol/'host-tests.command.json').read_text())['exit_status']==0
candidate=args.case=='acceptance'
prep=root/('.build/c3-vorbis-format-'+('candidate' if candidate else 'project')+'-prep-01')
expected_pins='39a3a389a7263b48490043e3fc727af7f54bb3cc300eb84ceb966f97a773aeb5' if candidate else 'a433b95841ae724549fb845058d61da3c12b01167efa7f9ca748ed46ecca970d'
assert sha(prep/'pins.json')==expected_pins
pins=json.loads((prep/'pins.json').read_text())
copies={}
for row in pins['files']:
    path=prep/row['relative']
    assert path.stat().st_size==row['bytes'] and sha(path)==row['sha256']
    if row['relative'].startswith(('project/','variant/')):
        relative=('sources/' if row['relative'].startswith('project/') else '')+row['relative']
        assert sha(out/relative)==row['sha256']
        copies[relative]=row['sha256']
for row in pins['external_inputs']:
    assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
sdk_path=out/'sdk-build-result.json'
sdk=json.loads(sdk_path.read_text(encoding='utf-8-sig'))
assert sdk['status']=='TERMINAL_SUCCESS' and sdk['returncode']==0 and sdk['expected_rejection']==0
assert sdk['pins_sha256']==expected_pins and sdk['sdk_revision']==pins['sdk_revision']
for stream in ('stdout','stderr'): assert sha(out/('sdk-build.'+stream+'.log'))==sdk[stream+'_sha256']
outer_path=root/('.build/c3-vorbis-format-'+args.case+'-01-command.json')
outer=json.loads(outer_path.read_text())
assert outer['status']=='TERMINAL' and outer['returncode']==0
for name,identity in outer['logs'].items(): assert sha(name)==identity['sha256'] and Path(name).stat().st_size==identity['bytes']
context=json.loads((out/'macro-context.json').read_text())
for relative,digest in context['build_outputs'].items(): assert sha(out/relative)==digest,relative
for relative,digest in context['reviewed_sources'].items(): assert sha(out/relative)==digest,relative
for name,row in context['frozen_inputs'].items(): assert sha(name)==sha(out/row['snapshot'])==row['sha256']
post=json.loads((out/'postbuild-observations.json').read_text())
for relative,digest in post['flash_inputs'].items(): assert sha(out/relative)==digest,relative
assert sha(out/'build/flasher_args.json')==post['recipe_sha256']
records={}
for name in ('setup-macros','symbols','qemu-machine-help','merge','qemu'):
    path=out/(name+'.json'); row=json.loads(path.read_text())
    assert row['status']=='TERMINAL' and type(row['returncode']) is int and row['returncode']==0
    assert row['runner_sha256']=='33a64601d773382e748d69391eb068d7bc2b682540e3b670ddc13c0a19e22f7e'
    assert sha(row['argv'][0])==row['executable_sha256']
    for name_log,identity in row['logs'].items(): assert Path(name_log).stat().st_size==identity['bytes'] and sha(name_log)==identity['sha256']
    records[name]={'record':str(path.relative_to(out)),'sha256':sha(path),'returncode':row['returncode']}
elf=out/'build/c3_vorbis_public_format.elf'
assert struct.unpack_from('<H',elf.read_bytes(),18)[0]==243
macros=(out/'setup-macros.stdout.log').read_text()
for name,value in {'__riscv_xlen':32,'CONFIG_IDF_TARGET_ESP32C3':1,'CONFIG_FREERTOS_UNICORE':1,'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ':160,'FORMAT_EXPECT_LOW_RATE_REJECTION':0}.items():
    assert re.search(r'^#define '+name+' '+str(value)+r'$',macros,re.M)
assert not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M)
qemu=json.loads((out/'qemu.json').read_text())
assert '-snapshot' in qemu['argv'] and qemu['argv'][qemu['argv'].index('-nic')+1]=='none'
assert (out/'qemu-flash.bin').stat().st_size==4194304
header=out/'sources/project/main/fixture.h'
assert sha(header)==sha(protocol/'fixture.h')=='839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
assert sha(out/'sources/project/main/main.c')==sha(protocol/'source_main.c')=='ecc9ba589a02f6587fbc2474bff510dd0eb768c84d8fbc5518a631458750b31a'
sys.path.insert(0,str(protocol))
from c3_vorbis_format_protocol import validate_log
log=(out/'qemu.stdout.log').read_text()+'\n'+(out/'qemu.stderr.log').read_text()
observed=validate_log(log,'acceptance',None if candidate else 'old-guard',header.read_text(),returncode=qemu['returncode'],timed_out=qemu['status']!='TERMINAL')
report=dict(schema='c3-public-vorbis-format-qualification-v1',result='FORMAT_ACCEPTED' if candidate else 'CONTROL_EFFECTIVE',
    completed=True,regression_reproduced=False,format_acceptance_qualified=candidate,passed=candidate,
    control_effective=not candidate,scope='acceptance',control=None if candidate else 'old-guard',
    qualification_scope='public raw format only; no radio/Ogg/reset/OOM/resource/physical qualification',
    observed=observed,exact_pair_pcm_bytes=272640+(4 if candidate else 2)*1089792,commands=records,
    source_pins_sha256=sha(prep/'pins.json'),protocol_pins_sha256=sha(protocol/'pins.json'),
    sdk_build_receipt_sha256=sha(sdk_path),sdk_outer_receipt_sha256=sha(outer_path),source_copies=copies,
    setup_sha256=sha(out/'variant/vorbis_repair/setup.c'),flash_sha256=sha(out/'qemu-flash.bin'),elf_machine=243,
    qualification_script_sha256=sha(__file__),target_live=False)
with (out/'qualification.json').open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('result','observed','exact_pair_pcm_bytes','format_acceptance_qualified')}))
