"""Compile the owned portable floor1 core with ASan/UBSan; no codec or SDK.

The oracle computes each bin from a closed-form signed floor(abs(dy)*dx/adx),
then uses Python wide-product bit extraction. Boundary-only curves with n+/-1
endpoints test the renderer contract, not representable complete setup headers.
Every attempt retains sources, commands, logs, vectors and outputs in .build.
"""
import argparse
from bisect import bisect_right
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT/'idf/esp32-cyd2usb-native/main/vorbis_repair/floor1_render.h'
X = (-(1 << 31), -(1 << 31)+1, -65537, -1, 0, 1, 65537, (1 << 31)-2, (1 << 31)-1)
EXTRA_Y = (-(1 << 31), -1, 0, 1, (1 << 31)-1)
TABLE_SHA = 'b2eea42516d6a19aca6166cde9fe302d8c3bcc9eb31095ef88ae877a02389114'

C_DRIVER = r'''
#include <floor1_render.h>
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
static uint32_t read32(FILE *f) {
    unsigned char b[4]; assert(fread(b,1,4,f)==4);
    return (uint32_t)b[0] | (uint32_t)b[1]<<8 | (uint32_t)b[2]<<16 | (uint32_t)b[3]<<24;
}
static int32_t signed32(uint32_t u) { int32_t s; memcpy(&s,&u,4); return s; }
static void write32(FILE *f, int32_t value) {
    uint32_t u; memcpy(&u,&value,4);
    unsigned char b[4]={(unsigned char)u,(unsigned char)(u>>8),(unsigned char)(u>>16),(unsigned char)(u>>24)};
    assert(fwrite(b,1,4,f)==4);
}
int main(int argc,char **argv) {
    assert(argc==3); FILE *in=fopen(argv[1],"rb"), *out=fopen(argv[2],"wb"); assert(in && out);
    assert(read32(in)==UINT32_C(0x31523146)); uint32_t count=read32(in); write32(out,(int32_t)count);
    const int32_t x[]={INT32_MIN,INT32_MIN+1,-65537,-1,0,1,65537,INT32_MAX-1,INT32_MAX};
    const int32_t extras[]={INT32_MIN,-1,0,1,INT32_MAX};
    for(unsigned i=0;i<sizeof(x)/sizeof(*x);i++) {
        for(unsigned j=0;j<256;j++) write32(out,repair_floor1_multiply(x[i],repair_floor1_from_db[j]));
        for(unsigned j=0;j<sizeof(extras)/sizeof(*extras);j++) write32(out,repair_floor1_multiply(x[i],extras[j]));
    }
    for(uint32_t c=0;c<count;c++) {
        int n=(int)read32(in), posts=(int)read32(in), mult=(int)read32(in), present=(int)read32(in);
        assert(n>0 && n<=4096 && posts>=2 && posts<=65 && mult>=1 && mult<=4 && (present==0 || present==1));
        struct {uint32_t pre; uint16_t a[65]; uint32_t post;} xs;
        struct {uint32_t pre; char a[65]; uint32_t post;} forward;
        struct {uint32_t pre; int32_t a[65]; uint32_t post;} fit;
        memset(&xs,0,sizeof(xs)); memset(&forward,0,sizeof(forward)); memset(&fit,0,sizeof(fit));
        xs.pre=forward.pre=fit.pre=UINT32_C(0x13579bdf); xs.post=forward.post=fit.post=UINT32_C(0x2468ace0);
        for(int i=0;i<posts;i++){uint32_t v=read32(in);assert(v<=32768);xs.a[i]=(uint16_t)v;}
        for(int i=0;i<posts;i++){uint32_t v=read32(in);assert(v<(uint32_t)posts);forward.a[i]=(char)v;}
        for(int i=0;i<posts;i++) fit.a[i]=signed32(read32(in));
        unsigned char xs_copy[sizeof(xs)],forward_copy[sizeof(forward)],fit_copy[sizeof(fit)];
        memcpy(xs_copy,&xs,sizeof(xs));memcpy(forward_copy,&forward,sizeof(forward));memcpy(fit_copy,&fit,sizeof(fit));
        int32_t *pcm=malloc(((size_t)n+2)*sizeof(*pcm));assert(pcm);
        pcm[0]=INT32_C(0x13579bdf);pcm[n+1]=-INT32_C(0x2468ace0);
        for(int i=0;i<n;i++)pcm[i+1]=signed32(read32(in));
        int status=repair_floor1_render(n,posts,mult,xs.a,forward.a,present?fit.a:NULL,pcm+1);
        assert(status==present && pcm[0]==INT32_C(0x13579bdf) && pcm[n+1]==-INT32_C(0x2468ace0));
        assert(!memcmp(xs_copy,&xs,sizeof(xs)) && !memcmp(forward_copy,&forward,sizeof(forward)) && !memcmp(fit_copy,&fit,sizeof(fit)));
        write32(out,status);for(int i=0;i<n;i++)write32(out,pcm[i+1]);free(pcm);
    }
    assert(fgetc(in)==EOF);assert(!fclose(in));assert(!fclose(out));return 0;
}
'''

