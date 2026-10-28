"""Replay all integer timing metadata and safe Xiph-reference observations."""
import argparse,json,struct
from pathlib import Path
from vorbis_synthesis_checkpoint import ROOT,archive_members,clean_host,load_local,need,sha


def verify():
    members=archive_members('tests/results/vorbis-timing-20261028',
        '9cb5c3974079a9da76bb88a532734cc8023a60d49f36f531813a7155264e1fd6',
        '5b94f5f7a4382ca75345c1c6739f092d6d11789723a99be401dd391b8036f4c9')
    reader=load_local('tests/test-vorbis-timing.py',
        'f990067645a196972767639c100506be757b9adb8a2d0f8bbd8fe3857f0be33a','timing_checkpoint_reader')
    report,capture=clean_host(members,'host03')
    original=members['host03/sources/original31.json']
    need(sha(original)==reader.ORIGINAL_SHA,'pinned complete original31 source')
    model=reader.corpus(json.loads(original))
    need(reader.encode(model)==members['host03/input.bin'],'complete original input commands')
    for name,digest in report['sources'].items():
        need(sha(members['host03/sources/'+name])==digest,'every executed frozen source byte')
    fragment=reader.xiph_fragment(members['host03/sources/upstream/block.c'])
    need(fragment==members['host03/sources/native/xiph-granule.inc'] and
         sha(fragment)==report['fragment_sha256'],'unchanged original Xiph metadata slice')
    measured=reader.inspect_capture(capture,model);controls=reader.corruption_controls(capture,model)
    need(measured==report['measurements'] and controls==report['corruption_controls'],'all timing observations replayed')
    need(report['controls']==dict(commands=20019,references=12467,refusals=26359,checks=1521715),
         'complete guarded command/refusal totals')
    for name in ['input.bin','model.json','capture.bin']:
        need(members['host02/'+name]==members['host03/'+name],'corruption-probe repair changed no corpus or capture')
    commands={row['name']:row for row in report['commands']}
    need(len(commands)==3 and '-fsanitize=address,undefined' in commands['compile']['child_argv'] and
         '-UNDEBUG' in commands['compile']['child_argv'],'actual sanitizer/assert-enabled metadata execution')
    profiles=json.loads(members['profiles01/report.json'])
    need(profiles['completed'] and profiles['passed'] and len(profiles['commands'])==7 and
         all(row['returncode']==0 for row in profiles['commands']),'source checks completed')
    need(profiles['lint']==[dict(unit='timing',warnings=0,errors=0)],'production source lint clean')
    machines=[]
    for name,body in members.items():
        if name.startswith('profiles01/') and name.endswith('.o'):
            need(body[:5]==b'\x7fELF\x01','actual ELF32 source object')
            machines.append(struct.unpack_from('<H',body,18)[0])
    need(sorted(machines)==[94,94,243,243],'C/C++ source objects for both architectures')
    lint=json.loads(members['fixture-lint01/report.json'])
    need(lint['completed'] and lint['warnings']==6 and lint['errors']==0,'LP64 fixture diagnostics retained')
    return dict(passed=True,members=len(members),measurements=measured,corruption_controls=controls,
        archived_code_executed=False,files_extracted=False,commands_reexecuted=0,metadata_only=True,
        decoder_executed=False,PCM_executed=False,native_executed=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=verify()
    if args.report:
        need(args.report.resolve().is_relative_to(ROOT/'.build') and not args.report.exists(),'fresh local report')
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
