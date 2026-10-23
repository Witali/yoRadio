"""Assemble one fresh isolated raw-only CYD block-matrix proposal; no tools run."""
import hashlib, json, shutil, difflib
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'.build/cyd-vorbis-block-sdk-prep-01'
PROPOSAL=ROOT/'.build/cyd-vorbis-block-target-prep-01'
BANKS=ROOT/'.build/cyd-vorbis-block-banks-01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(PROPOSAL/'pins.json')=='8a8ac8f58e78412675db9af258444001ad4aa0d4ba769e143f33c96e83c285d2'
for row in json.loads((PROPOSAL/'pins.json').read_text())['files']:
    assert sha(PROPOSAL/row['relative'])==row['sha256']
assert sha(BANKS/'banks.json')=='efd24b5bc251c18be3cd00ce743a2366be0dfe9c1b2aff211fed89480dff96d9'
assert sha(BANKS/'banks_data.h')=='037e21071bde6702d8a55d8bc723961d3f1759519849439b33bf63ea69962c7e'
OUT.mkdir(exist_ok=False)
PROJECT=OUT/'target/cyd_vorbis_blocks_qemu'
(PROJECT/'main').mkdir(parents=True)
base=ROOT/'tests/target/cyd_vorbis_format_qemu'
for name in ('CMakeLists.txt','sdkconfig.defaults','partitions.csv','main/Kconfig.projbuild'):
    shutil.copyfile(base/name,PROJECT/name)
for name in ('main.c','banks_contract.h'):
    shutil.copyfile(PROPOSAL/'project/main'/name,PROJECT/'main'/name)
shutil.copyfile(BANKS/'banks_data.h',PROJECT/'main/banks_data.h')
for name in ('banks.json','freeze.json'):
    shutil.copyfile(BANKS/name,PROJECT/name)
proofs=PROJECT/'proofs';proofs.mkdir()
for src,dst in (
 ('.build/cyd-vorbis-block-host-01/report.json','original-dual-report.json'),
 ('.build/cyd-vorbis-block-host-01-command.json','original-dual-command.json'),
 ('.build/cyd-vorbis-block-xiph-01/report.json','xiph-report.json'),
 ('.build/cyd-vorbis-block-xiph-01-command.json','xiph-command.json'),
 ('.build/cyd-vorbis-block-rate-host-01/report.json','rate-report.json'),
 ('.build/cyd-vorbis-block-rate-host-01-command.json','rate-command.json')):
    shutil.copyfile(ROOT/src,proofs/dst)

changes=[]
def adapt(text,old,new,label):
    assert text.count(old)==1,(label,text.count(old))
    changes.append(label)
    return text.replace(old,new)

