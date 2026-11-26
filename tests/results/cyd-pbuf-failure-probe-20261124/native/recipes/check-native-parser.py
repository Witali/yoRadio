from pathlib import Path
import ast,hashlib,json,runpy
base=Path(__file__).resolve().parent;p=base/'analyse-pbuf-native.py';ast.parse(p.read_bytes())
parse=runpy.run_path(str(p),run_name='proof_checks')['parse']
s=b'CYD_OPENETH_PBUF_FAILURE_SUMMARY total=3 overflow=0 used=1 saturated=0 table_bytes=128 lock_bytes=8\n'
e=b'CYD_OPENETH_PBUF_FAILURE index=0 layer=54 type=640 length=1440 derived_allocation_bytes=1512 caller_pc=0x400d0000 count=3 saturated=0\n'
cases=[]
def accept(name,body,total):
    value=parse(body);assert(None if value is None else value['total'])==total;cases.append(name)
def reject(name,body):
    try:parse(body)
    except AssertionError:cases.append(name);return
    raise AssertionError('Contradictory evidence accepted: '+name)
accept('absent-prefix-unavailable',b'',None)
accept('empty-explicit-snapshot',s.replace(b'total=3',b'total=0').replace(b'used=1',b'used=0'),0)
accept('valid-full-width-RAM',s+e,3)
accept('nonRAM-derived-size-unavailable',s+e.replace(b'type=640',b'type=386').replace(b'bytes=1512',b'bytes=0'),3)
reject('inconsistent-total',s.replace(b'total=3',b'total=4')+e)
reject('missing-bucket',s)
reject('exceeded-capacity',s.replace(b'used=1',b'used=5')+e)
reject('duplicate-tuple',s.replace(b'total=3',b'total=6').replace(b'used=1',b'used=2')+e+e.replace(b'index=0',b'index=1'))
reject('malformed-tag',s+e+b'CYD_OPENETH_PBUF_FAILURE broken\n')
reject('unflagged-entry-saturation',s+e.replace(b'saturated=0',b'saturated=1'))
reject('multiple-snapshots',s+e+s+e)
reject('overflow-before-table-full',s.replace(b'total=3',b'total=4').replace(b'overflow=0',b'overflow=1')+e)
reject('total-saturation-without-max',s.replace(b'saturated=0',b'saturated=1')+e)
reject('entry-saturation-without-max',s.replace(b'total=3',b'total=4294967295').replace(b'saturated=0',b'saturated=5')+e.replace(b'saturated=0',b'saturated=1'))
sat_s=s.replace(b'total=3',b'total=4294967295').replace(b'saturated=0',b'saturated=5')
sat_e=e.replace(b'count=3',b'count=4294967295').replace(b'saturated=0',b'saturated=1')
accept('valid-explicit-saturation',sat_s+sat_e,0xffffffff)
reject('missing-entry-saturation-bit',sat_s.replace(b'saturated=5',b'saturated=1')+sat_e)
reject('missing-total-saturation-bit',sat_s.replace(b'saturated=5',b'saturated=4')+sat_e)
rows=b''.join(e.replace(b'index=0',('index='+str(i)).encode()).replace(b'0x400d0000',('0x400d000'+str(i)).encode()).replace(b'count=3',b'count=1')for i in range(4))
accept('valid-full-table-overflow',s.replace(b'total=3',b'total=6').replace(b'overflow=0',b'overflow=2').replace(b'used=1',b'used=4')+rows,6)
out=base/'native-parser-host-02.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,cases=cases,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),scope='Pure data rejection controls; no compiler/guest/network or controller-verdict changes.'),indent=2)+'\n')
print(json.dumps(dict(passed=True,controls=len(cases))))
