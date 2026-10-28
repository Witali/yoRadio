"""Challenge full SDK function matching with mutations at real relocation sites."""
import argparse
import copy
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image,sha,startup_gp
from match_factory_sdk import CASES,classify,load_models
from reverse.elf_archive import members
from reverse.rv32_link_match import match,meaningful,validate_trace


def controls(image_bytes,libraries):
    """Reject changed fixed bits/flow and require actual linker permissions/bindings."""
    image=Image(image_bytes);gp=startup_gp(image);models,_=load_models(libraries)
    baseline=classify(image_bytes,libraries);rejected=[];data_by_name={}
    def fail(label,operation,reason=None):
        """A negative case is accepted only when the requested comparison rejects it."""
        try:operation()
        except (AssertionError,ValueError) as error:
            if reason:assert reason in str(error),(label,str(error))
            rejected.append(label)
        else:raise AssertionError('Invalid SDK match accepted: '+label)
    for name,start,_,_ in CASES:
        spec=models[name]['spec'];data=image.read(start,len(spec['code'])+64,True)
        row=next(r for r in baseline['functions'] if r['name']==name);data_by_name[name]=data
        trace=tuple((r['kind'],r['object_offset'],len(bytes.fromhex(r['object_bytes'])),
            int(r['pc'],0)-start,len(bytes.fromhex(r['linked_bytes']))) for r in row['transformations'])
        wrong=bytearray(data);wrong[0]^=128
        fail(name+'/fixed-register-or-immediate',lambda:match(spec,bytes(wrong),start,gp))
        branch=next(r for r in row['transformations'] if any(x['type'] in (16,44,45)
            for x in meaningful(spec['relocs'].get(r['object_offset'],[]))))
        wrong=bytearray(data);offset=int(branch['pc'],0)-start;length=len(bytes.fromhex(branch['linked_bytes']))
        wrong[offset]^=128 if length==4 else 4
        fail(name+'/local-branch-semantics',lambda:validate_trace(spec,bytes(wrong),start,trace,gp),'Local control flow differs')
        fail(name+'/full-body-truncation',lambda:match(spec,data[:row['linked_bytes']-1],start,gp))
        unpermitted=copy.deepcopy(spec)
        removed=next(r for r in row['transformations'] if r['kind']=='gp-high-removed')['object_offset']
        unpermitted['relocs'][removed]=[r for r in unpermitted['relocs'][removed] if r['type']!=51]
        fail(name+'/missing-relax-permission',lambda:match(unpermitted,data,start,gp))
    name='wifi_connect_process';row=next(r for r in baseline['functions'] if r['name']==name)
    spec=models[name]['spec'];start=int(row['start'],0);data=data_by_name[name];wrong=bytearray(data)
    call=next(r for r in row['transformations'] if r['kind']=='call-relaxed' and
        any(x['name']=='wifi_log' for x in meaningful(spec['relocs'].get(r['object_offset'],[]))))
    offset=int(call['pc'],0)-start;assert len(bytes.fromhex(call['linked_bytes']))==4
    word=int.from_bytes(wrong[offset:offset+4],'little')^(1<<12);wrong[offset:offset+4]=word.to_bytes(4,'little')
    trace=tuple((r['kind'],r['object_offset'],len(bytes.fromhex(r['object_bytes'])),
        int(r['pc'],0)-start,len(bytes.fromhex(r['linked_bytes']))) for r in row['transformations'])
    fail('repeated-wifi-log-target',lambda:validate_trace(spec,bytes(wrong),start,trace,gp),'Inconsistent symbol binding')
    name='ieee80211_tx_mgt_cb';row=next(r for r in baseline['functions'] if r['name']==name)
    start=int(row['start'],0);spec=models[name]['spec'];wrong=bytearray(data_by_name[name])
    access=next(r for r in row['transformations'] if r['kind']=='gp-low' and
        any(x['name']=='g_wifi_nvs' for x in meaningful(spec['relocs'].get(r['object_offset'],[]))))
    offset=int(access['pc'],0)-start
    word=int.from_bytes(wrong[offset:offset+4],'little')^(1<<20);wrong[offset:offset+4]=word.to_bytes(4,'little')
    # A locally valid relocation must still agree with another function's global symbol.
    match(spec,bytes(wrong),start,gp)
    fail('cross-function-nvs-binding',lambda:classify(image_bytes,libraries,{name:bytes(wrong)}),
        'Shared SDK symbol resolves differently')
    raw=(libraries/'libnet80211.a').read_bytes()
    fail('truncated-real-archive',lambda:list(members(raw[:-1])))
    return dict(passed=True,functions_matched=3,local_branches_checked=sum(r['local_branches_checked'] for r in baseline['functions']),
        rejected_controls=rejected,semantic_equivalence_proved=False,whole_image_completeness_proved=False)


def main():
    """Use immutable real ELF/library inputs and save only a typed test result."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--sdk-libraries',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    result=controls(args.elf.read_bytes(),args.sdk_libraries)
    result['producer_sha256']=sha(Path(__file__).read_bytes())
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))


if __name__=='__main__':main()