(PROJECT/'main/CMakeLists.txt').write_text('''set(M "$ENV{CYD_VORBIS_CANDIDATE}")
idf_component_register(SRCS "main.c" INCLUDE_DIRS "."
 REQUIRES esp_audio_codec freertos heap esp_system esp_rom)
target_compile_definitions(${COMPONENT_LIB} PRIVATE
 BLOCK_MATRIX_PROFILE_CYD=1 BLOCK_MATRIX_MINIMAL_RATE_REBIND_VERIFIED=1)
include("${M}/compat/vorbis_repair/enable.cmake")
native_enable_vorbis_repair()
''',encoding='utf-8')
helper=(ROOT/'idf/esp32-cyd2usb-native/main/compat/vorbis_repair/enable.cmake').read_text()
helper=adapt(helper,'foreach(source setup.c simple.c output.c)','foreach(source setup.c output.c)','raw-only required sources')
helper=adapt(helper,'        "${main}/vorbis_repair/simple.c"\n','', 'raw-only compile sources')
start=helper.index('    target_link_options(')
helper=adapt(helper,helper[start:helper.index('endfunction()',start)],'''    target_link_options(${COMPONENT_LIB} INTERFACE
        "-Wl,--wrap=esp_vorbis_dec_open"
        "-Wl,--wrap=esp_vorbis_dec_decode")
''','raw-only two public wrappers')
(PROJECT/'raw-enable.cmake').write_text(helper,encoding='utf-8')
ps=(base/'sdk-build.ps1').read_text()
ps=adapt(ps,"      [Parameter(Mandatory)][string]$CodecDirectory,\n      [Parameter(Mandatory)][ValidateSet('0','1')][string]$ExpectedRejection)","      [Parameter(Mandatory)][string]$CodecDirectory)",'launcher remove format-scope parameter')
ps=adapt(ps,'\n \'-D\', "FORMAT_EXPECT_LOW_RATE_REJECTION=$ExpectedRejection",','', 'launcher remove format-scope cmake flag')
(PROJECT/'sdk-build.ps1').write_text(ps,encoding='utf-8')
shutil.copyfile(ROOT/'tests/windows_compile_command.py',OUT/'windows_compile_command.py')
shutil.copyfile(PROPOSAL/'block_protocol.py',OUT/'block_protocol.py')
runner=(ROOT/'tests/run-cyd-vorbis-format-qemu.py').read_text()
original=runner
runner=adapt(runner,'"""Isolated CYD public raw Vorbis format probe; no radio/Ogg/reset/OOM qualification."""','"""Isolated CYD public raw block matrix; no radio/Ogg/reset/OOM qualification."""','runner scope')
runner=adapt(runner,'from windows_compile_command import macro_command, check_macro_inputs','from windows_compile_command import macro_command, check_macro_inputs\nfrom block_protocol import validate_log, checked_banks','strict block protocol')
runner=adapt(runner,"FIXTURE_SHA = '839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'","DATA_SHA = 'efd24b5bc251c18be3cd00ce743a2366be0dfe9c1b2aff211fed89480dff96d9'",'pin frozen actual banks')
runner=adapt(runner,"'vorbis_repair/output.c', 'vorbis_repair/simple.c',","'vorbis_repair/output.c',",'two canonical raw translation units')
a=runner.index('def fixture_accounting(');b=runner.index('def main():',a)
runner=adapt(runner,runner[a:b],'','remove prior fixture and protocol validator')
runner=adapt(runner,"    parser.add_argument('--scope', choices=('baseline', 'acceptance'), required=True)\n    parser.add_argument('--control', choices=('old-guard',))\n",'','no prior scope or source mutant')
runner=adapt(runner,"    if args.control and args.scope != 'acceptance': parser.error('old-guard control requires acceptance scope')\n",'','remove old-scope check')
runner=adapt(runner,"'target/cyd_vorbis_format_qemu'","'target/cyd_vorbis_blocks_qemu'",'new isolated project path')
runner=adapt(runner,"scope=args.scope, control=args.control,\n                  regression_reproduced=False, format_acceptance_qualified=False, physical_device=False,","block_matrix_qualified=False, full_G6_qualified=False, physical_device=False,",'matrix report identity')
runner=adapt(runner,"        freeze(Path(__file__).with_name('windows_compile_command.py'), Path('helpers/windows_compile_command.py'))","        freeze(Path(__file__).with_name('windows_compile_command.py'), Path('helpers/windows_compile_command.py'))\n        freeze(Path(__file__).with_name('block_protocol.py'), Path('helpers/block_protocol.py'))",'freeze actual protocol')
a=runner.index("        header = (out/'sources/project/main/fixture.h')");b=runner.index("        report['variant_sources']",a)
runner=adapt(runner,runner[a:b],'''        manifest_path = out/'sources/project/banks.json'
        need(sha(manifest_path) == DATA_SHA, 'Wrong frozen bank manifest')
        banks = json.loads(manifest_path.read_text())
        checked_banks(banks['banks'])
        freeze_record = json.loads((out/'sources/project/freeze.json').read_text())
        need(freeze_record['manifest_sha256'] == DATA_SHA and
             sha(out/'sources/project/main/banks_data.h') == freeze_record['banks_header_sha256'], 'Raw bank header binding')
        proofs = out/'sources/project/proofs'
        for name,key in (('xiph-report.json','host_reference_report_sha256'),
                         ('original-dual-report.json','original_dual_report_sha256'),
                         ('rate-report.json','minimal_rate_rebind_report_sha256')):
            need(sha(proofs/name) == banks[key], 'Host proof hash '+name)
        xiph = json.loads((proofs/'xiph-report.json').read_text())
        rate = json.loads((proofs/'rate-report.json').read_text())
        dual = json.loads((proofs/'original-dual-report.json').read_text())
        need(xiph['completed'] is True and xiph['reference_corpus_qualified'] is True and
             len(xiph['cases']) == 108 and not xiph['failures'], 'All108 Xiph corpus proof')
        need(rate['completed'] is True and rate['passed'] is True and len(rate['cases']) == 36 and not rate['failures'],
             'All36 minimal rate rebind proof')
        need(dual['completed'] is True and dual['passed'] is False and len(dual['cases']) == 108 and len(dual['failures']) == 30,
             'Preserve original dual-reference NONPASS')
        for name,expected in (('xiph-command.json',0),('rate-command.json',0),('original-dual-command.json',1)):
            row = json.loads((proofs/name).read_text())
            need(row['status'] == 'TERMINAL' and type(row['returncode']) is int and row['returncode'] == expected,
                 'Actual host terminal receipt '+name)
        report['encoded_data'] = dict(manifest_sha256=DATA_SHA, xiph_cases=108, native_compared=78,
            native_floor_refusals=30, minimal_rate_rebind_qualified=True)
        shutil.copytree(out/'sources/candidate',out/'variant')
        shutil.copyfile(out/'sources/project/raw-enable.cmake',out/'variant/compat/vorbis_repair/enable.cmake')
''','bind actual completed host proofs and raw-only helper adaptation')
runner=adapt(runner,"'-ExpectedRejection',int(args.scope == 'baseline')],1200)","],1200)",'launcher argument')
runner=adapt(runner,"MODULES[:3]} and len(actual) == 3","MODULES[:2]} and len(actual) == 2",'exact two actual raw compile rows')
runner=adapt(runner,"],120)\n        stderr = (out/'qemu.stderr.log')","],300)\n        stderr = (out/'qemu.stderr.log')",'bounded full matrix runtime')
runner=adapt(runner,"        report['observed'] = validate_log(log+'\\n'+stderr,args.scope,args.control,header)","        qemu_row = report['commands'][-1]\n        report['observed'] = validate_log(log+'\\n'+stderr,banks['banks'],'cyd',\n            manifest_sha256=DATA_SHA,minimal_rate_rebind_qualified=True,\n            returncode=qemu_row['exit_status'],timed_out=qemu_row['state'] != 'complete',interrupted=False)",'strict actual target process validation')
a=runner.index('        report.update(completed=True,regression_reproduced=');b=runner.index('        return 0',a)
runner=adapt(runner,runner[a:b],'''        report.update(completed=True,block_matrix_qualified=True,passed=True,result='RAW_BLOCK_MATRIX_ACCEPTED')
        save()
        print(json.dumps({k:report[k] for k in ('result','passed','block_matrix_qualified','observed')}))
''','bounded matrix success only')
runner=adapt(runner,"report.update(passed=False,completed=False,regression_reproduced=False,format_acceptance_qualified=False,","report.update(passed=False,completed=False,block_matrix_qualified=False,",'matrix nonpass')
assert 'args.scope' not in runner and 'args.control' not in runner and 'fixture.h' not in runner
compile(runner,str(OUT/'run-cyd-vorbis-blocks-qemu.py'),'exec')
(OUT/'run-cyd-vorbis-blocks-qemu.py').write_text(runner,encoding='utf-8')
(OUT/'runner-adaptation.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),runner.splitlines(True),fromfile='tests/run-cyd-vorbis-format-qemu.py',tofile='run-cyd-vorbis-blocks-qemu.py')),encoding='utf-8')
pins={'status':'SOURCE_ONLY','changes':changes,'files':{p.relative_to(OUT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()},'no_tools_executed':True}
(OUT/'pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT),'changes':len(changes),'files':len(pins['files']),'pins_sha256':sha(OUT/'pins.json')}))
