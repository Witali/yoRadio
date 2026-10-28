"""Pure full-corpus replay of adjacent-block overlap qualification."""
import argparse,json,struct
from pathlib import Path
from vorbis_synthesis_checkpoint import ROOT,archive_members,clean_host,load_local,need,sha


def verify():
    members=archive_members('tests/results/vorbis-overlap-20261028',
        '685778be3a8650fd9e1740e2e99b1540b1f2cde7ec33046f96d3e3bde6fd2d23',
        'cba1bd703fb6467828b56db3becd796eaf270f4ecdebf78025f5d3b577c54700')
    reader=load_local('tests/test-vorbis-overlap.py',
        'bf49268b746e50304522c43077e18eecf46f3fa2b7c6b68f86b8f26c3d4cb147','overlap_checkpoint_reader')
    report,capture=clean_host(members,'host03')
    need(report['controls']==dict(cases=864,refusals=8308,checks=11895678,cancellations=57376,resets=108),
         'complete guarded stateful corpus')
    for name,digest in report['sources'].items():
        need(sha(members['host03/sources/'+name])==digest,'all executed frozen source bytes')
    measured=reader.inspect_capture(capture)
    controls=reader.corruption_controls(capture)
    need(measured==report['measurements'] and controls==report['corruption_controls'],'complete independent replay')
    need(measured['nonzero_operands_rounded_to_zero']==17962 and
         measured['underflow_terms_with_exponent_at_least1074']==13767 and
         measured['full_range_PCM_qualified'] is False,'known underflow limitation retained')
    commands={row['name']:row for row in report['commands']}
    need(len(commands)==3 and '-fsanitize=address,undefined' in commands['compile']['child_argv'] and
         '-UNDEBUG' in commands['compile']['child_argv'],'actual sanitizer/assert-enabled execution')
    profiles=json.loads(members['profiles01/report.json'])
    need(profiles['completed'] and profiles['passed'] and len(profiles['commands'])==7 and
         all(row['returncode']==0 for row in profiles['commands']),'source profiles complete')
    need(profiles['lint']==[dict(unit='overlap',warnings=0,errors=0)],'production source lint clean')
    machines=[]
    for name,body in members.items():
        if name.startswith('profiles01/') and name.endswith('.o'):
            need(body[:5]==b'\x7fELF\x01','real ELF32 source object')
            machines.append(struct.unpack_from('<H',body,18)[0])
    need(sorted(machines)==[94,94,243,243],'C/C++ objects of both ISA')
    lint=json.loads(members['fixture-lint01/report.json'])
    need(lint['completed'] and lint['warnings']==19 and lint['errors']==0,'fixture diagnostics retained')
    return dict(passed=True,members=len(members),measurements=measured,corruption_controls=controls,
        archived_code_executed=False,files_extracted=False,commands_reexecuted=0,native_executed=False,
        full_range_PCM_qualified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=verify()
    if args.report:
        need(args.report.resolve().is_relative_to(ROOT/'.build') and not args.report.exists(),'fresh local report')
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
