"""Inspect all retained window evidence without running archived commands."""
import argparse, json, struct
from pathlib import Path
from vorbis_synthesis_checkpoint import ROOT, archive_members, clean_host, load_local, need, sha


def verify():
    members = archive_members('tests/results/vorbis-window-20261028',
        '5ab17e02a3182fc1b00ac99cdde5bde2bae73768ee0466ae3504e0cef6cab79c',
        'a3095be81555f9c33ffa6bb70a616e1eb54472afb090e3949bb4243a0e6bd242')
    reader = load_local('tests/test-vorbis-window.py',
        'c2fbcc21f1236b2c4b95d7e4f77a5498d4eb427fb2ec5ec5777c0447b0ed69d9','window_checkpoint_reader')
    report, capture = clean_host(members)
    for name,digest in report['sources'].items():
        need(sha(members['host04/sources/'+name])==digest,'every executed source byte')
    need(members['host04/sources/runner.py']==(ROOT/'tests/test-vorbis-window.py').read_bytes(),'same pinned reader')
    measured = reader.inspect_capture(capture)
    need(measured==report['measurements'] and reader.corruption_controls(capture)==report['corruption_controls'],
         'complete high-precision replay and corruption controls')
    need(len(report['commands'])==3 and report['controls']==dict(refusals=5272,checks=3494013),'complete guarded corpus')
    need(members['host02/capture.bin']==members['host03/capture.bin']==capture,'all numerical captures identical')
    compile_row = next(row for row in report['commands'] if row['name']=='compile')
    need('-fsanitize=address,undefined' in compile_row['child_argv'] and '-UNDEBUG' in compile_row['child_argv'],
         'sanitizers and assertions enabled')
    profiles=json.loads(members['profiles02/report.json'])
    need(profiles['completed'] and profiles['passed'] and len(profiles['commands'])==8 and
         all(row['returncode']==0 for row in profiles['commands']), 'source checks terminal and clean')
    need(profiles['lint']==[dict(unit='window',warnings=0,errors=0),dict(unit='fixture',warnings=16,errors=0)],
         'all lint diagnostics retained')
    actual=[]
    for name,body in members.items():
        if name.startswith('profiles02/') and name.endswith('.o'):
            need(body[:5]==b'\x7fELF\x01','actual ELF32 source object')
            actual.append(struct.unpack_from('<H',body,18)[0])
    need(sorted(actual)==[94,94,243,243],'C/C++ objects for both architectures')
    return dict(passed=True,members=len(members),measurements=measured,
        corruption_controls=report['corruption_controls'],archived_code_executed=False,
        commands_reexecuted=0,files_extracted=False,native_executed=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=verify()
    if args.report:
        need(args.report.resolve().is_relative_to(ROOT/'.build') and not args.report.exists(),'fresh local report')
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
