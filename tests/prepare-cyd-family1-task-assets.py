"""Generate lossless immutable span descriptors for the new CYD task diagnostic."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT=ROOT/'tests/prepare-cyd-family1-task-contract.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def prepare():
    spec=importlib.util.spec_from_file_location('current_family1_task_contract',CONTRACT)
    data=importlib.util.module_from_spec(spec);spec.loader.exec_module(data)
    contract,original,source=data.contracts();blob,storage=data.compact_assets(contract,original,source)
    rows=['#pragma once'];views={};entries={row['id']:row for row in contract['entries']}
    for index,view in enumerate(storage['views']):
        name='view_'+str(index);reference=view['reference'];key=(reference,view['style'],view['gain_q8']);views[key]=name
        spans=','.join('{'+str(span['offset'])+','+str(span['bytes'])+'}' for span in view['spans'])
        rows.append('static const span_t '+name+'_spans[]={'+spans+'};')
        if reference<13:
            entry=entries[reference];needed=entry['needed_streams'];kind='FAMILY1';channels=entry['channels'];layout=1
            frames=entry['logical_frames'];hold=entry['hold_offset'];stream_count=entry['streams'];coupled=entry['coupled']
            maximum=max(page['bytes'] for page in source['fixtures'][reference][view['style']]['pages']);label=entry['name']
        else:
            pin=data.LEGACY[reference];body=(ROOT/pin['path']).read_bytes();label=kind=pin['name'];channels=2;layout=0
            frames=528000;needed=[0];stream_count=1;coupled=1;at=maximum=0
            while at<len(body):
                n=body[at+26];end=at+27+n+sum(body[at+27:at+27+n]);maximum=max(maximum,end-at);at=end
            need(at==len(body),'whole unchanged legacy physical extent');hold=0
        rows.append('static const uint8_t '+name+'_needed[]={'+','.join(map(str,needed or [0]))+'};')
        fields=[name+'_spans',str(len(view['spans'])),str(view['bytes']),json.dumps(label),json.dumps(kind),
            str(reference),str(channels),str(layout),str(len(needed)),str(stream_count),str(coupled),name+'_needed',
            str(frames),str(hold),str(maximum),str(view['gain_q8'])]
        rows.append('static const link_t '+name+'={'+','.join(fields)+'};')
    def literal(case):
        pointers=[]
        for link in case['links']:
            style='split' if case['page_style'] and link['reference']<13 else 'whole'
            pointers.append('&'+views[(link['reference'],style,link['gain_q8'])])
        return '{'+','.join([json.dumps(case['name']),'{'+','.join(pointers)+'}',str(len(pointers)),
            str(case['volume']),str(case['schedule']),str(case['page_style'])])+'}'
    lifecycles=[case for case in contract['cases'] if case['id']=='T0']
    rows.append('static const fixture_t lifecycles[]={'+','.join(literal(case) for case in lifecycles)+'};')
    full=[]
    for life in lifecycles:
        cases=[case for case in contract['cases'] if case['name']==life['name'] and case['id']=='FULL']
        need(len(cases)==3,'all full schedules present');full.append('{'+','.join(literal(case) for case in cases)+'}')
    rows.append('static const fixture_t full_sets[][3]={'+','.join(full)+'};')
    for name,case_id,count in [('map_cases','MAP',16),('chains','CHAIN',2)]:
        cases=[case for case in contract['cases'] if case['id']==case_id];need(len(cases)==count,'complete declared fixture group')
        rows.append('static const fixture_t '+name+'[]={'+','.join(literal(case) for case in cases)+'};')
    header='\n'.join(rows)+'\n';size_header='#pragma once\n#define F1_ASSET_BYTES '+str(len(blob))+'u\n'
    contract=dict(contract,immutable_storage=storage)
    return contract,blob,header,size_header,source


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--headers-only',action='store_true');args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local asset preparation')
    contract,blob,header,size_header,source=prepare();out.mkdir(parents=True)
    for name,body in [('reference.h',header),('asset_size.h',size_header)]:
        (out/name).write_text(body,encoding='utf-8',newline='\n')
    for name,value in [('contract.json',contract),('fixture-preparation.json',source)]:
        (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
    if not args.headers_only:(out/'fixtures.bin').write_bytes(blob)
    print(json.dumps(dict(passed=True,prepared_only=True,asset_bytes=len(blob),asset_sha256=hashlib.sha256(blob).hexdigest(),
        descriptor_bytes=contract['immutable_storage']['descriptor_bytes'],fixture_assets_written=not args.headers_only,
        target_executed=False,actual_image_fit_measured=False)))


if __name__=='__main__':main()
