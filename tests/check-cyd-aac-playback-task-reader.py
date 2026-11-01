"""Reject contradictory copies of a genuine terminal AAC task transcript.

This reads local data and reviewed canonical reader code. It starts no SDK,
emulator, decoder or archived program and changes no original native evidence.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/run-cyd-aac-playback-task-qemu.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--capture',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();native,out=args.capture.resolve(),args.output.resolve()
    need(native.is_relative_to(ROOT/'.build') and native.is_dir(),'actual local native capture')
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local witness directory')
    report=json.loads((native/'report.json').read_bytes())
    need(report['passed'] and report['completed'] and report['all_bound_inputs_current'],'original complete native qualification passed')
    need(READER.read_bytes()==(native/'sources/controller.py').read_bytes(),'exact executed canonical native reader')
    spec=importlib.util.spec_from_file_location('reviewed_actual_AAC_task_reader',READER)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    original=(native/'qemu.stdout.log').read_text('utf-8')+'\n'+(native/'qemu.stderr.log').read_text('utf-8')
    original=original.replace('\r\n','\n')
    measured=reader.validate_log(original,report['pcm_reference'])
    need(json.loads(json.dumps(measured))==report['measurements'],'whole original public reference/task transcript accepted')
    before={str(path):sha(path) for path in (READER,native/'report.json',native/'qemu.stdout.log',native/'qemu.stderr.log')}
    out.mkdir(parents=True)
    (out/'controller.py').write_bytes(Path(__file__).read_bytes())
    (out/'reader.py').write_bytes(READER.read_bytes())

    def alter(tag,match,values=None,remove=False):
        lines=original.splitlines()
        for index,line in enumerate(lines):
            if not line.startswith(tag+' '):continue
            pairs=[part.split('=',1) for part in line[len(tag)+1:].split()];fields=dict(pairs)
            if not all(fields.get(key)==str(value) for key,value in match.items()):continue
            if remove:del lines[index]
            else:
                need(set(values)<=set(fields),'control changes an actual measured field')
                for key,value in values.items():fields[key]=str(value(fields[key]) if callable(value) else value)
                lines[index]=tag+' '+' '.join(key+'='+fields[key] for key,_ in pairs)
            changed='\n'.join(lines);need(changed!=original,'contradiction changed the original observation');return changed
        raise ValueError('requested genuine witness missing: '+tag)

    case='CYD_AAC_TASK_CASE';end='CYD_AAC_TASK_COMPLETE';run='CYD_AAC_TASK_PCM_RUN'
    controls=[
        ('public_AAC_Plus_disabled',lambda:alter('CYD_AAC_TASK_OBS_OPEN',{}, {'aac_plus':0})),
        ('NULL_public_configuration',lambda:alter('CYD_AAC_TASK_OBS_OPEN',{}, {'cfg_size':0})),
        ('ADTS_configuration_disabled',lambda:alter('CYD_AAC_TASK_OBS_OPEN',{}, {'no_adts_header':1})),
        ('missing_HEv2_maintenance',lambda:alter(case,{'fixture':'AAC5','id':'T2'},remove=True)),
        ('core_only_HE_length',lambda:alter(case,{'fixture':'AAC3','id':'T0'},{'pcm_bytes':57344})),
        ('lost_PS_complete_hash',lambda:alter(case,{'fixture':'AAC5','id':'T0'},{'sha256':'0'*64})),
        ('wrong_complete_run_hash',lambda:alter(run,{'fixture':'AAC4'},{'sha256':'0'*64})),
        ('wrong_queued_sample_rate',lambda:alter(run,{'fixture':'AAC3'},{'rate':22050})),
        ('duplicated_mono_layout',lambda:alter(run,{'fixture':'AAC5'},{'channels':1})),
        ('Opus_header_gain_leaks_into_AAC',lambda:alter(case,{'fixture':'AAC0','id':'T0'},{'header_zero':0})),
        ('false_nominal_source_label',lambda:alter('CYD_AAC_TASK_STATE_INFO',{}, {'source_AOT_inferred':1})),
        ('PCM_metadata_not_marked',lambda:alter('CYD_AAC_TASK_STATE_INFO',{}, {'format_is_pcm':0})),
        ('actual_PCM_formatter_loses_label',lambda:alter('CYD_AAC_TASK_STATE_INFO',{'state_current':1},{'pcm_label':0})),
        ('reference_core_only_HE',lambda:alter('CYD_AAC_REFERENCE_CASE',{'index':3},{'pcm_bytes':57344})),
        ('reference_HEv2_hash_changed',lambda:alter('CYD_AAC_REFERENCE_CASE',{'index':5},{'sha256':'0'*64})),
        ('reference_uses_private_reset_hook',lambda:alter('CYD_AAC_REFERENCE_COMPLETE',{}, {'reset_hooks':1})),
        ('reference_not_isolated',lambda:alter('CYD_AAC_REFERENCE_COMPLETE',{}, {'production_tasks':1})),
        ('missing_continuous_observation',lambda:alter(case,{'fixture':'LATE_HEV2','schedule':1},remove=True)),
        ('wrong_continuous_reference_binding',lambda:alter(case,{'fixture':'LC_RATE','schedule':0},{'reference':0})),
        ('late_stock_observation_relabelled_nominal',lambda:alter(case,{'fixture':'LATE_HEV2','schedule':0},{'observed_only':0})),
        ('partial_transport_reached_EOF',lambda:alter('CYD_AAC_TASK_CONTROL_TRANSPORT_HELD',{'fixture':'AAC5'},{'position':2787})),
        ('wrong_independent_ADTS_boundary',lambda:alter('CYD_AAC_TASK_FIXTURE',{'fixture':'AAC0'},{'hold_after_frame':2})),
        ('held_read_not_genuine',lambda:alter('CYD_AAC_TASK_CONTROL_TRANSPORT_HELD',{}, {'genuine_read':0})),
        ('Stop_discard_sequence_mismatch',lambda:alter('CYD_AAC_TASK_CONTROL_STOP_QUIET',{'fixture':'AAC1'},{'discard_sequence':lambda value:int(value)+1})),
        ('Stop_output_keeps_writing',lambda:alter('CYD_AAC_TASK_CONTROL_STOP_QUIET',{'fixture':'AAC2'},{'driver_writes':lambda value:int(value)+1})),
        ('Stop_input_owner_still_active',lambda:alter('CYD_AAC_TASK_CONTROL_STOP_QUIET',{'fixture':'AAC4'},{'input_reading':1})),
        ('Stop_emits_EOF',lambda:alter('CYD_AAC_TASK_CONTROL_STOP_QUIET',{}, {'no_eof':0})),
        ('wrong_discard_owner_core',lambda:alter('CYD_AAC_TASK_CONTROL_DISCARD',{}, {'core':0})),
        ('stale_maintenance_token_accepted',lambda:alter(case,{'fixture':'AAC5','id':'T2'},{'stale_rejected':0})),
        ('EOF_not_publicly_drained',lambda:alter('CYD_AAC_TASK_OBS_CLOSE',{'instance':1},{'drained':0})),
        ('encoded_byte_not_consumed',lambda:alter('CYD_AAC_TASK_OBS_CLOSE',{'instance':1},{'input_consumed':lambda value:int(value)-1})),
        ('wrong_decoder_stack',lambda:alter('CYD_AAC_TASK_PROFILE',{'role':'decode'},{'stack':8192})),
        ('wrong_stream_core',lambda:alter('CYD_AAC_TASK_PROFILE',{'role':'stream'},{'core':1})),
        ('public_decoder_leak',lambda:alter(end,{}, {'closes':59})),
        ('public_client_leak',lambda:alter(end,{}, {'http_cleanup':59})),
        ('public_driver_leak',lambda:alter(end,{}, {'driver_deleted':0})),
        ('missing_real_preload',lambda:alter(end,{}, {'preloads':0})),
        ('missing_ordered_AAC_layout',lambda:alter(end,{}, {'legacy_layout_stamps':0})),
        ('impossible_heap_block',lambda:alter('CYD_AAC_TASK_MEMORY',{}, {'largest_internal':0})),
        ('unsupported_conformance_claim',lambda:alter(end,{}, {'independent_codec_conformance':1})),
    ]
    rejected=[]
    for name,make in controls:
        try:reader.validate_log(make(),report['pcm_reference'])
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory original-data copy accepted: '+name)
    need(all(sha(path)==digest for path,digest in before.items()),'all original native evidence remains unchanged')
    result=dict(passed=True,original_transcript_accepted=True,rejected_controls=len(rejected),rejected=rejected,
        reader_sha256=sha(READER),original_bindings=before,native_campaign_repeated=False,
        original_reports_modified=False,independent_codec_conformance=False)
    (out/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,rejected_controls=len(rejected),native_campaign_repeated=False)))


if __name__=='__main__':
    sys.dont_write_bytecode=True
    main()
