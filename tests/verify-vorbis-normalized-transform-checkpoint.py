"""Replay the complete normalized IMDCT capture using pinned local pure readers."""
import argparse, json
from pathlib import Path
from vorbis_synthesis_checkpoint import ROOT, archive_members, clean_host, load_local, need, sha


def verify():
    members = archive_members('tests/results/vorbis-normalized-transform-20261028',
        '92ef522d3707836307333694257fa2f4330e6edb32be1b3041f3e5112f9af1f4',
        'a6b528502ec1dc86546e2596631883f57497d3ed8b3efe9a69014e64d244f305')
    subject = load_local('tests/test-vorbis-normalized-transform.py',
        '311c171916a61f663cf07edeac7718e2c34d79fa76b50a3f87067c74dcbde61a','normalized_checkpoint_reader')
    oracle = load_local('tests/test-vorbis-transform.py',
        '443000f55dc389a3a53a84af4a8bb118ada5367e4a3ccbf8525a9ceb630cf59c','normalized_checkpoint_oracle')
    report, capture = clean_host(members)
    need(len(report['commands'])==7 and report['controls']==dict(cases=1729,matched=301248,refusals=336,checks=5589927),
         'complete host scope')
    for name,pin in report['inputs'].items():
        need(sha(members['host04/'+pin['snapshot']])==pin['sha256'], 'all executed source identities')
    need(members['host04/sources/runner.py']==(ROOT/'tests/test-vorbis-normalized-transform.py').read_bytes(),
         'executed reader matches pinned local reader')
    measured = subject.compare(capture,oracle)
    need(measured==report['measurements'], 'all original measurements independently replayed')
    need(oracle.oracle_anchors()==report['anchors'], 'independent FFT anchors')
    need(members['host03/capture.bin']==capture, 'test strengthening did not change numerical corpus')
    # Check every recorded old/new comparison was inside an assert-enabled,
    # sanitizer-instrumented build, rather than inferring parity from FFT error.
    commands = {row['name']:row for row in report['commands']}
    for index in range(3):
        argv = commands[f'compile-{index:02}']['child_argv']
        need('-UNDEBUG' in argv and '-fsanitize=address,undefined' in argv and '-Werror' in argv,
             'assertions/sanitizers enabled in every unit')
    need('matched=301248 refusals=336 checks=5589927' in members['host04/execute.stdout.log'].decode(),
         'actual guarded comparison totals')
    controls = [('magic',b'X'+capture[1:]),('truncated',capture[:-1]),('trailing',capture+b'X'),
                ('source',capture[:28]+bytes(8)+capture[36:]),
                ('output',capture[:284]+b'\0\0\0\0\0\0\xf8\x7f'+capture[292:])]
    for name,bad in controls:
        try: subject.compare(bad,oracle)
        except (ValueError,OverflowError): continue
        raise ValueError('damaged capture accepted: '+name)
    gcc = json.loads(members['gcc02/report.json'])
    need(gcc['completed'] and len(gcc['commands'])==12 and
         all(row['returncode']==0 and not row.get('forced_stop') for row in gcc['commands']), 'source profiles pass')
    lint=json.loads(members['lint01/report.json']);fixture_lint=json.loads(members['lint02/report.json'])
    need(lint['completed'] and lint['errors']==0 and
         all(row['warnings']==row['errors']==0 for row in lint['commands'] if row['source'] in ('spectrum.c','transform.c')),
         'production source analysis clean')
    need(fixture_lint['completed'] and fixture_lint['warnings']==3 and fixture_lint['errors']==0,
         'all final fixture diagnostics retained')
    objects = [body for name,body in members.items() if name.startswith('gcc02/') and name.endswith('.o')]
    need(len(objects)==6 and all(body[:5]==b'\x7fELF\x01' for body in objects), 'six actual ELF32 objects')
    return dict(passed=True,members=len(members),measurements=measured,corruption_controls=[name for name,_ in controls],
        archived_code_executed=False,commands_reexecuted=0,files_extracted=False,native_executed=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=verify()
    if args.report:
        need(args.report.resolve().is_relative_to(ROOT/'.build') and not args.report.exists(),'fresh local report')
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
