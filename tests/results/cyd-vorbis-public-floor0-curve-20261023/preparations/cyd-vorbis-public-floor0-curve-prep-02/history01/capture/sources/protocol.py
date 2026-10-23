"""Strict complete public-curve evidence protocol; never execute target/math/codec."""
import hashlib
import json
from pathlib import Path
import re
import struct

PREFIX='CYD_PUBLIC_TREMOR_CURVE_'


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(data):return hashlib.sha256(data).hexdigest()


def fnv(data):
    value=2166136261
    for byte in data:value=((value^byte)*16777619)&0xffffffff
    return value


def load_contract(path,expected_sha256):
    data=Path(path).read_bytes()
    need(sha(data)==expected_sha256,'Exact root-reviewed derived contract bytes')
    contract=json.loads(data)
    need(contract['schema']=='public-floor0-curve-contract-v1','Public curve contract schema')
    model=contract['model']
    need(sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())==contract['model_sha256'],'Exact derived model identity')
    need(model['counts']['cases']==6 and model['counts']['packets']==84 and model['counts']['calls']==168 and
         len(model['calls'])==168 and len(model['cases'])==6 and model['counts']['bins']==sum(row['words'][3] for row in model['calls']), 'Complete6/84/168 derived counts')
    for index,row in enumerate(model['calls']):
        w=row['words']
        need(row['call']==index and len(w)==31 and w[:3]==[index//28,(index//2)%14,index%2] and
             w[3] in (32,128,1024) and w[4] in (5,6) and w[5] in (64,128) and w[7:9]==[60,24000] and
             all(0<value<3*(1<<24) for value in w[9:9+w[4]]) and all(a<b for a,b in zip(w[9:8+w[4]],w[10:9+w[4]])) and
             all(0<abs(value)<=768 for value in w[15:]) and fnv(struct.pack('<31i',*w))==row['input_fnv32'],'Exact valid original public descriptor')
    return contract


def control_lines(model):
    out=[]
    for index,value in enumerate((-768,-256,0,256,768)):
        output=(value*2147483647)//32768
        out.append(f'{PREFIX}CONTROL multiply={index} input={value} output={output} core=0')
    out.append(f'{PREFIX}CONTROL zero_residue=1 bins={model["calls"][0]["words"][3]} core=0')
    return out


def call_line(row):
    w=row['words']
    return (f'{PREFIX}CALL call={row["call"]} case={w[0]} packet={w[1]} channel={w[2]} n={w[3]} m={w[4]} '
            f'ln={w[5]} amp_q4={w[6]} input={row["input_fnv32"]:08x} core=0')


def complete_marker(contract):
    return f'{PREFIX}COMPLETE calls=168 bins={contract["model"]["counts"]["bins"]} core=0\n'


def validate_log(log,contract,*,returncode,timed_out,interrupted):
    need(type(returncode) is int and returncode==0 and timed_out is False and interrupted is False,'Actual owned terminal0 without timeout/interruption')
    need(not re.search(r'CYD_PUBLIC_TREMOR_CURVE_FAILURE|Guru Meditation|CORRUPT\s*HEAP|assert failed|abort\(\)|Brownout|Rebooting',log,re.I),'No actual failure/panic/reset')
    lines=[line for line in log.replace('\r\n','\n').splitlines() if PREFIX in line]
    need(all(line.startswith(PREFIX) for line in lines),'Unprefixed/mixed protocol text')
    model=contract['model'];position=0
    def take(expected):
        nonlocal position
        need(position<len(lines) and lines[position]==expected,'Exact complete ordered public curve event: '+expected[:100])
        position+=1
    take(f'{PREFIX}BEGIN cases=6 packets=84 calls=168 bins={model["counts"]["bins"]} model={contract["model_sha256"]} core=0')
    for line in control_lines(model):take(line)
    calls=[]
    for row in model['calls']:
        take(call_line(row));call=row['call'];w=row['words'];parts=[]
        for offset in range(0,w[3],16):
            need(position<len(lines),'Missing full curve chunk')
            match=re.fullmatch(re.escape(PREFIX)+rf'OUT call={call} offset={offset} count=16 hex=([0-9a-f]{{128}}) core=0',lines[position])
            need(match is not None,'Exact16-bin little-endian complete curve chunk')
            parts.append(bytes.fromhex(match[1]));position+=1
        value=b''.join(parts)
        need(len(value)==w[3]*4,'Every full half-block curve byte')
        values=list(struct.unpack('<'+'i'*w[3],value))
        need(not any(values[16:]),'Zero residue tail stays exactly zero')
        for source,actual in zip(w[15:],values[:16]):
            bound=(abs(source)*2147483647+32767)//32768
            need(-bound<=actual<=bound and (actual==0 or (actual>0)==(source>0)),'Bounded sign-preserving public curve output')
        take(f'{PREFIX}END call={call} bins={w[3]} output={fnv(value):08x} canary=1 lsp=1 tail=1 core=0')
        calls.append(dict(call=call,case=w[0],packet=w[1],channel=w[2],bins=w[3],sha256=sha(value),bytes=len(value),values=value))
    take(complete_marker(contract).rstrip('\n'))
    need(position==len(lines),'No trailing/repeated/extra public curve events')
    need(sum(row['bins'] for row in calls)==model['counts']['bins'],'All full half-block bins')
    return dict(cases=6,packets=84,calls=168,bins=model['counts']['bins'],curve_bytes=sum(row['bytes'] for row in calls),
        protocol_lines=len(lines),core=0,public_function_evaluated=True,target_codec_executed=False,reference_decoder_executed=False,
        PCM_computed=False,numeric_qualified=False,full_G6_qualified=False,curves=calls)
