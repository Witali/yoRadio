"""Inspect frozen pbuf EOF-prefix evidence without changing controller verdicts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

SUMMARY=re.compile(rb'^CYD_OPENETH_PBUF_FAILURE_SUMMARY total=(\d+) overflow=(\d+) used=(\d+) saturated=(\d+) table_bytes=(\d+) lock_bytes=(\d+)\r?$',re.M)
ENTRY=re.compile(rb'^CYD_OPENETH_PBUF_FAILURE index=(\d+) layer=(\d+) type=(\d+) length=(\d+) derived_allocation_bytes=(\d+) caller_pc=0x([0-9a-fA-F]{8}) count=(\d+) saturated=(\d+)\r?$',re.M)

def pin(path):
    body=Path(path).read_bytes();return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())

def parse(uart):
    summaries=list(SUMMARY.finditer(uart));entries=list(ENTRY.finditer(uart))
    tags=re.findall(rb'^CYD_OPENETH_PBUF_FAILURE(?:_SUMMARY)?[^\r\n]*',uart,re.M)
    assert len(tags)==len(summaries)+len(entries),'Malformed or unexpected probe line'
    if not summaries:
        assert not entries
        return None
    assert len(summaries)==1,'This full-stream campaign expects one diagnostic flush snapshot'
    names=('total','overflow','used','saturated','table_bytes','lock_bytes')
    summary=dict(zip(names,map(int,summaries[0].groups())))
    assert summary['table_bytes']==128 and summary['lock_bytes']==8
    assert 0<=summary['used']<=4 and 0<=summary['saturated']<=7
    assert all(0<=summary[k]<=0xffffffff for k in('total','overflow'))
    rows=[]
    for entry in entries:
        assert entry.start()>summaries[0].end(),'Entry precedes its snapshot summary'
        values=[int(v,16 if i==5 else 10)for i,v in enumerate(entry.groups())]
        row=dict(zip(('index','layer','type','length','derived_allocation_bytes','caller_pc','count','saturated'),values))
        assert all(0<=x<=0xffffffff for x in row.values())
        assert row['length']<=65535 and row['count']>0 and row['saturated'] in(0,1)
        rows.append(row)
    assert [x['index']for x in rows]==list(range(summary['used']))
    keys=[tuple(x[k]for k in('layer','type','length','derived_allocation_bytes','caller_pc'))for x in rows]
    assert len(set(keys))==len(keys),'Duplicate tuple in fixed table'
    assert summary['used']==4 or summary['overflow']==0,'Overflow requires a full table'
    assert not(summary['saturated']&1) or summary['total']==0xffffffff
    assert not(summary['saturated']&2) or summary['overflow']==0xffffffff
    assert bool(summary['saturated']&4)==any(x['saturated']for x in rows)
    assert all(not x['saturated']or x['count']==0xffffffff for x in rows)
    assert not(summary['saturated']&6) or summary['saturated']&1
    if not summary['saturated']:
        assert all(not x['saturated']for x in rows)
        assert summary['total']==summary['overflow']+sum(x['count']for x in rows)
    summary['entries']=rows
    return summary

def executable_sections(body):
    assert body[:6]==b'\x7fELF\x01\x01','Expected target ELF32 little endian'
    h=struct.unpack_from('<16sHHIIIIIHHHHHH',body)
    assert h[2]==94,'Expected Xtensa ELF'
    result=[]
    for index in range(h[12]):
        row=struct.unpack_from('<IIIIIIIIII',body,h[6]+index*h[11])
        if row[2]&4 and row[5]:result.append((row[3],row[3]+row[5]))
    return result

def inspect_pc(pc,elf,addr2line,objdump,ranges):
    assert any(start<=pc and pc+3<=end for start,end in ranges),'PC is outside executable target storage'
    symbol=subprocess.run([str(addr2line),'-f','-C','-i','-e',str(elf),hex(pc)],capture_output=True)
    assert symbol.returncode==0,'Target symbolization failed; private diagnostics withheld'
    lines=symbol.stdout.decode(errors='replace').splitlines()
    assert lines and len(lines)%2==0 and all(x!='??'for x in lines[::2]),'Unresolved call-site symbol'
    frames=[dict(function=lines[i],source=lines[i+1])for i in range(0,len(lines),2)]
    disasm=subprocess.run([str(objdump),'-d','--start-address='+hex(pc),'--stop-address='+hex(pc+3),str(elf)],capture_output=True)
    assert disasm.returncode==0,'Target call instruction inspection failed'
    text=disasm.stdout.decode(errors='replace')
    matches=re.findall(r'^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(call8|callx8)\s+([^\r\n]+)',text,re.M)
    assert len(matches)==1 and int(matches[0][0],16)==pc,'Captured PC does not identify an Xtensa call8/callx8 instruction'
    return dict(frames=frames,instruction=dict(address=pc,encoding=matches[0][1],mnemonic=matches[0][2],operand=matches[0][3].strip()),
                disassembly_sha256=hashlib.sha256(disasm.stdout).hexdigest(),
                scope='Instruction and source symbolization; the SDK linked-target qualification independently proves wrapper reach.')

def attach_verified_tcp_sites(snapshot,link_report,elf):
    proof=json.loads(link_report.read_bytes())
    assert proof['passed']is True and proof['wrapper_real_call_dominates_exits_without_cycle']is True
    assert {k:proof['elf'][k]for k in('bytes','sha256')}==pin(elf)
    assert proof['verifier']['sha256']=='d4e636beb193d9a52460f587300cc07cae4b93285e3b8b3a04cd7a7337dcd90b'
    sites=proof['tcp_out_sites'];assert len(sites)==4
    assert len({row['call']['site']for row in sites})==4
    for row in sites:
        assert '__wrap_pbuf_alloc'in row['call']['target']['names']
        assert row['call']['site']==row['call']['normalized_return_pc_expected']
    if snapshot:
        for entry in snapshot['entries']:
            matches=[row for row in sites if row['call']['site']==entry['caller_pc']]
            assert len(matches)<=1
            entry['verified_tcp_call']=matches[0]if matches else None
            entry['tcp_subset_scope']='Matched exact qualified TCP call-site PC'if matches else 'Outside the four verified TCP sites; retain as a separate observation'
    return proof

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in('run','elf','addr2line','objdump','link-report','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    report=json.loads((args.run/'report.json').read_bytes());uart=(args.run/'qemu.log').read_bytes()
    assert report['state']in('TERMINAL_PASS','TERMINAL_NONPASS')
    assert hashlib.sha256(uart).hexdigest()==report['uart_sha256']
    assert report['qemu_sha256']=='28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4'
    assert report['runner_sha256']=='ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f'
    snapshot=parse(uart);ranges=executable_sections(args.elf.read_bytes())
    if snapshot:
        for row in snapshot['entries']:
            row['target_pc']=inspect_pc(row['caller_pc'],args.elf,args.addr2line,args.objdump,ranges)
    attach_verified_tcp_sites(snapshot,args.link_report,args.elf)
    health={name:report.get(name)for name in('first_active_health','health_during_webui','eof_health','post_eof_health','last_reachable_health')}
    observations={name:None if not isinstance(value,dict)else {k:value.get(k)for k in('uptime_ms','minimum_heap','allocation_failures','last_allocation_failure')}for name,value in health.items()}
    result=dict(controller_state=report['state'],controller_reason=report.get('reason'),physical_tested=False,
        inputs=dict(report=pin(args.run/'report.json'),uart=pin(args.run/'qemu.log'),elf=pin(args.elf),addr2line=pin(args.addr2line),objdump=pin(args.objdump),link_report=pin(args.link_report)),
        attribution_available=snapshot is not None,pbuf_pcm_flush_prefix=snapshot,health_observations=observations,
        pcm_sha256=report.get('pcm_sha256'),pcm_flushes=report.get('pcm_probe_flushes'),
        interpretation='The probe is a cumulative PCM-flush prefix. Later EOF/WebUI/peer-close heap counts are independent snapshots, not an atomic common observation. NULL is not automatically a heap failure; retain non-RAM/overflow/saturation, unwrapped paths and unexplained differences. This report never promotes a controller NONPASS.')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(controller_state=report['state'],attribution_available=snapshot is not None,
        pbuf_prefix_total=None if snapshot is None else snapshot['total'],buckets=None if snapshot is None else snapshot['used'],
        eof_allocation_failures=(report.get('eof_health')or{}).get('allocation_failures'))))

if __name__=='__main__':main()