SUPERVISOR = r'''
"""Own one Linux session/group; publish nonce-bound terminal/cleanup facts."""
import ctypes,json,os,signal,subprocess,sys,time
from pathlib import Path
request_path=Path(sys.argv[1]).resolve();request=json.loads(request_path.read_text())
receipt=Path(request['receipt']).resolve();stop=Path(request['stop']).resolve()
assert receipt.parent==stop.parent==request_path.parent
nonce=request['nonce'];assert len(nonce)==32 and all(c in '0123456789abcdef' for c in nonce)
timeout=request['timeout'];assert 0<timeout<=60
state=dict(nonce=nonce,request_sha256=__import__('hashlib').sha256(request_path.read_bytes()).hexdigest(),
           supervisor_pid=os.getpid(),state='starting',child_reaped=False,group_gone=False)
child=None;pgid=None;signal_stop=[]
def save():
    tmp=receipt.with_suffix('.tmp');tmp.write_text(json.dumps(state));deadline=time.monotonic()+1
    while True:
        try:tmp.replace(receipt);return
        except PermissionError:
            if time.monotonic()>=deadline:raise
            time.sleep(.01)
def group_exists():
    try:os.killpg(pgid,0);return True
    except ProcessLookupError:return False
def on_signal(number,frame):signal_stop.append(number)
for sig in (signal.SIGTERM,signal.SIGHUP,signal.SIGINT):signal.signal(sig,on_signal)
try:
    # Adopt and reap only descendants of this supervisor after a group stop.
    assert ctypes.CDLL(None,use_errno=True).prctl(36,1,0,0,0)==0
    child=subprocess.Popen(request['argv'],stdin=subprocess.DEVNULL,start_new_session=True)
    pgid=child.pid;assert os.getpgid(child.pid)==pgid and os.getsid(child.pid)==pgid
    state.update(state='running',child_pid=child.pid,owned_pgid=pgid,new_session=True);save()
    deadline=time.monotonic()+timeout
    while child.poll() is None:
        if signal_stop:state.update(state='signal_stop',signals=signal_stop);break
        if stop.exists() and stop.read_text()==nonce:state['state']='stop_requested';break
        if time.monotonic()>=deadline:state['state']='timeout';break
        time.sleep(.02)
    else:state['state']='terminal'
except BaseException as exc:state.update(state='supervisor_error',error=repr(exc))
finally:
    try:
        if child is not None:
            if group_exists():
                if state['state']=='terminal':state['state']='live_descendants_nonpass'
                os.killpg(pgid,signal.SIGKILL);state['group_sigkill_sent']=True
            child.wait(timeout=5);state.update(child_reaped=True,child_returncode=child.returncode)
            deadline=time.monotonic()+5
            while True:
                try:
                    while os.waitpid(-pgid,os.WNOHANG)[0]:pass
                except ChildProcessError:pass
                if not group_exists():state['group_gone']=True;break
                if time.monotonic()>=deadline:break
                time.sleep(.02)
    except BaseException as exc:state['cleanup_error']=repr(exc)
    state['final']=True;save()
sys.exit(0 if state['child_reaped'] and state['group_gone'] and 'cleanup_error' not in state else 1)
'''

DESCENDANT_CONTROL = r'''
import json,os,subprocess,sys,time
from pathlib import Path
grandchild=subprocess.Popen(['python3','-c','import time; time.sleep(30)'])
ready=Path(sys.argv[1]);tmp=ready.with_suffix('.tmp')
tmp.write_text(json.dumps(dict(nonce=sys.argv[2],child_pid=os.getpid(),child_pgid=os.getpgrp(),
                              grandchild_pid=grandchild.pid,grandchild_pgid=os.getpgid(grandchild.pid))))
tmp.replace(ready)
time.sleep(30)
'''


