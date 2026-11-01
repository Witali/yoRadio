"""Reject contradictory copies of an actual passing Ogg task transcript.

This never modifies the native campaign or runs an SDK, emulator or archived
program. It imports the identical current canonical reader and mutates only
in-memory copies of actual observations.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/run-cyd-ogg-playback-task-qemu.py'


def need(value,reason):
    if not value: raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    native,out=args.capture.resolve(),args.output.resolve()
    need(native.is_relative_to(ROOT/'.build') and native.is_dir(),'actual local native capture')
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh ignored witness capture')
    report=json.loads((native/'report.json').read_bytes())
    need(report['passed'] and report['completed'] and report['all_bound_inputs_current'],'original actual gate is passing')
    need(READER.read_bytes()==(native/'sources/controller.py').read_bytes(),'identical current executed reader')
    spec=importlib.util.spec_from_file_location('current_ogg_playback_task_reader',READER)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    source=(native/'qemu.stdout.log').read_text('utf-8')+'\n'+(native/'qemu.stderr.log').read_text('utf-8')
    original=source.replace('\r\n','\n')
    need(reader.validate_log(original,report['pcm_reference'])==report['measurements'],'actual intact transcript accepted')
    before={str(p):sha(p) for p in (READER,native/'report.json',native/'qemu.stdout.log',native/'qemu.stderr.log')}
    out.mkdir(parents=True)
    (out/'reader.py').write_bytes(READER.read_bytes())
    (out/'controller.py').write_bytes(Path(__file__).read_bytes())

    def alter(tag,match,values=None,remove=False):
        lines=original.splitlines()
        for i,line in enumerate(lines):
            if not line.startswith(tag+' '): continue
            pairs=[part.split('=',1) for part in line[len(tag)+1:].split()]
            fields=dict(pairs)
            if not all(fields.get(key)==str(value) for key,value in match.items()): continue
            if remove: del lines[i]
            else:
                need(set(values)<=set(fields),'mutation edits an observed field')
                for key,value in values.items(): fields[key]=str(value(fields[key]) if callable(value) else value)
                lines[i]=tag+' '+' '.join(key+'='+fields[key] for key,_ in pairs)
            changed='\n'.join(lines)
            need(changed!=original,'contradictory control changed the actual transcript')
            return changed
        raise ValueError('requested actual control witness is missing: '+tag)

    case='CYD_OGG_PLAYBACK_TASK_CASE'
    end='CYD_OGG_PLAYBACK_TASK_COMPLETE'
    chain='CYD_OGG_PLAYBACK_TASK_CHAIN'
    controls=[
        ('missing_long_maintenance',lambda:alter(case,{'fixture':'OPUS120','id':'T2'},remove=True)),
        ('untrimmed_long_output_size',lambda:alter(case,{'fixture':'OPUS120','id':'T0'},{'pcm_bytes':2119680})),
        ('wrong_logical_pcm_hash',lambda:alter(case,{'fixture':'OPUS20','id':'T0'},{'sha256':'0'*64})),
        ('stop_discard_mismatch',lambda:alter(case,{'fixture':'VORBIS','id':'T1'},{'discard_generation':lambda x:int(x)+1})),
        ('stale_token_accepted',lambda:alter(case,{'fixture':'OPUS20','id':'T2'},{'stale_rejected':0})),
        ('missing_chain_link',lambda:alter('CYD_OGG_PLAYBACK_LINK',{'fixture':'CHAIN','index':1},remove=True)),
        ('intermediate_chain_eof',lambda:alter(end,{}, {'output_flushes':11})),
        ('chain_uses_multiple_http',lambda:alter(chain,{}, {'http_cleanup':18})),
        ('no_same_input_link_crossing',lambda:alter(chain,{}, {'cross_link_reads':0})),
        ('chain_generation_changes',lambda:alter('CYD_OGG_PLAYBACK_OBS_OPEN',{'fixture':'CHAIN','instance':18},{'generation':lambda x:int(x)+1})),
        ('wrong_resize_capacity',lambda:alter('CYD_OGG_PLAYBACK_OBS_RETRY',{'fixture':'OPUS120'},{'capacity':12288})),
        ('retry_replays_consumed_input',lambda:alter('CYD_OGG_PLAYBACK_OBS_RETRY',{'fixture':'OPUS120'},{'arguments_advanced_once':0})),
        ('missing_public_resize',lambda:alter('CYD_OGG_PLAYBACK_OBS_RESIZE',{'fixture':'OPUS120'},remove=True)),
        ('lowered_production_output_capacity',lambda:alter('CYD_OGG_PLAYBACK_OBS_INITIAL',{'instance':1},{'capacity':8192})),
        ('wrong_task_stack',lambda:alter('CYD_OGG_PLAYBACK_TASK_PROFILE',{'role':'decode'},{'stack':8192})),
        ('impossible_free_heap_block',lambda:alter('CYD_OGG_PLAYBACK_MEMORY',{'fixture':'OPUS20'},{'largest_internal':0})),
        ('missing_compiler_fixture_census',lambda:alter('CYD_OGG_PLAYBACK_TASK_FIXTURE',{'fixture':'OPUS120'},remove=True)),
        ('decoder_leak',lambda:alter(end,{}, {'live_decoders':1})),
    ]
    rejected=[]
    for name,make in controls:
        mutated=make()
        try: reader.validate_log(mutated,report['pcm_reference'])
        except ValueError as error: rejected.append(dict(name=name,reason=str(error)))
        else: raise ValueError('contradictory transcript accepted: '+name)
    need(all(sha(path)==digest for path,digest in before.items()),'original native evidence and reader unchanged')
    result=dict(passed=True,original_transcript_accepted=True,rejected=rejected,
                rejected_controls=len(rejected),reader_sha256=sha(READER),original_bindings=before,
                native_campaign_repeated=False,original_reports_modified=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,rejected_controls=len(rejected),native_campaign_repeated=False)))


if __name__=='__main__':
    sys.dont_write_bytecode=True
    main()
