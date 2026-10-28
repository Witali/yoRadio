"""Pure exact-pair PCM capture replay with pinned local integer/Fraction oracle."""
import argparse,json,struct
from pathlib import Path
from vorbis_synthesis_checkpoint import ROOT,archive_members,clean_host,load_local,need,sha


def verify():
    members=archive_members('tests/results/vorbis-pcm-pair-20261028',
        'd96b5cbe53cee88ca78d5f4fb4e43dd72b5fc8676f64b55d92c2d575d413e648',
        '1cab066613634e0cd0240389c45c783c536df6e620e86d6cc4da83f4a6bbedd0')
    reader=load_local('tests/test-vorbis-pcm-pair.py',
        'f53ec0429b06abf2576e5c052df4ea95fc60dae59f63f42687a25e6ba7e60aa9','pcm_pair_checkpoint_reader')
    report,capture=clean_host(members)
    for name,pin in report['inputs'].items():
        need(sha(members['host04/'+pin['snapshot']])==pin['sha256'],'all executed source identities')
    model=reader.rows()
    need(reader.encode(model)==members['host04/input.bin'],'complete original input corpus')
    measured=reader.compare(capture,model)
    controls=reader.corruption_controls(capture,model)
    need(measured==report['measurement'] and controls==report['corruption_controls'],'complete PCM and corruption replay')
    need(reader.fraction_anchors()==report['fraction_anchors']==2033,'independent Fraction/symbolic anchors')
    need(report['controls']==dict(refusals=186,checks=4986045),'full refusal/assertion campaign')
    need(members['host03/capture.bin']==capture,'pure-reader strengthening did not change numerical capture')
    commands={row['name']:row for row in report['commands']}
    need(len(commands)==3 and '-fsanitize=address,undefined' in commands['compile']['child_argv'] and
         '-UNDEBUG' in commands['compile']['child_argv'],'actual assertions and sanitizers enabled')
    profiles=json.loads(members['profiles02/report.json'])
    need(profiles['completed'] and profiles['passed'] and len(profiles['commands'])==8 and
         all(row['returncode']==0 for row in profiles['commands']),'source checks completed')
    need(profiles['lint']==[dict(unit='pcm',warnings=0,errors=0),dict(unit='fixture',warnings=5,errors=0)],
         'all production and fixture diagnostics retained')
    machines=[]
    for name,body in members.items():
        if name.startswith('profiles02/') and name.endswith('.o'):
            need(body[:5]==b'\x7fELF\x01','real ELF32 source object')
            machines.append(struct.unpack_from('<H',body,18)[0])
    need(sorted(machines)==[94,94,243,243],'C/C++ source objects for both ISA')
    return dict(passed=True,members=len(members),measurements=measured,fraction_anchors=2033,
        corruption_controls=controls,archived_code_executed=False,commands_reexecuted=0,
        files_extracted=False,native_executed=False,complete_decoder_qualified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--report',type=Path);args=parser.parse_args()
    result=verify()
    if args.report:
        need(args.report.resolve().is_relative_to(ROOT/'.build') and not args.report.exists(),'fresh local report')
        args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))
