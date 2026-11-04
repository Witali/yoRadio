"""Verify selected inert observations and current owned reader; no native tools."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def need(v,label):
    if not v:raise ValueError(label)
def load(p):return json.loads(p.read_bytes())
def pin(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true');args=parser.parse_args()
    manifest=load(HERE/'manifest.json')
    for name,expected in manifest['files'].items():need(pin(HERE/name)==expected,'exact result file '+name)
    bindings=load(HERE/'source-bindings.json');reader=ROOT/'tests/fixtures/family1_normalizer/records.py'
    need(pin(reader)=={k:bindings['files'][reader.relative_to(ROOT).as_posix()][k] for k in ('bytes','sha256')},'current owned reader is exact captured source')
    if args.require_current:
        for name,p in bindings['files'].items():need(pin(ROOT/name)=={k:p[k] for k in ('bytes','sha256')},'current source '+name)
    spec=importlib.util.spec_from_file_location('current_owned_normalizer_record_reader',reader);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    selected=load(HERE/'observations.json')['records'];need([x['line'] for x in selected]==sorted(set(x['line'] for x in selected)),'ordered exact selected line indexes')
    text='\n'.join(x['text'] for x in selected);expected=load(HERE/'expected.json');module.validate_gate(text,expected)
    rows=[(x['line'],*module.fields(x['text'])) for x in selected]
    choose=lambda tag:[(i,r) for i,t,r in rows if t==tag]
    need([r for i,r in choose('CYD_F1_TASK_PROFILE')]==[dict(role='stream',core=0,priority=3,stack=6144),dict(role='decode',core=1,priority=5,stack=16384),dict(role='output',core=1,priority=6,stack=4096)],'original task creation profiles')
    refs=choose('CYD_F1_REFERENCE_CASE');need([r['index'] for i,r in refs]==list(range(13)),'all direct-reference summaries')
    need(refs[12][1]['sha256']==expected['source_pcm']['sha256'] and refs[12][1]['pcm_bytes']==153600,'fresh complete F12 source summary')
    complete=choose('CYD_F1_REFERENCE_COMPLETE');need(len(complete)==1 and complete[0][1]==dict(cases=13,live=0,private_helpers=0,production_tasks=0,heap_integrity=1),'reference ownership complete')
    starts=choose('CYD_NORM_BEGIN');ends=choose('CYD_NORM_CASE');allwrites=choose('CYD_F1_WRITE_RETURN')
    need([r['call'] for i,r in allwrites]==list(range(1,153)),'all152 genuine source-write returns retained')
    generations=[]
    for (start,begin),(end,case) in zip(starts,ends):
        writes=[r for i,r in allwrites if start<i<end];need(len(writes)==76 and sum(r['data_bytes'] for r in writes)==153600,'whole per-case borrowed source span')
        need(len({r['source_generation'] for r in writes})==1,'one genuine generation per complete case');generations.append(writes[0]['source_generation'])
        for r in writes:
            need(r['before_status']==r['after_status']==r['result']==0 and r['before_bytes']==r['after_bytes']==32 and r['equal']==1 and r['core']==1 and r['priority']==6 and r['start_us']<=r['return_us'],'actual immutable borrowed source through real renderer')
            need(all(r[k]==0 for k in ('acquire_entry','acquire_return','pause_start','pause_return','pause_acquire','pause_requested','cancelling')),'ordinary complete source-write scope')
        links=[r for i,r in choose('CYD_F1_LINK') if start<i<end];need(len(links)==1 and links[0]==dict(fixture='active8_120',index=0,reference=12,channels=8,layout=1,gain_q8=1536,bytes=153600,sha256=expected['source_pcm']['sha256']),'whole original raw C8 source hash')
        pads=[r for i,r in choose('CYD_F1_RENDER_PADDING') if start<i<end];need(pads==[dict(fixture='active8_120',schedule=begin['case'],page_style=begin['case']-1,ordinal=begin['case'],phase='FLUSH',block_bytes=1024,logical_before=18432,wire_before=18432,logical_bytes=768,wire_bytes=1024,padding_bytes=256,zero_checked=1,core=1,priority=6)],'full logical tail and zero wire padding')
    need(len(set(generations))==2 and min(generations)>0,'distinct genuine generations')
    request=choose('CYD_NORM_REQUEST')[0][0];need(sum(r['data_bytes'] for i,r in allwrites if starts[0][0]<i<request)==5448*8*2,'reset request follows the actual complete first packet')
    link=load(HERE/'link-audit.json');need(link['passed'] and len(set(link['wraps']))==79 and len(link['sdk_wraps'])==32 and link['declared_target_wraps']==43 and link['normalizer_wraps']==4,'exact SDK32+target43+normalizer4 wraps')
    need(len(link['symbolic_edges'])==6 and all(e['sections'] and e['link_wraps_and_final_symbols_checked'] for e in link['symbolic_edges']),'six real forwarding symbol/relocation edges')
    print(json.dumps(dict(passed=True,data_only=True,cases=2,source_writes=152,current_sources_checked=len(bindings['files']) if args.require_current else 1,recorded_process_provenance_only=True,omitted_PCM_recomputed=False)))
if __name__=='__main__':main()
