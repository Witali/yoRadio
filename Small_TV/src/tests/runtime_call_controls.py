"""Reject wrong runtime bodies and relocation-compatible but incorrectly bound calls."""
from copy import deepcopy

from audit_factory_xrefs import Image, startup_gp
from reverse.runtime_call_gaps import Linked, qualify
from reverse.rv32_link_match import match, model


def controls(factory, native, parts, qualified):
    """Exercise the real qualification path; do not just alter a recorded pass flag."""
    rejected=[];images={'factory':Image(factory),'native':Linked(native)}
    def reject(name, operation):
        """An altered body must actually reach and fail the verifier."""
        try:operation()
        except ValueError:rejected.append(name)
        else:raise AssertionError('Invalid runtime evidence accepted: '+name)
    changes=(('factory','_panic_handler',0,1,'frame-register'),
             ('native','_panic_handler',0,1,'native-frame-register'),
             ('factory','_panic_handler',0x40380180-0x40380102,8,'panic-target'),
             ('factory','_panic_handler',0x4038017a-0x40380102,0x100,'local-panic-branch'),
             ('factory','_ZnajRKSt9nothrow_t',8,8,'begin-catch-target'),
             ('factory','_ZnajRKSt9nothrow_t',10,8,'end-catch-target'),
             ('factory','_ZnajRKSt9nothrow_t',4,8,'array-new-identity'),
             ('native','_ZnajRKSt9nothrow_t',4,8,'native-array-new-identity'),
             ('factory','_ZL15eh_globals_dtorPv',40,8,'delete-target'),
             ('native','__wrap__Unwind_DeleteException',8,0x200000,'native-abort-target'),
             ('factory','__wrap__Unwind_DeleteException',8,0x200000,'shared-abort-target'))
    for variant,name,offset,mask,label in changes:
        row=next(r for r in qualified['variants'][variant]['functions'] if r['name']==name)
        code=bytearray(images[variant].read(int(row['start'],0),row['linked_bytes'],True))
        length=2 if code[offset]&3!=3 else 4
        word=int.from_bytes(code[offset:offset+length],'little')^mask
        code[offset:offset+length]=word.to_bytes(length,'little')
        reject(label,lambda:qualify(factory,native,parts,{(variant,name):bytes(code)}))
    altered=dict(parts);key='new_opvnt.o';data=bytearray(altered[key]);data[-1]^=1;altered[key]=bytes(data)
    reject('changed-source-object',lambda:qualify(factory,native,altered))
    spec=deepcopy(model(parts['new_opvnt.o'],'_ZnajRKSt9nothrow_t'))
    for offset,rows in spec['relocs'].items():
        spec['relocs'][offset]=[r for r in rows if r['type']!=51]
    code=images['factory'].read(0x420a3a0a,20,True)
    reject('missing-relax-permission',lambda:match(spec,code,0x420a3a0a,startup_gp(images['factory'])))
    return dict(passed=True,rejected=rejected)
