"""Check actual linked-call rejection and the current VM network-ready predicate."""
from copy import deepcopy
import io

from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import sha
from reverse.nothrow_linkage import verify
from reverse.rv32_link_match import model
from reverse.elf_archive import members
from nothrow_network_qemu import network_ready


def controls(elf,app,wrapper_object,nvs_archive,qualification,old_elf,old_app):
    """Reach semantic target checks even after rebinding the altered ELF/app descriptor."""
    rejected=[]
    def reject(name,operation):
        """Only an actual verifier exception counts as rejecting a mutated input."""
        try:operation()
        except (ValueError,AssertionError):rejected.append(name)
        else:raise AssertionError('Invalid nothrow linkage accepted: '+name)
    def modified(pc,mask):
        """Change one executable word in a private byte copy, never the build file."""
        changed=bytearray(elf);e=ELFFile(io.BytesIO(elf));sections=[s for s in e.iter_sections()
            if s['sh_flags']&4 and s['sh_addr']<=pc<pc+4<=s['sh_addr']+s['sh_size']]
        assert len(sections)==1;s=sections[0];at=s['sh_offset']+pc-s['sh_addr']
        size=2 if changed[at]&3!=3 else 4
        word=int.from_bytes(changed[at:at+size],'little')^mask
        changed[at:at+size]=word.to_bytes(size,'little')
        image=bytearray(app);image[176:208]=bytes.fromhex(sha(changed))
        return bytes(changed),bytes(image)
    objects=[raw for name,raw in members(nvs_archive) if name=='nvs_page.cpp.obj'];assert len(objects)==1
    row=qualification['nvs_page_load'];spec=model(objects[0],row['name'])
    offsets=[at for at,rows in spec['relocs'].items() if any(r['name']=='_ZnajRKSt9nothrow_t' and r['type'] in (18,19) for r in rows)]
    assert len(offsets)==1
    call=next(t for t in row['transformations'] if t['object_offset']==offsets[0])
    changed,image=modified(int(call['pc'],0),0x200000)
    reject('nvs-bypasses-wrapper',lambda:verify(changed,image,wrapper_object,nvs_archive))
    core=next(r for r in qualification['functions'] if r['name'].startswith('_ZL'))
    changed,image=modified(int(core['start'],0),1)
    reject('wrapper-frame',lambda:verify(changed,image,wrapper_object,nvs_archive))
    caller=next(r for r in qualification['functions'] if r['name'].startswith('__wrap_'))
    call=next(t for t in caller['transformations'] if t['kind'].startswith('call'))
    changed,image=modified(int(call['pc'],0),0x200000)
    reject('wrong-local-helper',lambda:verify(changed,image,wrapper_object,nvs_archive))
    core_spec=model(wrapper_object,core['name'])
    at=next(at for at,rows in core_spec['relocs'].items() if any(r['name']=='malloc' for r in rows))
    call=next(t for t in core['transformations'] if t['object_offset']==at)
    size=len(bytes.fromhex(call['linked_bytes']))
    if size==8:pc=int(call['pc'],0)+4;mask=0x200000
    else:pc=int(call['pc'],0);mask=8 if size==2 else 0x200000
    changed,image=modified(pc,mask)
    reject('wrong-malloc-callee',lambda:verify(changed,image,wrapper_object,nvs_archive))
    reject('old-unwrapped-build',lambda:verify(old_elf,old_app,wrapper_object,nvs_archive))
    reject('wrong-app-descriptor',lambda:verify(elf,old_app,wrapper_object,nvs_archive))
    valid=dict(response_count=2,difference_seconds=0.125)
    state=dict(connected=True,time_synced=True,ap_active=False,station_address='192.168.43.15')
    assert network_ready(valid,state,1,'192.168.43.15')
    assert not network_ready(valid,state,1,'10.0.2.15')
    for name,field,value in (('disconnected','connected',False),('not-synchronized','time_synced',False),
                             ('still-ap','ap_active',True),('wrong-address','station_address','192.168.43.1')):
        changed=deepcopy(state);changed[field]=value
        assert not network_ready(valid,changed,1,'192.168.43.15');rejected.append(name)
    for name,sample in (('no-ntp',None),('stale-ntp',dict(response_count=1,difference_seconds=0)),
                        ('wrong-clock',dict(response_count=2,difference_seconds=1.01))):
        assert not network_ready(sample,state,1,'192.168.43.15');rejected.append(name)
    return dict(passed=True,rejected=rejected,network_positive=True,stale_subnet_constant_rejected=True)
