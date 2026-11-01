"""Reject contradictory copies of the actual passing gain task transcript.

Only local data are read. No SDK, emulator, archived program, production gain
helper or codec is executed; original reports/logs remain unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/run-cyd-ogg-gain-task-qemu.py'
ORACLE=ROOT/'tests/prepare-cyd-opus-gain-output-reference.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();native,out=args.capture.resolve(),args.output.resolve()
    need(native.is_relative_to(ROOT/'.build') and native.is_dir(),'actual local native capture')
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local witness output')
    report=json.loads((native/'report.json').read_bytes())
    need(report['passed'] and report['completed'] and report['all_bound_inputs_current'],'actual original gate passed')
    need(READER.read_bytes()==(native/'sources/controller.py').read_bytes(),'identical frozen original controller')
    need(ORACLE.read_bytes()==(native/'sources/reference/final-mono-oracle.py').read_bytes(),'identical pre-execution independent mono oracle')
    reader=module('current_gain_task_reader',READER)
    oracle=module('independent_captured_stock_mono',ORACLE)
    original=(native/'qemu.stdout.log').read_text('utf-8')+'\n'+(native/'qemu.stderr.log').read_text('utf-8')
    original=original.replace('\r\n','\n')

    def validate(text):
        measured,stock=reader.validate_log(text,report['pcm_reference'])
        waits=[row for tag,row in measured['public_controls'] if tag=='CAPTURE_WAIT']
        need(waits==[dict(fixture='LIFE_VORBIS',fixed_budget_ms=90000,ordinary_budget_ms=30000,whole_qemu_budget_ms=600000)],'one fixed bounded first-capture budget; ordinary lifecycle and whole-QEMU bounds unchanged')
        need(stock==(native/'stock-vorbis.pcm').read_bytes(),'all original captured stock bytes')
        # The complete independently computed legacy mono hashes were committed
        # by the outer gate only after whole stock-byte identity was checked.
        expected=report['vorbis_post_oracle']['expected_mono_hashes']
        for row in measured['render_links']:
            if row['codec']=='VORBIS':need(row['sha256']==expected[str(row['volume'])],'whole Vorbis reset/bypass output')
        for row in measured['render_cases']:
            links=[link for link in measured['render_links'] if link['fixture']==row['fixture']]
            need(links and all(link['sha256']==row['sha256'] for link in links),'each single-link final output digest agrees with its actual span')
        opened=0;source_complete=render_complete=0;queued=[]
        chain=report['pcm_reference']['chain']['links']
        for line in text.splitlines():
            if not line.startswith('CYD_OGG_GAIN_') or ' fixture=GAIN_CHAIN ' not in line:continue
            tag=line.split(' ',1)[0]
            if tag=='CYD_OGG_GAIN_OBS_OPEN':
                if opened and source_complete<opened and chain[opened-1]['gain_q8']!=chain[opened]['gain_q8']:
                    queued.append(dict(next_index=opened,source_links_complete=source_complete,render_links_complete=render_complete))
                opened+=1
            elif tag=='CYD_OGG_GAIN_LINK':source_complete+=1
            elif tag=='CYD_OGG_GAIN_RENDER_LINK':render_complete+=1
        need(opened==source_complete==render_complete==9 and queued,'a real later-gain decoder opens while earlier source PCM remains queued for the output owner')
        return measured,stock

    measured,stock=validate(original)
    for volume in (1,254):
        need(oracle.full_mono(stock,0,volume)['sha256']==report['vorbis_post_oracle']['expected_mono_hashes'][str(volume)],'independent full Vorbis mono golden recomputed')
    expected=dict(report['measurements'])
    for key in ('stock_vorbis_path','independent_vorbis_mono_hashes'):expected.pop(key)
    expected['vorbis_oracle_pending']=True
    need(json.loads(json.dumps(measured))==expected,'actual intact native reader evidence matches its frozen report')
    before={str(path):sha(path) for path in (READER,ORACLE,native/'report.json',native/'qemu.stdout.log',native/'qemu.stderr.log',native/'stock-vorbis.pcm')}
    out.mkdir(parents=True)
    (out/'controller.py').write_bytes(Path(__file__).read_bytes())
    (out/'reader.py').write_bytes(READER.read_bytes())

    def alter(tag,match,values=None,remove=False):
        lines=original.splitlines()
        for at,line in enumerate(lines):
            if not line.startswith(tag+' '):continue
            pairs=[part.split('=',1) for part in line[len(tag)+1:].split()];fields=dict(pairs)
            if not all(fields.get(key)==str(value) for key,value in match.items()):continue
            if remove:del lines[at]
            else:
                need(set(values)<=set(fields),'control changes an actual observed field')
                for key,value in values.items():fields[key]=str(value(fields[key]) if callable(value) else value)
                lines[at]=tag+' '+' '.join(key+'='+fields[key] for key,_ in pairs)
            result='\n'.join(lines);need(result!=original,'control changes the original observation');return result
        raise ValueError('requested witness record missing: '+tag)

    case='CYD_OGG_GAIN_TASK_CASE';end='CYD_OGG_GAIN_TASK_COMPLETE';link='CYD_OGG_GAIN_RENDER_LINK'
    controls=[
        ('missing_long_maintenance',lambda:alter(case,{'fixture':'LIFE_MINUS6','id':'T2'},remove=True)),
        ('untrimmed_source_size',lambda:alter(case,{'fixture':'LIFE_PLUS48','id':'T0'},{'pcm_bytes':2115840})),
        ('source_was_gain_mutated',lambda:alter('CYD_OGG_GAIN_LINK',{'fixture':'LIFE_PLUS48'},{'sha256':'0'*64})),
        ('wrong_gain_sign',lambda:alter(link,{'fixture':'LIFE_MINUS6'},{'gain_q8':1536})),
        ('gain_not_reset_for_vorbis',lambda:alter(link,{'fixture':'GAIN_CHAIN','index':1},{'gain_q8':12288})),
        ('early_clipped_mono',lambda:alter(link,{'fixture':'LIFE_PLUS48'},{'sha256':'0'*64})),
        ('vorbis_mono_changed',lambda:alter(link,{'fixture':'GAIN_CHAIN','index':1},{'sha256':'0'*64})),
        ('mismatched_case_mono_digest',lambda:alter('CYD_OGG_GAIN_RENDER_CASE',{'fixture':'OPUS20_ZERO_V254'},{'sha256':'0'*64})),
        ('wrong_player_volume',lambda:alter(link,{'fixture':'LIFE_PLUS48'},{'volume':254})),
        ('untrimmed_mono_size',lambda:alter(link,{'fixture':'LIFE_PLUS48'},{'bytes':1057920})),
        ('missing_reset_link',lambda:alter(link,{'fixture':'GAIN_CHAIN','index':3},remove=True)),
        ('stop_discard_sequence_mismatch',lambda:alter('CYD_OGG_GAIN_CONTROL_STOP_QUIET',{'fixture':'LIFE_VORBIS'},{'discard_sequence':lambda x:int(x)+1})),
        ('discard_wrong_output_owner',lambda:alter('CYD_OGG_GAIN_CONTROL_DISCARD',{}, {'core':0})),
        ('discard_precedes_request',lambda:alter('CYD_OGG_GAIN_CONTROL_STOP_REQUEST',{'fixture':'LIFE_PLUS48'},{'time_us':lambda x:int(x)+1000000000})),
        ('output_not_quiet_after_stop',lambda:alter('CYD_OGG_GAIN_CONTROL_STOP_QUIET',{'fixture':'LIFE_MINUS6'},{'driver_writes':lambda x:int(x)+1})),
        ('stop_input_still_reading',lambda:alter('CYD_OGG_GAIN_CONTROL_STOP_QUIET',{'fixture':'LIFE_PLUS48'},{'input_reading':1})),
        ('stale_token_accepted',lambda:alter(case,{'fixture':'LIFE_PLUS48','id':'T2'},{'stale_rejected':0})),
        ('intermediate_chain_eof',lambda:alter(end,{}, {'output_flushes':25})),
        ('multiple_chain_http_sessions',lambda:alter('CYD_OGG_GAIN_TASK_CHAIN',{}, {'http_cleanup':38})),
        ('no_same_read_link_crossing',lambda:alter('CYD_OGG_GAIN_TASK_CHAIN',{}, {'cross_link_reads':0})),
        ('chain_generation_changes',lambda:alter('CYD_OGG_GAIN_OBS_OPEN',{'fixture':'GAIN_CHAIN','instance':38},{'generation':lambda x:int(x)+1})),
        ('wrong_resize_capacity',lambda:alter('CYD_OGG_GAIN_OBS_RETRY',{'fixture':'LIFE_MINUS6'},{'capacity':12288})),
        ('retry_replays_input',lambda:alter('CYD_OGG_GAIN_OBS_RETRY',{'fixture':'LIFE_MINUS6'},{'arguments_advanced_once':0})),
        ('missing_real_resize',lambda:alter('CYD_OGG_GAIN_OBS_RESIZE',{'fixture':'LIFE_MINUS6'},remove=True)),
        ('wrong_decode_stack',lambda:alter('CYD_OGG_GAIN_TASK_PROFILE',{'role':'decode'},{'stack':8192})),
        ('impossible_heap_block',lambda:alter('CYD_OGG_GAIN_MEMORY',{'fixture':'LIFE_PLUS48'},{'largest_internal':0})),
        ('decoder_leak',lambda:alter(end,{}, {'live_decoders':1})),
        ('driver_leak',lambda:alter(end,{}, {'driver_deleted':0})),
        ('no_actual_preload',lambda:alter(end,{}, {'preloads':0})),
        ('no_ordered_gain_metadata',lambda:alter(end,{}, {'gain_stamps':0})),
        ('wrong_first_capture_budget',lambda:alter('CYD_OGG_GAIN_CONTROL_CAPTURE_WAIT',{}, {'fixed_budget_ms':900000})),
    ]
    rejected=[]
    for name,make in controls:
        try:validate(make())
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory transcript accepted: '+name)
    need(all(sha(path)==digest for path,digest in before.items()),'original source and native evidence unchanged')
    result=dict(passed=True,original_transcript_accepted=True,rejected_controls=len(rejected),rejected=rejected,
        reader_sha256=sha(READER),oracle_sha256=sha(ORACLE),original_bindings=before,
        queued_gain_transition_proven=True,native_campaign_repeated=False,original_reports_modified=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,rejected_controls=len(rejected),native_campaign_repeated=False)))


if __name__=='__main__':
    sys.dont_write_bytecode=True
    main()
