"""Freeze all public raw banks from the completed independent host evidence."""
import hashlib,importlib.util,json,struct
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'.build/cyd-vorbis-block-banks-01'
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(data): return hashlib.sha256(data).hexdigest()
def load(path): return json.loads(Path(path).read_text())

def main():
    dual=ROOT/'.build/cyd-vorbis-block-host-01/report.json'
    reference=ROOT/'.build/cyd-vorbis-block-xiph-01/report.json'
    rate=ROOT/'.build/cyd-vorbis-block-rate-host-01/report.json'
    d,x,r=map(load,(dual,reference,rate))
    assert d['completed'] and not d['passed'] and len(d['cases'])==108 and len(d['failures'])==30
    assert x['completed'] and x['reference_corpus_qualified'] and not x['failures'] and len(x['cases'])==108
    assert x['original_report_sha256']==sha(dual) and sum(c['native_comparison_qualified'] for c in x['cases'])==78
    assert r['completed'] and r['passed'] and len(r['cases'])==36 and not r['failures']
    for name,code in (('host',1),('xiph',0),('rate-host',0)):
        path=ROOT/('.build/cyd-vorbis-block-'+name+'-01-command.json'); receipt=load(path)
        assert receipt['status']=='TERMINAL' and receipt['returncode']==code
    helper=ROOT/'.build/cyd-vorbis-block-host-driver-01.py'
    assert sha(helper)==d['driver_sha256']==r['driver_sha256']
    spec=importlib.util.spec_from_file_location('reviewed_block_host',helper)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    matrices=[ROOT/'.build/cyd-vorbis-block-candidates-01/candidates.json',
              ROOT/'.build/cyd-vorbis-minimal-block-prep-01/generated01/matrix.json',
              ROOT/'.build/cyd-vorbis-minimal-block-rate-prep-01/generated01/matrix.json']
    realistic,minimal,rebound=map(load,matrices)
    assert len(realistic['cases'])==72 and len(minimal['cases'])==len(rebound['cases'])==36
    for a,b in zip(minimal['cases'],rebound['cases']):
        assert (a['short'],a['long'])==(b['short'],b['long']) and a['rate']==48000 and b['rate']==192000
        aa=module.packets((matrices[1].parent/a['ogg']).read_bytes())
        bb=module.packets((matrices[2].parent/b['ogg']).read_bytes())
        corrected=bytearray(aa[0]['data']); struct.pack_into('<I',corrected,12,192000)
        assert bytes(corrected)==bb[0]['data'] and aa[1:]==bb[1:]
    banks=[]; arrays=[]
    def array(kind,name,values):
        return 'static const '+kind+' '+name+'[] = {\n'+',\n'.join(','.join(str(v) for v in values[i:i+32]) for i in range(0,len(values),32))+'\n};\n'
    required={(1<<s,1<<l) for s in range(6,14) for l in range(s,14)}
    for bank_name,matrix,matrix_path,source_rate in (
        ('identity',realistic,matrices[0],192000),('transitions',realistic,matrices[0],192000),
        ('minimal',minimal,matrices[1],48000)):
        cases=[c for c in matrix['cases'] if c.get('family',bank_name)==bank_name]
        assert len(cases)==36 and {(c['short'],c['long']) for c in cases}==required
        first=module.packets((matrix_path.parent/cases[0]['ogg']).read_bytes())
        info,setup=first[0]['data'][7:],first[2]['data'][7:]
        packets=[row['data'] for row in first[3:]]; modes=cases[0]['mode_flags']; offsets=[0]; audio=b''
        assert len(info)==23 and info[4]==2 and struct.unpack_from('<I',info,5)[0]==source_rate
        for packet in packets: audio+=packet; offsets.append(len(audio))
        assert len(packets)==len(modes)=={'identity':68,'transitions':70,'minimal':14}[bank_name]
        for case in cases:
            parsed=module.packets((matrix_path.parent/case['ogg']).read_bytes())
            assert parsed[2]['data'][7:]==setup and [row['data'] for row in parsed[3:]]==packets
            assert case['mode_flags']==modes
            ident=bytearray(parsed[0]['data'][7:]); ident[21]=info[21]
            assert bytes(ident)==info
        stem='bank_'+bank_name
        for kind,suffix,values in (('uint8_t','info',info),('uint8_t','setup',setup),('uint8_t','audio',audio),
                                  ('uint8_t','modes',modes),('uint32_t','offsets',offsets)):
            arrays.append(array(kind,stem+'_'+suffix,values))
        banks.append(dict(name=bank_name,source_rate=source_rate,target_rate=192000,packet_count=len(packets),
            info_sha256=digest(info),setup_sha256=digest(setup),audio_sha256=digest(audio),
            info_size=len(info),setup_size=len(setup),audio_size=len(audio),offsets=offsets,mode_flags=modes,
            source_matrix=str(matrix_path.relative_to(ROOT)),source_matrix_sha256=sha(matrix_path)))
    manifest=dict(schema='public-vorbis-block-frozen-banks-v1',banks=banks,
        host_reference_report_sha256=sha(reference),original_dual_report_sha256=sha(dual),
        original_dual_reference_passed=False,xiph_cases_qualified=108,native_cases_compared=78,native_floor_refusals=30,
        minimal_rate_rebind_report_sha256=sha(rate),minimal_rate_rebind_qualified=True,
        matrix_pins={str(p.relative_to(ROOT)):sha(p) for p in matrices},
        raw_payload_prefix_stripped=7,target_executed=False,full_G6_qualified=False)
    manifest_data=(json.dumps(manifest,indent=2)+'\n').encode(); manifest_sha=digest(manifest_data)
    header='#pragma once\n#include "banks_contract.h"\n#define BLOCK_MATRIX_DATA_MANIFEST_SHA256 "'+manifest_sha+'"\n'+''.join(arrays)
    header+='static const block_bank_t block_banks[3] = {\n'
    for bank in banks:
        stem='bank_'+bank['name']; fields=['.name="'+bank['name']+'"','.source_rate='+str(bank['source_rate'])+'U']
        fields += ['.'+field+'='+stem+'_'+field for field in ('info','setup','audio','modes','offsets')]
        fields += ['.'+field+'_size=sizeof('+stem+'_'+field+')' for field in ('info','setup','audio')]
        fields += ['.modes_count=sizeof('+stem+'_modes)/sizeof('+stem+'_modes[0])',
                   '.offsets_count=sizeof('+stem+'_offsets)/sizeof('+stem+'_offsets[0])','.packet_count='+str(bank['packet_count'])+'U']
        header+='    {'+','.join(fields)+'},\n'
    header+='};\n'
    assert not OUT.exists(); OUT.mkdir(); (OUT/'banks.json').write_bytes(manifest_data)
    (OUT/'banks_data.h').write_bytes(header.encode())
    (OUT/'freeze.json').write_text(json.dumps(dict(manifest_sha256=manifest_sha,banks_header_sha256=sha(OUT/'banks_data.h'),
        freeze_script_sha256=sha(__file__),raw_banks=3,cases=108,paired_packets=5472,minimal_rate_rebind_qualified=True,
        target_executed=False),indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'frozen_banks':3,'cases':108,'paired_packets':5472,'manifest_sha256':manifest_sha,'header_sha256':sha(OUT/'banks_data.h')}))

if __name__=='__main__': main()