def need(ok, message):
    if not ok: raise ValueError(message)


def digest(data): return hashlib.sha256(data).hexdigest()


def multiply(x, y):
    bits = (((x*y) & ((1 << 64)-1)) >> 15) & 0xffffffff
    return bits-(1 << 32) if bits >= 1 << 31 else bits


def cases():
    rows = []
    for n in (32,64,128,256,512,1024,2048,4096):
        for mult, maximum in enumerate((255,127,85,63), 1):
            for endpoint in (1,2,8,n-1,n,n+1,32768):
                for low, high in ((0,0),(maximum//2,maximum//2),(maximum,maximum),(0,maximum),(maximum,0)):
                    rows.append(dict(n=n,mult=mult,xs=[0,endpoint],fit=[low,high],present=True))
                if endpoint > 2:
                    interior = list(range(1,min(endpoint,64)))
                    interior = interior[::2][::-1]+interior[1::2]
                    for inactive in (False,True):
                        xs=[0,endpoint]+interior
                        ys=[maximum//3,maximum]+[0 if i%2 else maximum for i in range(len(interior))]
                        fit=[v | (0x8000 if inactive and i>=2 and i%3 else 0) for i,v in enumerate(ys)]
                        rows.append(dict(n=n,mult=mult,xs=xs,fit=fit,present=True))
            rows.append(dict(n=n,mult=mult,xs=[0,1],fit=[maximum,maximum],present=False))
    for index, row in enumerate(rows):
        row['forward'] = sorted(range(len(row['xs'])),key=row['xs'].__getitem__)
        row['input'] = [X[(i+index)%len(X)] for i in range(row['n'])]
    return rows


def oracle(case, table):
    if not case['present']: return [0]*case['n']
    active = sorted((x,(f&0x7fff)*case['mult']) for x,f in zip(case['xs'],case['fit']) if not f&0x8000)
    positions = [x for x,y in active]; output = []
    for x, value in enumerate(case['input']):
        lo=bisect_right(positions,x)-1; x0,y0=active[lo]
        if lo+1==len(active): y=y0
        else:
            x1,y1=active[lo+1];dy=y1-y0
            y=y0+(1 if dy>=0 else -1)*(abs(dy)*(x-x0)//(x1-x0))
        output.append(multiply(value,table[y]))
    return output


def vectors(rows):
    data=bytearray(struct.pack('<II',0x31523146,len(rows)))
    for row in rows:
        data.extend(struct.pack('<4I',row['n'],len(row['xs']),row['mult'],int(row['present'])))
        for name in ('xs','forward','fit','input'):
            data.extend(b''.join(struct.pack('<I',value&0xffffffff) for value in row[name]))
    return bytes(data)


def assess(data, rows, table):
    values=struct.unpack('<'+'i'*(len(data)//4),data);need(len(data)%4==0 and values[0]==len(rows),'complete output case count')
    at=1;math=[multiply(x,y) for x in X for y in (*table,*EXTRA_Y)]
    need(list(values[at:at+len(math)])==math,'wide multiplication oracle');at+=len(math)
    mismatch=[]
    for index,row in enumerate(rows):
        need(values[at]==int(row['present']),'renderer present/unused return');at+=1
        actual=list(values[at:at+row['n']]);want=oracle(row,table);at+=row['n']
        mismatch.extend((index,i,a,b) for i,(a,b) in enumerate(zip(actual,want)) if a!=b)
        need(len(actual)==len(want),'full curve output')
    need(at==len(values),'no output suffix')
    return mismatch,len(math)


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--cc',default='gcc')
    a=p.parse_args();out=a.output.resolve();build=(ROOT/'.build').resolve()
    need(build.parent==ROOT and out!=build and out.is_relative_to(build) and not out.exists(),'fresh .build output required')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'control').mkdir()
    r=dict(completed=False,passed=False,scope=__doc__,sources={},commands=[],sanitizers=['address','undefined'],target_executed=False,physical_device=False)
    def save():(out/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    def run(name,argv=None,timeout=60,expected='terminal',inject_interrupt=False,descendant_control=False):
        nonce=uuid.uuid4().hex;request_path=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
        ready=out/(name+'.ready.json')
        if descendant_control:argv=['python3','-c',DESCENDANT_CONTROL,host(ready),nonce]
        request=dict(nonce=nonce,argv=list(map(str,argv)),timeout=timeout,receipt=host(receipt),stop=host(stop))
        request_path.write_text(json.dumps(request),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[host(out/'supervisor.py'),host(request_path)]
        entry=dict(name=name,argv=command,child_argv=request['argv'],nonce=nonce,request_sha256=digest(request_path.read_bytes()))
        r['commands'].append(entry);save();started=time.monotonic();child=None;caught=None;actual={}
        def descendant_ready(identity):
            witness=json.loads(ready.read_text())
            need(witness['nonce']==nonce and witness['child_pid']==identity['child_pid']==identity['owned_pgid']
                 and witness['child_pgid']==witness['grandchild_pgid']==identity['owned_pgid']
                 and type(witness['grandchild_pid']) is int and witness['grandchild_pid']>0
                 and witness['grandchild_pid']!=witness['child_pid'],'owned descendant PID/PGID ready witness')
            entry['descendant_ready']=witness
        try:
            with (out/(name+'.stdout.log')).open('xb') as so,(out/(name+'.stderr.log')).open('xb') as se:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                if inject_interrupt:
                    deadline=time.monotonic()+10
                    while time.monotonic()<deadline:
                        if receipt.exists() and ready.exists():
                            identity=json.loads(receipt.read_text())
                            if identity.get('state')=='running':descendant_ready(identity);break
                        need(child.poll() is None,'supervisor exited before interruption control');time.sleep(.02)
                    else:raise ValueError('supervisor running identity missing')
                    raise KeyboardInterrupt('owned parent interruption control')
                child.wait(timeout=timeout+15)
        except BaseException as exc:caught=exc;entry['parent_error']=repr(exc)
        finally:
            try:
                if child is not None and (caught is not None or child.poll() is None):
                    stop.write_text(nonce,encoding='utf-8');entry['stop_nonce_requested']=True
                    deadline=time.monotonic()+12
                    while time.monotonic()<deadline:
                        if receipt.exists():
                            actual=json.loads(receipt.read_text())
                            if actual.get('final'):break
                        if child.poll() is not None and not receipt.exists():break
                        time.sleep(.02)
                    if child.poll() is None:
                        try:child.wait(timeout=3)
                        except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);entry['local_transport_forced_stop']=True
                if receipt.exists():actual=json.loads(receipt.read_text())
                entry.update(supervisor=actual,supervisor_exit=None if child is None else child.poll(),
                    state=actual.get('state','launch_nonpass'),returncode=actual.get('child_returncode'),
                    transport_reaped=child is not None and child.poll() is not None,
                    linux_cleanup_confirmed=actual.get('nonce')==nonce and actual.get('request_sha256')==entry['request_sha256']
                        and actual.get('final') is True and actual.get('child_reaped') is True and actual.get('group_gone') is True
                        and actual.get('new_session') is True and type(actual.get('child_pid')) is int
                        and actual['child_pid']>0 and actual.get('owned_pgid')==actual['child_pid'])
                if descendant_control:descendant_ready(actual)
            except BaseException as exc:entry['parent_cleanup_error']=repr(exc)
            finally:
                if child is not None and child.poll() is None:
                    child.kill();child.wait(timeout=5);entry['local_transport_forced_stop']=True
                entry.update(elapsed_seconds=time.monotonic()-started,stdout_sha256=digest((out/(name+'.stdout.log')).read_bytes()) if (out/(name+'.stdout.log')).exists() else None,
                    stderr_sha256=digest((out/(name+'.stderr.log')).read_bytes()) if (out/(name+'.stderr.log')).exists() else None);save()
        need(entry.get('linux_cleanup_confirmed') and entry['transport_reaped'] and entry['supervisor_exit']==0
             and not entry.get('local_transport_forced_stop') and 'parent_cleanup_error' not in entry
             and (not descendant_control or 'descendant_ready' in entry),'owned Linux/transport cleanup unconfirmed: '+name)
        if caught is not None:raise caught
        need(entry['state']==expected and (entry['returncode']==0 if expected=='terminal' else entry['returncode']<0),'host command failed: '+name)
        return entry
    try:
        for path,name in ((HEADER,'floor1_render.h'),(Path(__file__),'test-vorbis-floor1-render.py')):
            data=path.read_bytes();(out/'sources'/name).write_bytes(data);r['sources'][str(path.resolve())]=digest(data)
        header=(out/'sources/floor1_render.h').read_text();tablebody=header.split('repair_floor1_from_db[256] = {',1)[1].split('};',1)[0]
        table=[int(x,16) for x in re.findall(r'0x[0-9a-fA-F]+',tablebody)]
        need(len(table)==256 and digest(struct.pack('<256i',*table))==TABLE_SHA,'exact pinned public fullprecision lookup')
        (out/'driver.c').write_text(C_DRIVER,encoding='utf-8',newline='\n')
        (out/'supervisor.py').write_text(SUPERVISOR,encoding='utf-8',newline='\n')
        r['supervisor_sha256']=digest((out/'supervisor.py').read_bytes())
        r['driver_sha256']=digest((out/'driver.c').read_bytes());save()
        run('compiler-version',[a.cc,'--version']);run('compiler-machine',[a.cc,'-dumpmachine'])
        run('timeout-control',timeout=1,expected='timeout',descendant_control=True)
        try:run('interruption-control',inject_interrupt=True,descendant_control=True)
        except KeyboardInterrupt:
            need(r['commands'][-1]['state']=='stop_requested','owned interruption stop acknowledgement')
        else:raise ValueError('parent BaseException control did not execute')
        r['owned_process_controls']=dict(timeout_group_gone=True,parent_baseexception_group_gone=True)
        common=[a.cc,'-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie']
        rows=cases();(out/'inputs.bin').write_bytes(vectors(rows))
        run('compile',[*common,'-I'+host(out/'sources'),host(out/'driver.c'),'-o',host(out/'renderer')])
        run('execute',[host(out/'renderer'),host(out/'inputs.bin'),host(out/'outputs.bin')])
        mismatch,math_count=assess((out/'outputs.bin').read_bytes(),rows,table);need(not mismatch,'closed-form curve mismatch: '+repr(mismatch[:3]))
        # Restore just the public old tail on owned, small, non-overflowing inputs.
        anchor='out[j] = repair_floor1_multiply(out[j], repair_floor1_from_db[ly]);'
        need(header.count(anchor)==1,'exact old-tail semantic control anchor')
        (out/'control/floor1_render.h').write_text(header.replace(anchor,'out[j] *= ly;',1),encoding='utf-8',newline='\n')
        probe=dict(n=32,mult=1,xs=[0,1],forward=[0,1],fit=[128,128],present=True,input=[i-16 for i in range(32)])
        (out/'control-inputs.bin').write_bytes(vectors([probe]))
        run('control-compile',[*common,'-I'+host(out/'control'),host(out/'driver.c'),'-o',host(out/'old-tail')])
        run('control-execute',[host(out/'old-tail'),host(out/'control-inputs.bin'),host(out/'control-outputs.bin')])
        wrong,_=assess((out/'control-outputs.bin').read_bytes(),[probe],table)
        need(wrong and all(case==0 and index>=1 for case,index,actual,want in wrong),'named old-tail semantic failure required')
        need(all(digest(Path(path).read_bytes())==sha for path,sha in r['sources'].items()),'source changed during host checks')
        r.update(completed=True,passed=True,cases=len(rows),curve_bins=sum(x['n'] for x in rows),wide_products=math_count,
                 exact_curve_oracle=True,input_preservation=True,canaries=True,null_memo_cases=sum(not x['present'] for x in rows),
                 old_tail_control=dict(named_failure='tail_lookup_application',semantic_mismatches=len(wrong),first=wrong[0],terminal_zero=True,sanitizer_failure=False),
                 lookup_little_endian_sha256=TABLE_SHA,limitations='Owned renderer arithmetic only; no vendor ABI, decoder, SDK, full Vorbis/G6, radio or physical qualification.')
        save();print(json.dumps({k:r[k] for k in ('completed','passed','cases','curve_bins','wide_products','old_tail_control')}));return 0
    except BaseException as exc:r.update(completed=False,passed=False,error=repr(exc));save();raise


if __name__=='__main__':sys.exit(main())
