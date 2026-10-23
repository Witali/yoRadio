"""Strict finite owned floor0 publication records; no process or C execution."""
import hashlib
import json
from pathlib import Path
import re

PREFIX='CYD_VORBIS_OWNED_FLOOR0_'
SETUP='6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
ABI='e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'
ORIGINAL=tuple(f'floor0-{family}-r0-s{s}-l{l}' for family in ('even6','odd5') for s,l in ((64,256),(256,2048),(64,2048)))
IDS=ORIGINAL+tuple(x.replace('-r0-','-r0-minp1-') for x in ORIGINAL)


def need(ok,reason):
    if not ok:raise ValueError(reason)


def digest(raw):return hashlib.sha256(raw).hexdigest()


def contract_shape(contract):
    m=contract['model']
    need(contract['contract_sha256']==digest(json.dumps(m,sort_keys=True,separators=(',',':')).encode()),'contract_model_identity')
    need(m['schema']=='owned-floor0-fixtures-v1' and m['case_count']==len(m['cases'])==12
         and m['protocol_lines']==32 and m['pairs']==[[i,i+6] for i in range(6)]
         and tuple(c['id'] for c in m['cases'])==IDS and m['publication_bytes']==40,'exact12_original_equivalent_cases')
    need(m['setup_sha256']==SETUP and m['ABI_sha256']==ABI,'unchanged_production_parser_ABI')
    for i,c in enumerate(m['cases']):
        even=i%6<3
        need((c['order'],c['rate'],c['barkmap'],c['ampbits'],c['ampdB'],c['books'],c['total_books'],c['parse_bits'])==
             ((6,48000,64,6,60,[2],3,66) if even else (5,48000,128,8,60,[2,3],4,74)), 'exact_original_floor_configuration')
        need(c['end_bit']-c['first_bit']==c['parse_bits'] and c['first_bit']>=0 and
             c['end_bit']<=c['setup_bytes']*8 and c['group']==('original' if i<6 else 'minp1'), 'exact_absolute_span_and_source_group')


def load_contract(path,*,expected_sha256):
    raw=Path(path).read_bytes()
    need(re.fullmatch('[0-9a-f]{64}',expected_sha256) and digest(raw)==expected_sha256,'reviewed_contract_file_identity')
    value=json.loads(raw);contract_shape(value);return value


def validate_log(log,contract,*,returncode,timed_out,interrupted,force_stopped=False):
    contract_shape(contract)
    need(type(returncode) is int and returncode==0 and timed_out is False and interrupted is False and force_stopped is False,
         'normal_actual_terminal0_required')
    need(type(log) is str and not re.search(r'Guru Meditation|CORRUPT\s*HEAP|assert failed|abort\(\)|Brownout|Rebooting',log,re.I),
         'target_panic_or_reset')
    rows=[]
    for line in log.replace('\r\n','\n').splitlines():
        if PREFIX not in line:continue
        need(line.startswith(PREFIX),'native_prefix_only')
        kind,separator,rest=line[len(PREFIX):].partition(' ')
        need(separator and kind!='FAILURE','explicit_unit_failure')
        parts=rest.split(' ')
        need(all(re.fullmatch('[a-z_]+=[^ =\\s]+',part) for part in parts),'strict_key_value_record')
        fields=dict(p.split('=',1) for p in parts)
        need(len(fields)==len(parts),'duplicate_fields')
        rows.append((kind,fields))
    need(len(rows)==32,'all32_publication_events_required')
    cursor=0
    def event(kind,expected):
        nonlocal cursor
        observed,fields=rows[cursor];cursor+=1
        need(observed==kind and fields=={k:str(v) for k,v in expected.items()},'event_fields_or_order:'+kind)
        return fields
    m=contract['model']
    event('BEGIN',dict(contract=contract['contract_sha256'],cases=12,pairs=6,core=0))
    publications=[]
    for i,c in enumerate(m['cases']):
        values=dict(case=i,id=c['id'],group=c['group'],first=c['first_bit'],end=c['end_bit'],consumed=c['parse_bits'],
            total_books=c['total_books'],order=c['order'],rate=c['rate'],barkmap=c['barkmap'],ampbits=c['ampbits'],ampdb=c['ampdB'],
            numbooks=len(c['books']),books=','.join(map(str,c['books'])),allocated=40,live=1,vi_unchanged=1,ci_unchanged=1,guards=1,core=0)
        observed=event('FIELDS',values)
        publications.append(tuple(observed[key] for key in ('order','rate','barkmap','ampbits','ampdb','numbooks','books')))
        event('CASE',dict(case=i,id=c['id'],live=0,guards=1,core=0))
    for a,b in m['pairs']:
        need(publications[a]==publications[b],'actual_published_original_equivalent_equality')
        event('PAIR',dict(first=a,second=b,publication_equal=1,span_equal=1,bytes=40,core=0))
    event('COMPLETE',dict(cases=12,pairs=6,live=0,core=0))
    need(cursor==len(rows),'no_trailing_publication_records')
    return dict(schema='owned-floor0-observed-v1',cases=12,pairs=6,protocol_lines=32,publication_bytes=40,
        publication_fields_matched=True,exact_consumption_matched=True,guards_and_normal_release_matched=True,
        vendor_backend_qualified=False,curve_qualified=False,PCM_qualified=False,full_G6_qualified=False,physical_qualified=False)
