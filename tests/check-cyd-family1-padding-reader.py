"""Read-only padding parser contract controls; no native observations fabricated.

These synthetic metadata vectors use the declared512-sample/S16 DMA geometry
and complete prepared input extents. They are not native02's unrecorded bytes.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/read-cyd-family1-task-log.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--contract',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();source=args.contract.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists() and source.is_relative_to(ROOT/'.build'),'fresh local contract-control result')
    contract=json.loads(source.read_bytes());spec=importlib.util.spec_from_file_location('reviewed_current_padding_reader',READER)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    entry=next(row for row in contract['entries'] if row['id']==0);case=next(row for row in contract['cases'] if row['reference']==0 and row['id']=='T0')
    need(entry['channels']==3 and entry['pcm_bytes']==57600 and entry['logical_frames']==9600,'independent full source extent anchor')
    small=dict(entries=[entry],cases=[case])
    record=dict(fixture='default3',schedule=0,page_style=0,ordinal=1,phase='FLUSH',block_bytes=1024,
        logical_before=18432,wire_before=18432,logical_bytes=768,wire_bytes=1024,padding_bytes=256,zero_checked=1,core=1,priority=6)
    reader.validate_padding_records([record],small)
    source_tag='CYD_F1_LINK';render_tag='CYD_F1_RENDER_LINK';padding_tag='CYD_F1_RENDER_PADDING';case_tag='CYD_F1_TASK_CASE'
    rows=[(source_tag,{}),(render_tag,{}),(padding_tag,record),(case_tag,{})]
    reader.validate_padding_flow(rows,small)
    # A second independent arithmetic anchor:528000 complete stereo frames
    # produce1056000 logical mono bytes and require768 trailing wire bytes.
    long_entry=next(row for row in contract['entries'] if row['id']==11);long_case=next(row for row in contract['cases'] if row['reference']==11 and row['id']=='T0')
    long_record=dict(record,fixture='full120',logical_before=1055744,wire_before=1055744,logical_bytes=256,padding_bytes=768)
    reader.validate_padding_records([long_record],dict(entries=[long_entry],cases=[long_case]))
    rejected=[]
    def reject(name,action):
        try:action()
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory parser contract accepted: '+name)
    for name,key,value in [
        ('wrong_surplus','padding_bytes',258),('nonzero_surplus_reported','zero_checked',0),
        ('wrong_phase','phase','PCM'),('wrong_configured_block','block_bytes',512),
        ('extra_DMA_block','wire_bytes',2048),('missing_surplus','padding_bytes',0),
        ('wrong_logical_tail','logical_bytes',766),('early_logical_position','logical_before',18430),
        ('earlier_wire_surplus','wire_before',19456),('duplicate_ordinal','ordinal',2),
        ('wrong_owner_core','core',0),('wrong_owner_priority','priority',5),
        ('wrong_fixture','fixture','default6'),('wrong_schedule','schedule',1),
        ('wrong_page_style','page_style',1),('oversized_surplus','padding_bytes',1026),
    ]:
        changed=dict(record,**{key:value});reject(name,lambda changed=changed:reader.validate_padding_records([changed],small))
    reject('missing_padding_record',lambda:reader.validate_padding_records([],small))
    reject('extra_padding_record',lambda:reader.validate_padding_records([record,record],small))
    for name,changed in [
        ('before_source_end',[(padding_tag,record),(source_tag,{}),(render_tag,{}),(case_tag,{})]),
        ('before_render_end',[(source_tag,{}),(padding_tag,record),(render_tag,{}),(case_tag,{})]),
        ('after_case_terminal',[(source_tag,{}),(render_tag,{}),(case_tag,{}),(padding_tag,record)]),
        ('twice_in_final_phase',rows[:3]+[(padding_tag,record)]+rows[3:]),
        ('logical_span_after_padding',rows[:3]+[(source_tag,{})]+rows[3:]),
        ('no_case_terminal',rows[:-1]),
    ]:reject(name,lambda changed=changed:reader.validate_padding_flow(changed,small))
    need(len(rejected)==24,'all declared wrong/early/nonzero/size/count controls executed')
    out.mkdir(parents=True);(out/'reader.py').write_bytes(READER.read_bytes());(out/'controller.py').write_bytes(Path(__file__).read_bytes())
    report=dict(passed=True,synthetic_parser_contract_vectors=True,native02_failing_driver_bytes_observed=False,
        original_native_evidence_modified=False,SDK_started=False,QEMU_started=False,production_sources_modified=False,
        complete_extent_anchors=[dict(logical_mono_bytes=19200,wire_tail_bytes=1024,padding_bytes=256),
            dict(logical_mono_bytes=1056000,wire_tail_bytes=1024,padding_bytes=768)],
        rejected_controls=len(rejected),rejected=rejected,reader_sha256=hashlib.sha256(READER.read_bytes()).hexdigest(),
        contract=dict(path=source.relative_to(ROOT).as_posix(),bytes=source.stat().st_size,sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,rejected_controls=24,synthetic_parser_contract_vectors=True,native02_failing_driver_bytes_observed=False)));return 0


if __name__=='__main__':raise SystemExit(main())
