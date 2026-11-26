"""Private bounded native-GDB/MI collector. Import/construction never start GDB.

Only Collector.start(loopback_endpoint) may launch/attach. The caller owns QEMU,
role mapping, PCAP, final resource/RFC gates and fixture watchdog. No embedded
GDB Python, target calls, register/memory writes, temporary software breakpoints
or guest-owned-process termination. Scripted tests use injected MI transports.
"""
from collections import deque
from dataclasses import dataclass
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import threading
import time

SOURCE='95672e8f673ec977b6f61b78eeba6958d0d992ac'
ELF_SHA='3811af87f91fb563ead8e61ae5c188bc74f4495b07bb9e230834e4cef50f85bb'
GDB_SHA='5ce33ee35b9075251532fc8ea6f1745ce0885764689f0014ff1c3a3f42bcd71a'
GDB_VERSION='GNU gdb (esp-gdb) 17.1_20260402'
GDB_BYTES=14596096
QUAL_SHA='929eeef0ba37dfa6d95eb5cb07279bf7a63a31b05690c7a3f69d3345ca064612'
ROOT=Path(__file__).resolve().parents[2]
DEFAULT_ELF=ROOT/'.build/cws-close26/target/sdk/continuous/compiled/yoradio_cyd2usb_native.elf'
DEFAULT_GDB=Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/xtensa-esp-elf-gdb/17.1_20260402/xtensa-esp-elf-gdb/bin/xtensa-esp-elf-gdb-no-python.exe')
DEFAULT_CONFIG=DEFAULT_GDB.parent.parent/'lib/xtensa_esp32.so'
CONFIG_SHA='792439b2ca04c141571f00cbd6edc04c465e20aa473acfca9c03416fb8c1b9c8'
CONFIG_BYTES=379125
SITES={
 'errno':(0x400f1620,'92c8f5'), 'retry_clock':(0x400f1632,'88a1'),
 'select_before':(0x400f16ae,'10e120'), 'select_after':(0x400f16b7,'16da03'),
 'loop_clock':(0x400f15d9,'472b10'), 'send_after':(0x400f1600,'a61a0c'),
 'complete_clock':(0x400f16ed,'d881'), 'return':(0x400f16fa,'1df0'),
 'finish_status':(0x400f2419,'a55213'), 'finish_text':(0x400f1555,'e53e14'),
 'shutdown':(0x40105947,'404074'),
 'status_clear':(0x400f23e4,'0c09'), 'text_clear':(0x400f1523,'0c08'),
}


class Incomplete(Exception):
    def __init__(self,category): super().__init__(category);self.category=category


def need(condition,category):
    if not condition: raise Incomplete(category)


def digest(body): return hashlib.sha256(body).hexdigest()
def signed32(value): return value if value<0x80000000 else value-0x100000000


def queue_pressure(q):
    """An instantaneous blocked write/head, not permanent unsendability.

    Positive-window arithmetic matches pinned tcp_out.c:1266,1309. A later
    persist split or window/ACK change may progress; same-frame timeout and
    caller abort plus independent wire evidence remain separate requirements.
    """
    counts=('snd_wnd','snd_buf','snd_queuelen')
    need(all(type(q.get(k)) is int and 0<=q[k]<=0xffffffff for k in counts),'guest-queue-count-shape')
    need(all(isinstance(q.get(k),str) and re.fullmatch('0x[0-9a-f]+',q[k]) and int(q[k],16)<=0xffffffff
             for k in ('unsent','unacked')),'guest-queue-pointer-shape')
    retained=q['snd_queuelen']>0 and (int(q['unsent'],16)>0 or int(q['unacked'],16)>0)
    if not retained:return None
    selected={k:q[k] for k in (*counts,'unsent','unacked')}
    if q['snd_wnd']==0:return dict(pressure_basis='zero-peer-window',guest_queue=selected)
    if q['snd_buf']!=0 or int(q['unsent'],16)==0:return None
    # Extra fields are mandatory only for a positive-window candidate. They
    # come from actual scalar RAM reads, never host/traffic-size inference.
    if 'unsent_head' not in q or 'cwnd' not in q:return None
    need(type(q['cwnd']) is int and 0<=q['cwnd']<=0xffffffff and
         type(q.get('lastack')) is int and 0<=q['lastack']<=0xffffffff,'guest-positive-window-count-shape')
    if not 0<q['snd_wnd']<=q['cwnd']:return None
    head=q['unsent_head'];need(type(head) is dict,'guest-unsent-head-shape')
    for key in ('pointer','tcphdr_pointer'):
        need(isinstance(head.get(key),str) and re.fullmatch('0x[0-9a-f]+',head[key]) and
             int(head[key],16)<=0xffffffff,'guest-unsent-head-pointer-shape')
    need(head['pointer']==q['unsent'],'guest-unsent-head-owner-mismatch')
    if int(head['tcphdr_pointer'],16)==0:return None
    need(type(head.get('len')) is int and 0<=head['len']<=65535 and
         type(head.get('seqno_raw')) is int and 0<=head['seqno_raw']<=0xffffffff,'guest-unsent-header-scalar-shape')
    if head['len']==0:return None
    seq_host=int.from_bytes(head['seqno_raw'].to_bytes(4,'little'),'big')
    distance=(seq_host-q['lastack'])&0xffffffff
    end=distance+head['len']
    if distance>=0x80000000 or end>=0x80000000 or end<=q['snd_wnd']:return None
    selected.update(cwnd=q['cwnd'],lastack=q['lastack'],unsent_head=dict(head,
        seqno_host=seq_host,seqno_conversion='ntohl-u32-from-little-endian-target',
        seq_distance=distance,sequence_end=end))
    return dict(pressure_basis='positive-peer-window-unsent-head-blocked',guest_queue=selected)


@dataclass(frozen=True)
class Limits:
    max_stops:int=512
    max_single_stop_seconds:float=2.0
    max_total_pause_seconds:float=30.0
    max_raw_bytes:int=4*1024*1024
    max_line_bytes:int=65536
    max_pending_records:int=4096
    max_events:int=4096
    command_seconds:float=2.0
    attach_seconds:float=5.0
    startup_seconds:float=5.0
    def __post_init__(self):
        caps=dict(max_stops=512,max_single_stop_seconds=2.,max_total_pause_seconds=30.,max_raw_bytes=4*1024*1024,
                  max_line_bytes=65536,max_pending_records=4096,max_events=4096,command_seconds=2.,attach_seconds=5.,startup_seconds=5.)
        for name,cap in caps.items():need(0<getattr(self,name)<=cap,'observer-limit-declaration')


class _MIGrammar:
    def __init__(self,text): self.text=text;self.at=0
    def peek(self): return self.text[self.at:self.at+1]
    def take(self,char):
        need(self.peek()==char,'mi-syntax');self.at+=1
    def word(self):
        match=re.match(r'[A-Za-z0-9_.-]+',self.text[self.at:])
        need(match is not None,'mi-word');self.at+=len(match[0]);return match[0]
    def string(self):
        self.take('"');out=[]
        escapes={'n':'\n','r':'\r','t':'\t','b':'\b','f':'\f','v':'\v','a':'\a','"':'"',"'":"'",'?':'?','\\':'\\'}
        while True:
            need(self.at<len(self.text),'mi-truncated-string')
            char=self.text[self.at];self.at+=1
            if char=='"': return ''.join(out)
            if char!='\\': out.append(char);continue
            need(self.at<len(self.text),'mi-truncated-escape')
            char=self.text[self.at];self.at+=1
            if char in escapes:out.append(escapes[char])
            elif char in '01234567':
                digits=char
                while len(digits)<3 and self.peek() and self.peek() in '01234567':digits+=self.peek();self.at+=1
                out.append(chr(int(digits,8)))
            elif char=='x':
                match=re.match('[a-fA-F0-9]{1,2}',self.text[self.at:]);need(match is not None,'mi-hex-escape')
                self.at+=len(match[0]);out.append(chr(int(match[0],16)))
            else:raise Incomplete('mi-unknown-escape')
    def result(self):
        key=self.word();self.take('=');return key,self.value()
    def value(self):
        if self.peek()=='"':return self.string()
        if self.peek()=='{':
            self.at+=1;value={}
            if self.peek()!='}':
                while True:
                    key,child=self.result();need(key not in value,'mi-duplicate-result');value[key]=child
                    if self.peek()!=',':break
                    self.at+=1
            self.take('}');return value
        if self.peek()=='[':
            self.at+=1;items=[]
            if self.peek()!=']':
                while True:
                    if re.match(r'[A-Za-z0-9_.-]+=',self.text[self.at:]):
                        key,child=self.result();items.append({key:child})
                    else:items.append(self.value())
                    if self.peek()!=',':break
                    self.at+=1
            self.take(']');return items
        raise Incomplete('mi-value')


def parse_mi(line):
    """Parse one MI record, preserving token/result/async/stream distinctions."""
    line=line.rstrip('\r\n')
    if line.strip()=='(gdb)':return {'kind':'prompt'}
    match=re.match(r'(\d*)([\^*+=~@&])(.*)$',line)
    need(match is not None,'mi-unframed-output')
    token=int(match[1]) if match[1] else None;kind=match[2];parser=_MIGrammar(match[3])
    if kind in '~@&':
        text=parser.string();need(parser.at==len(parser.text),'mi-stream-trailing-data')
        return dict(kind=kind,token=token,text=text)
    klass=parser.word();payload={}
    while parser.peek():
        parser.take(',');key,value=parser.result();need(key not in payload,'mi-duplicate-result');payload[key]=value
    return dict(kind=kind,token=token,klass=klass,payload=payload)


class _ProcessIO:
    """Owned GDB child only. Bounded reader queue/lines; never owns a guest PID."""
    def __init__(self,argv,limits,*,env):
        self.limits=limits;self.lines=queue.Queue(limits.max_pending_records);self.error=None
        self.eof=threading.Event();self.reader_done=threading.Event();self.closed=False;self.cleanup_receipt=None
        self.child=subprocess.Popen(argv,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        self.reader=threading.Thread(target=self._read,daemon=True);self.reader.start()
    def _read(self):
        try:
            while True:
                line=self.child.stdout.readline(self.limits.max_line_bytes+1)
                if not line:self.eof.set();break
                need(len(line)<=self.limits.max_line_bytes,'mi-line-bound')
                try:self.lines.put(line,timeout=.01)
                except queue.Full:raise Incomplete('mi-pending-bound')
        except Exception as error:self.error=getattr(error,'category','mi-reader-error')
        finally:self.reader_done.set()
    def write(self,body):self.child.stdin.write(body);self.child.stdin.flush()
    def read(self,timeout):
        deadline=time.monotonic()+timeout
        while True:
            if self.error:raise Incomplete(self.error)
            try:return self.lines.get_nowait()
            except queue.Empty:pass
            if self.eof.is_set():raise Incomplete('gdb-pipe-EOF')
            if self.child.poll() is not None:raise Incomplete('gdb-exited-without-MI-result')
            remaining=deadline-time.monotonic()
            if remaining<=0:raise Incomplete('mi-record-deadline')
            try:return self.lines.get(timeout=min(.05,remaining))
            except queue.Empty:pass
    def close(self):
        if self.closed:return self.cleanup_receipt
        # The direct pinned binary is the only owned Popen handle. Never scan
        # process names/PIDs, close a guest, or assume terminate means reaped.
        deadline=time.monotonic()+self.limits.command_seconds
        issues=[]
        try:self.child.stdin.close()
        except Exception:issues.append('stdin-close')
        try:
            if self.child.poll() is None:
                try:self.child.wait(timeout=min(.1,max(.001,deadline-time.monotonic())))
                except subprocess.TimeoutExpired:
                    self.child.terminate()
                    try:self.child.wait(timeout=min(.5,max(.001,deadline-time.monotonic())))
                    except subprocess.TimeoutExpired:
                        self.child.kill();self.child.wait(timeout=max(.001,deadline-time.monotonic()))
        except Exception:issues.append('owned-process-wait')
        self.reader.join(timeout=max(0,deadline-time.monotonic()))
        # A direct child exit must release the only pipe writer. Do not take a
        # buffered-pipe lock while a reader is still blocked; report instead.
        reader_alive=self.reader.is_alive()
        if reader_alive:issues.append('owned-reader-not-joined')
        else:
            try:self.child.stdout.close()
            except Exception:issues.append('stdout-close')
        process_stopped=self.child.poll() is not None
        if not process_stopped:issues.append('owned-process-not-reaped')
        if not self.eof.is_set():issues.append('owned-pipe-EOF-unwitnessed')
        self.cleanup_receipt=dict(process_stopped=process_stopped,reader_joined=not reader_alive,
            stdin_closed=bool(getattr(self.child.stdin,'closed',False)),
            stdout_closed=bool(getattr(self.child.stdout,'closed',False)),pipe_EOF=self.eof.is_set(),issues=issues)
        self.closed=True
        if issues:raise Incomplete('owned-GDB-cleanup-incomplete')
        return self.cleanup_receipt


class MI:
    def __init__(self,io,limits,raw,clock=time.monotonic):
        self.io=io;self.limits=limits;self.raw=raw;self.clock=clock;self.token=0
        self.pending=deque();self.bytes=0;self.sha=hashlib.sha256()
    def _log(self,body):
        need(self.bytes+len(body)<=self.limits.max_raw_bytes,'mi-raw-log-bound')
        self.raw.write(body);self.raw.flush();self.bytes+=len(body);self.sha.update(body)
    def read(self,deadline):
        need(self.clock()<deadline,'mi-record-deadline')
        body=self.io.read(deadline-self.clock());need(len(body)<=self.limits.max_line_bytes,'mi-line-bound')
        self._log(b'< '+body)
        record=parse_mi(body.decode('utf-8',errors='strict'));record['_host_received']=self.clock();return record
    def ready(self):
        """Require the initial MI prompt before writing any command/attaching."""
        deadline=self.clock()+self.limits.startup_seconds
        seen=set()
        while True:
            try:record=self.read(deadline)
            except Incomplete as error:
                if error.category=='mi-record-deadline':raise Incomplete('GDB-startup-readiness-deadline')
                raise
            if record['kind']=='prompt':return
            if record['kind'] in ('~','&'):continue
            # Exact notifications emitted by this pinned binary's two -iex
            # startup guards in the saved no-target bootstrap probe. Other
            # parameters, values, fields, duplicates or async records fail.
            payload=record.get('payload',{})
            tag=None
            if record['kind']=='=' and record.get('token') is None:
                if record['klass']=='thread-group-added' and payload=={'id':'i1'}:tag='initial-thread-group'
                elif record['klass']=='cmd-param-changed' and payload in (
                    {'param':'auto-load gdb-scripts','value':'off'},
                    {'param':'auto-load local-gdbinit','value':'off'}):tag=payload['param']
            need(tag is not None and tag not in seen,'unexpected-pre-command-MI-record')
            seen.add(tag)
    def command(self,text,*,seconds=None,allowed=('done',)):
        self.token+=1;token=self.token;body=(str(token)+text+'\n').encode()
        self._log(b'> '+body);self.io.write(body)
        deadline=self.clock()+(seconds or self.limits.command_seconds);streams=[]
        while True:
            record=self.read(deadline)
            if record['kind']=='^':
                need(record['token']==token,'mi-result-token-mismatch')
                need(record['klass']!='error','mi-command-error')
                need(record['klass'] in allowed,'mi-unexpected-result-class')
                return record['payload'],streams
            if record['kind'] in '~@&':streams.append(record)
            elif record['kind'] not in ('prompt',):
                need(len(self.pending)<self.limits.max_pending_records,'mi-pending-bound');self.pending.append(record)
    def stopped(self,seconds=None,*,poll=False):
        deadline=self.clock()+(seconds or self.limits.command_seconds)
        while True:
            try:record=self.pending.popleft() if self.pending else self.read(deadline)
            except Incomplete as error:
                if poll and error.category=='mi-record-deadline':return None
                raise
            if record['kind']=='*' and record['klass']=='stopped':return record
            need(record['kind']!='^','mi-unsolicited-result')
            if record['kind']=='=' and record['klass'] in ('thread-group-exited','thread-exited'):
                raise Incomplete('guest-or-debugger-thread-exited')


class FrameMachine:
    """Source-bound scalar state machine. Never substitutes host time for guest time."""
    def __init__(self,fd,pcb,guest_tuple):
        need(54<=fd<=63,'selected-fd-range');self.fd=fd;self.pcb=pcb;self.tuple=guest_tuple
        self.candidate=None;self.frame=None;self.preselect=None;self.wait=None
        self.timeout=None;self.cause=None;self.sites=('errno','retry_clock');self.state='INCOMPLETE'
        self.allow_new_call=False
    def _owned(self,s,finish=False,transition=False):
        if s['fd']!=self.fd:return False
        need(s['pcb']['identity']==self.pcb and s['pcb']['tuple']==self.tuple,'fd-PCB-tuple-changed')
        if self.frame and not finish:
            need(s['deadline_us']==self.frame['deadline_us'] and s['client_deadline_us']==self.frame['deadline_us'],
                 'same-frame-deadline-changed')
            if transition:return True
            if self.allow_new_call:
                self.frame['sp']=s['sp'];self.allow_new_call=False
            else:need(s['sp']==self.frame['sp'],'same-frame-stack-changed')
        return True
    def consume(self,site,s):
        finish=site in ('finish_status','finish_text','shutdown')
        if not self._owned(s,finish,site in ('status_clear','text_clear')):return []
        if site=='errno':
            need(s['sent']<0,'nonprogress-site-return')
            if s['errno']==11 and s['write_ready']:
                q=s['pcb']
                proof=queue_pressure(q)
                if proof:
                    need(s['deadline_us']>=1000000 and s['client_deadline_us']==s['deadline_us'] and not s['closing'],
                         'stored-frame-deadline-missing')
                    need(s.get('frame_kind') in ('status','text'),'source-frame-kind-unavailable')
                    self.candidate=dict(s,pressure_proof=proof)
                elif not self.frame:self.candidate=None
            self.sites=('retry_clock','return') if self.frame or self.candidate else ('errno','retry_clock')
        elif site in ('retry_clock','loop_clock','complete_clock'):
            need(type(s.get('now_us')) is int,'actual-target-clock-missing')
            if not self.frame:
                if self.candidate is None:return []
                c=self.candidate
                need(s['sp']==c['sp'] and s['deadline_us']==c['deadline_us'] and
                     s['client_deadline_us']==c['deadline_us'],'candidate-frame-changed')
                need(c['deadline_us']-1000000<=s['now_us']<c['deadline_us'],'pressure-not-in-original-frame-budget')
                self.frame=dict(deadline_us=c['deadline_us'],start_us=c['deadline_us']-1000000,
                    sp=c['sp'],frame_id='fd'+str(self.fd)+'-d'+str(c['deadline_us']),pressure_us=s['now_us'],
                    frame_kind=c['frame_kind'])
                self.preselect=s.copy();self.sites=('select_before','return')
                return [dict(kind='guest-pressure',observed_us=s['now_us'],errno='EAGAIN',
                             clock_basis='actual-target-retry-clock',would_block_write=True,
                             guest_queue_sample_site='actual-would-block-branch',**c['pressure_proof'])]
            if s['now_us']>=self.frame['deadline_us']:
                self.cause=dict(timeout_basis='actual-target-clock-expired',observed_us=s['now_us'])
                self.sites=('return','shutdown')
            elif site=='retry_clock':self.preselect=s.copy();self.sites=('select_before','return')
            elif site=='loop_clock':self.sites=('send_after','return')
            else:self.sites=('return','errno')
        elif site=='select_before':
            need(self.frame and self.preselect,'unbound-select')
            remaining=self.frame['deadline_us']-self.preselect['now_us']
            need(remaining>0 and s['wait_us']==remaining and s['write_ready'],'prepared-original-remainder-mismatch')
            self.wait=s.copy();self.sites=('select_after','return')
        elif site=='select_after':
            need(self.wait is not None,'select-without-prepared-wait')
            if s['select_result']==0:
                ticks=(s['tick']-self.wait['tick'])&0xffffffff
                need(ticks<0x80000000 and ticks*1000+1000>=self.wait['wait_us'],'select-zero-coarse-tick-too-early')
                self.cause=dict(timeout_basis='select-zero-original-remainder',observed_us=None,
                    preselect_us=self.preselect['now_us'],remaining_us=self.wait['wait_us'],timeval_us=self.wait['wait_us'],
                    select_result=0,tick_before=self.wait['tick'],tick_after=s['tick'],tick_hz=1000,tick_delta=ticks)
                self.sites=('return','shutdown')
            elif s['select_result']>0:self.sites=('loop_clock','return')
            else:raise Incomplete('select-error-not-timeout')
        elif site=='send_after':
            if s['sent']>0:
                need(s['sent']<=s['requested']-s['written'],'oversized-target-send')
                self.sites=(('loop_clock','return') if s['sent']<s['requested']-s['written'] else ('complete_clock','return'))
            else:self.sites=('errno','return')
        elif site=='return':
            if s['result']==-3:
                need(self.frame and self.cause,'timeout-without-actual-path')
                self.timeout=dict(kind='guest-timeout',caller_result=-3,result='HTTPD_SOCK_ERR_TIMEOUT',**self.cause)
                self.sites=('finish_status','finish_text')
            elif s['result']>=0:
                self.allow_new_call=True
                self.sites=('errno',self.frame['frame_kind']+'_clear')
            else:raise Incomplete('other-transport-failure-not-timeout')
        elif site in ('status_clear','text_clear'):
            need(self.frame and site==self.frame['frame_kind']+'_clear' and s['success_path'] is True
                 and s['closing'] is False,'source-bound-success-transition-missing')
            # It completed naturally: no timeout was exercised. Retire only at
            # this proven logical-frame boundary, never on a new D alone.
            self.frame=None;self.candidate=None;self.wait=None;self.preselect=None
            self.cause=None;self.timeout=None;self.state='PRESSURED_FRAME_COMPLETED';self.sites=()
        elif site in ('finish_status','finish_text'):
            need(self.timeout is not None and s['graceful'] is False and s['closing'],'failed-frame-finish-missing')
            self.sites=('shutdown',)
        elif site=='shutdown':
            need(self.timeout is not None and s['graceful'] is False,'failed-frame-abort-missing')
            self.state='PROJECT_TIMEOUT_WITNESSED';self.sites=()
            return [self.timeout]
        return []


class Collector:
    def __init__(self,observer,run_id,inputs_sha256,log_dir,*,elf=DEFAULT_ELF,gdb=DEFAULT_GDB,
                 qualification=None,limits=Limits(),io_factory=None,clock=time.monotonic,mode='withheld'):
        need(bool(re.fullmatch('[A-Za-z0-9_-]{1,64}',run_id)),'run-id')
        need(bool(re.fullmatch('[a-f0-9]{64}',inputs_sha256)),'inputs-manifest-hash')
        need(mode in ('withheld','read-resume','drained'),'collector-mode')
        self.mode=mode
        self.observer=observer;self.run_id=run_id;self.inputs_sha256=inputs_sha256
        self.log_dir=Path(log_dir);self.elf=Path(elf);self.gdb=Path(gdb);self.config=DEFAULT_CONFIG
        self.qualification=Path(qualification) if qualification else self.elf.parents[1]/'qualification.json'
        self.limits=limits;self.io_factory=io_factory or _ProcessIO;self.clock=clock
        self.mi=self.io=self.raw=self.meta=None;self.started=False;self.running=False
        self.attached=False;self.closed=False;self.io_cleanup=None
        self.owned=[];self.roles=[];self.machine=None;self.query=0;self.events=[]
        self.stops=0;self.max_pause=0.;self.total_pause=0.;self.stop_at=None
        self.state='INCOMPLETE';self.failure=None;self.lock=threading.Lock()
        self.cancel=threading.Event();self.collect_finished=threading.Event();self.collect_finished.set()
    def _fail(self,category):
        self.state='INCOMPLETE';self.failure=self.failure or category
        self.observer.incomplete(category)
    def _verify_pins(self):
        need(digest(self.elf.read_bytes())==ELF_SHA,'ELF-pin')
        gdb_body=self.gdb.read_bytes()
        need(len(gdb_body)==GDB_BYTES and digest(gdb_body)==GDB_SHA,'GDB-pin')
        self._verify_config()
        raw=self.qualification.read_bytes();q=json.loads(raw)
        need(digest(raw)==QUAL_SHA and q['passed'] is True and q['source_commit']==SOURCE and
             q['elf']['sha256']==ELF_SHA,'qualification-source-pin')
    def _verify_config(self):
        need(self.config.resolve()==DEFAULT_CONFIG.resolve(),'GDB-config-path-pin')
        try:body=self.config.read_bytes()
        except OSError:raise Incomplete('GDB-config-unavailable')
        need(len(body)==CONFIG_BYTES and digest(body)==CONFIG_SHA,'GDB-config-pin')
    def _child_environment(self):
        # Only this explicit child environment changes; inherited values are
        # never dumped into logs. The absolute module is the official wrapper's
        # proven architecture binding, not a guessed register-layout override.
        env=os.environ.copy();env['XTENSA_GNU_CONFIG']=str(self.config.resolve())
        return env
    def _verify_runtime_config(self):
        _,streams=self._cmd('-interpreter-exec console '+json.dumps('show environment XTENSA_GNU_CONFIG'))
        prefix='XTENSA_GNU_CONFIG = '
        lines=[line for record in streams if record['kind']=='~' for line in record['text'].splitlines()]
        need(len(lines)==1 and lines[0].startswith(prefix),'GDB-runtime-config-output')
        value=lines[0][len(prefix):]
        need(value==str(self.config.resolve()),'GDB-runtime-config-pin')
    def _note(self,value):
        need(len(self.events)<self.limits.max_events,'observer-event-bound');self.events.append(value)
        if self.meta:self.meta.write(json.dumps(value,sort_keys=True)+'\n');self.meta.flush()
    def _cmd(self,command,*,cleanup=False,**kwargs):
        # Clamp the WHOLE stopped interval, not just each separate MI query.
        # Cleanup may exceed an exhausted observation budget only to release
        # the owned hbreaks/resume/disconnect; it can never create a witness.
        if self.stop_at is not None and not cleanup:
            remaining=self.limits.max_single_stop_seconds-(self.clock()-self.stop_at)
            need(remaining>0,'observer-single-stop-bound')
            kwargs['seconds']=min(kwargs.get('seconds',self.limits.command_seconds),remaining)
        try:return self.mi.command(command,**kwargs)
        except Incomplete:
            if self.stop_at is not None and not cleanup and self.clock()-self.stop_at>=self.limits.max_single_stop_seconds:
                raise Incomplete('observer-single-stop-bound')
            raise
    def _values(self,expressions):
        self.query+=1;marker='R06V'+str(self.query)
        fmt=marker+' '+' '.join('%llu' for _ in expressions)+'\n'
        line='printf '+json.dumps(fmt)+', '+', '.join('(unsigned long long)('+e+')' for e in expressions)
        _,streams=self._cmd('-interpreter-exec console '+json.dumps(line))
        values=[]
        for record in streams:
            if record['kind']=='~':
                for text in record['text'].splitlines():
                    if text.startswith(marker+' '):values.append(text[len(marker)+1:])
        need(len(values)==1,'optimized-or-unreadable-scalar-output')
        fields=values[0].split();need(len(fields)==len(expressions) and all(re.fullmatch('[0-9]+',v) for v in fields),
                                    'non-numeric-scalar-output')
        return [int(v) for v in fields]
    def _client(self,fd):
        matches=[]
        for index in range(2):
            a=self._values([f's_clients[{index}].used',f's_clients[{index}].socket',
                            f's_clients[{index}].closing',f's_clients[{index}].frame_deadline_us'])
            if a[0] and signed32(a[1]&0xffffffff)==fd:matches.append(dict(index=index,closing=bool(a[2]),deadline=a[3]))
        need(len(matches)==1,'client-owner-unavailable');return matches[0]
    def _pcb(self,fd):
        need(54<=fd<=63,'fd-array-range');base=f'sockets[{fd-54}].conn'
        need(self._values([base])[0]!=0,'netconn-unavailable')
        pointer,type_=self._values([base+'->pcb.tcp',base+'->type'])
        need(pointer and type_&0xf0==0x10,'TCP-PCB-unavailable')
        p=base+'->pcb.tcp'
        names=('local_ip.addr','remote_ip.addr','local_port','remote_port','state','snd_wnd','snd_buf','snd_queuelen',
               'snd_nxt','lastack','unsent','unacked')
        a=self._values([p+'->'+n for n in names])
        ip=lambda value:str(ipaddress.IPv4Address(value.to_bytes(4,'little')))
        return dict(identity=hex(pointer),tuple=dict(local_ip=ip(a[0]),remote_ip=ip(a[1]),local_port=a[2],remote_port=a[3]),
                    state=a[4],snd_wnd=a[5],snd_buf=a[6],snd_queuelen=a[7],snd_nxt=a[8],lastack=a[9],
                    unsent=hex(a[10]),unacked=hex(a[11]))
    def _positive_unsent_head(self,fd,p):
        """Scalar header/owner fields only. Never traverse/read queue payload."""
        need(54<=fd<=63 and re.fullmatch('0x[0-9a-f]+',p['unsent']) and int(p['unsent'],16)>0,
             'positive-head-read-owner')
        pcb=f'sockets[{fd-54}].conn->pcb.tcp';head='((struct tcp_seg*)'+p['unsent']+')'
        owner,unsent,header,length,cwnd,lastack=self._values([pcb,pcb+'->unsent',head+'->tcphdr',
            head+'->len',pcb+'->cwnd',pcb+'->lastack'])
        need(owner==int(p['identity'],16) and unsent==int(p['unsent'],16) and lastack==p['lastack'],
             'positive-head-PCB-owner-changed')
        need(0<=header<=0xffffffff and 0<=length<=65535,'positive-head-scalar-range')
        raw=self._values(['((struct tcp_hdr*)'+hex(header)+')->seqno'])[0] if header else None
        p.update(cwnd=cwnd,unsent_head=dict(pointer=hex(unsent),tcphdr_pointer=hex(header),len=length,seqno_raw=raw))
    def _pause_begin(self,record=None):
        self.stop_at=(record or {}).get('_host_received',self.clock());self.running=False
        self.stops+=1;need(self.stops<=self.limits.max_stops,'observer-stop-bound')
    def _resume(self,*,cleanup=False):
        self._cmd('-exec-continue',allowed=('running',),cleanup=True);self.running=True
        if self.stop_at is not None:
            pause=self.clock()-self.stop_at;self.stop_at=None;self.max_pause=max(self.max_pause,pause);self.total_pause+=pause
            self._note(dict(kind='debugger-pause',seconds=pause,total_seconds=self.total_pause))
            category=('observer-single-stop-bound' if pause>self.limits.max_single_stop_seconds else
                      'observer-total-pause-bound' if self.total_pause>self.limits.max_total_pause_seconds else None)
            if category:
                if cleanup:self._fail(category)
                else:raise Incomplete(category)
    def debugger_receipt(self):
        return dict(max_stops=self.limits.max_stops,max_single_stop_seconds=self.limits.max_single_stop_seconds,
                    max_total_pause_seconds=self.limits.max_total_pause_seconds,stops=self.stops,
                    max_observed_stop_seconds=self.max_pause,total_observed_pause_seconds=self.total_pause,
                    budget_exceeded=self.failure in ('observer-stop-bound','observer-single-stop-bound','observer-total-pause-bound'),
                    scope='Observed host stop-to-resume intervals; excludes some RSP latency, not guest latency')
    def start(self,endpoint):
        """EXPLICIT sole launch/attach entry; returns two initial client/PCB bindings."""
        need(not self.started,'collector-already-started');need(callable(getattr(self.observer,'incomplete',None)),'Observer-incomplete-API-required')
        match=re.fullmatch(r'(?:127\.0\.0\.1|localhost):([0-9]{1,5})',endpoint)
        need(match and 0<int(match[1])<65536,'explicit-loopback-GDB-endpoint-required')
        self._verify_pins()
        require_external=self.log_dir.resolve()
        roots=(ROOT,*[p for p in ROOT.parents if (p/'.git').exists()])
        need(not any(require_external.is_relative_to(p.resolve()) for p in roots) and
             not any((p/'.git').exists() for p in (require_external,*require_external.parents)),
             'private-MI-logs-outside-repository')
        self.log_dir.mkdir(parents=True,exist_ok=False)
        self.raw=(self.log_dir/'raw-mi.log').open('xb');self.meta=(self.log_dir/'events.jsonl').open('x',encoding='utf-8')
        argv=[str(self.gdb),'--interpreter=mi2','-nx','--quiet','-iex','set auto-load off','-iex','set debuginfod enabled off']
        try:self.io=self.io_factory(argv,self.limits,env=self._child_environment())
        except Exception as error:self._fail(getattr(error,'category','GDB-process-start-incomplete'));self.close();raise
        self.mi=MI(self.io,self.limits,self.raw,self.clock);self.started=True
        try:
            startup_at=self.clock()
            self.mi.ready()
            self._note(dict(kind='host-tool-readiness',seconds=self.clock()-startup_at,
                            budget_seconds=self.limits.startup_seconds,target_attached=False))
            _,version_streams=self._cmd('-gdb-version')
            need(any(r['kind']=='~' and GDB_VERSION in r['text'].splitlines() for r in version_streams),
                 'GDB-runtime-version-pin')
            self._verify_runtime_config()
            for setting in ('pagination off','confirm off','may-call-functions off','may-write-memory off','may-write-registers off','non-stop off','mi-async on'):
                self._cmd('-gdb-set '+setting)
            self._cmd('-file-exec-and-symbols '+json.dumps(str(self.elf)))
            self._cmd('-target-select remote '+endpoint,seconds=self.limits.attach_seconds,allowed=('connected','done'))
            self.attached=True
            record=self.mi.stopped(self.limits.attach_seconds);self._pause_begin(record)
            symbols=self._values(['(unsigned)&s_clients[0]','(unsigned)&sockets[0]','(unsigned)&xTickCount','sizeof(xTickCount)'])
            need(symbols==[0x3ffb67e8,0x3ffb6c6c,0x3ffb31cc,4],'static-owner-symbol-binding')
            for name,(address,prefix) in SITES.items():
                result,_=self._cmd('-data-read-memory-bytes '+hex(address)+' '+str(len(prefix)//2))
                need(result['memory'][0]['contents'].lower()==prefix,'live-instruction-prefix-mismatch')
            self._check_breakpoints()
            for index in range(2):
                used,fd=self._values([f's_clients[{index}].used',f's_clients[{index}].socket'])
                if used:
                    fd=signed32(fd&0xffffffff);c=self._client(fd);p=self._pcb(fd)
                    self.roles.append(dict(client_index=index,guest_fd=fd,pcb=p['identity'],guest_tuple=p['tuple'],closing=c['closing']))
            need(len(self.roles)==2 and len({r['guest_fd'] for r in self.roles})==2,'two-live-client-bindings-required')
            self._note(dict(kind='input-binding',source_commit=SOURCE,elf_sha256=ELF_SHA,gdb_sha256=GDB_SHA,
                            qualification_sha256=QUAL_SHA,inputs_sha256=self.inputs_sha256,gdb_version=GDB_VERSION,
                            config_sha256=CONFIG_SHA,config_bytes=CONFIG_BYTES,
                            module_sha256=digest(Path(__file__).read_bytes()),initial_clients=self.roles))
            self._resume();return list(self.roles)
        except Exception as error:
            self._fail(getattr(error,'category','GDB-start-incomplete'));self.close();raise
    def bind_slow(self,fd,pcb,guest_tuple):
        need(self.started and self.machine is None,'collector-binding-order')
        need(any(r['guest_fd']==fd and r['pcb']==pcb and r['guest_tuple']==guest_tuple and not r['closing'] for r in self.roles),
             'selected-role-not-in-initial-bindings')
        self.machine=FrameMachine(fd,pcb,guest_tuple)
    def _check_breakpoints(self):
        result,_=self._cmd('-break-list');body=result.get('BreakpointTable',{}).get('body',[])
        rows=[item.get('bkpt',item) for item in body]
        need(len(rows)<=2,'more-than-two-breakpoints')
        need({r['number'] for r in rows}==set(self.owned),'unowned-breakpoint')
        return rows
    def _arm(self,names):
        need(0<len(names)<=2 and len(set(names))==len(names) and all(n in SITES for n in names),'invalid-hbreak-site-set')
        self._check_breakpoints()
        if self.owned:self._cmd('-break-delete '+' '.join(self.owned));self.owned=[]
        for name in names:
            address=SITES[name][0];result,_=self._cmd('-break-insert -h *'+hex(address));bp=result['bkpt']
            self.owned.append(bp['number'])
            need(('hw' in bp['type'] or 'hardware' in bp['type']) and 'breakpoint' in bp['type'] and int(bp['addr'],16)==address,
                 'hardware-breakpoint-not-exact')
        self._check_breakpoints();self._note(dict(kind='arm',sites=list(names),hardware_slots=len(self.owned)))
    def arm(self):
        need(self.machine is not None and self.running,'bind-before-arm')
        self._cmd('-exec-interrupt --all');record=self.mi.stopped();self._pause_begin(record)
        try:self._arm(self.machine.sites);self._resume()
        except Exception as error:self._fail(getattr(error,'category','GDB-arm-incomplete'));raise
    def _snapshot(self,site):
        fdexpr='$a11' if site.startswith('finish_') else '((ws_client_t*)$a5)->socket' if site=='status_clear' else '((ws_client_t*)$a2)->socket' if site=='text_clear' else '$a3'
        pc,sp,rawfd,tick=self._values(['$pc','$a1',fdexpr,'xTickCount'])
        fd=signed32(rawfd&0xffffffff);need(pc==SITES[site][0],'unexpected-hardware-PC')
        if fd!=self.machine.fd:return dict(fd=fd,pc=pc,sp=sp,tick=tick)
        c=self._client(fd);p=self._pcb(fd)
        s=dict(fd=fd,pc=pc,sp=sp,tick=tick,pcb=p,client_deadline_us=c['deadline'],closing=c['closing'])
        if site in ('status_clear','text_clear'):
            s['deadline_us']=c['deadline']
            # status_clear is reached exclusively by the verified success edge;
            # text_clear is common to SDK success/failure, so read real ESP_OK.
            s['success_path']=(site=='status_clear' or signed32(self._values(['$a10'])[0]&0xffffffff)==0)
            return s
        if site.startswith('finish_') or site=='shutdown':
            s['graceful']=bool(self._values(['$a12' if site.startswith('finish_') else '($a4 & 255)'])[0]);return s
        low,high,requested,written=self._values(['*(unsigned int*)($a1+40)','$a4','$a5','$a2'])
        s.update(deadline_us=(low|((high&0xffffffff)<<32)),requested=requested,written=written)
        if site in ('errno','send_after'):
            sent,errno,write=self._values(['$a10','$a8','*(unsigned char*)($a1+24)'])
            # Historical field name: write_ready is the helper's selected
            # WAIT-FOR-WRITE direction, not proof of select writability.
            s.update(sent=signed32(sent&0xffffffff),errno=errno,write_ready=bool(write))
            if site=='errno' and s['errno']==11 and s['write_ready']:
                if p['snd_wnd']>0 and p['snd_buf']==0 and p['snd_queuelen']>0 and int(p['unsent'],16)>0:
                    self._positive_unsent_head(fd,p)
                if queue_pressure(p):s['frame_kind']=self._frame_kind()
        if site in ('retry_clock','loop_clock','complete_clock'):
            lo,hi=self._values(['$a10','$a11']);s['now_us']=lo|((hi&0xffffffff)<<32)
        if site in ('select_before','select_after'):
            sec,usec,write,result=self._values(['((struct timeval*)$a1)->tv_sec','((struct timeval*)$a1)->tv_usec',
                                             '*(unsigned char*)($a1+24)','$a10'])
            s.update(wait_us=sec*1000000+usec,write_ready=bool(write),select_result=signed32(result&0xffffffff))
        if site=='return':s['result']=signed32(written&0xffffffff)
        return s
    def _frame_kind(self):
        result,_=self._cmd('-stack-list-frames 0 7')
        stack=result.get('stack',[]);need(0<len(stack)<=8,'bounded-frame-metadata-unavailable')
        for entry in stack:
            function=entry.get('frame',entry).get('func','')
            if function=='send_text':return 'text'
            if function in ('send_status_frame','send_status'):return 'status'
        raise Incomplete('optimized-logical-frame-kind-unavailable')
    def _forward(self,event):
        frame=self.machine.frame
        full=dict(origin='root-gdb-send-frame',run_id=self.run_id,source_commit=SOURCE,elf_sha256=ELF_SHA,
            inputs_sha256=self.inputs_sha256,guest_fd=self.machine.fd,pcb=self.machine.pcb,
            frame_id=frame['frame_id'],start_us=frame['start_us'],deadline_us=frame['deadline_us'],
            start_basis='derived-from-stored-deadline',entry_clock_observed=False,source_constructor_budget_us=1000000,
            evidence_sha256=self.mi.sha.hexdigest(),debugger=self.debugger_receipt(),**event)
        full['evidence_prefix_bytes']=self.mi.bytes
        self._note(full);self.observer.submit(full)
    def collect(self,stop_event,*,seconds):
        """Run in caller-owned thread. Caller watchdog/stop_event always wins."""
        need(self.started and self.machine and self.running,'collector-not-armed')
        need(0<seconds<=120,'collector-activity-declaration')
        need(self.collect_finished.is_set() and not self.closed,'collector-single-owner')
        self.collect_finished.clear()
        deadline=self.clock()+seconds
        try:
            while not stop_event.is_set() and not self.cancel.is_set() and self.clock()<deadline and self.machine.state not in ('PROJECT_TIMEOUT_WITNESSED','PRESSURED_FRAME_COMPLETED'):
                record=self.mi.stopped(min(.1,max(.001,deadline-self.clock())),poll=True)
                if record is None:continue
                self._pause_begin(record);reason=record['payload'].get('reason')
                need(reason=='breakpoint-hit','unexpected-target-stop')
                pc=int(record['payload']['frame']['addr'],16)
                names=[n for n,(address,_) in SITES.items() if address==pc];need(len(names)==1,'unexpected-hardware-PC')
                site=names[0];sample=self._snapshot(site);self._note(dict(kind='sample',site=site,**sample))
                events=self.machine.consume(site,sample)
                control_done=self.mode!='withheld' and any(e['kind']=='guest-pressure' for e in events)
                if self.machine.sites and not control_done:self._arm(self.machine.sites)
                else:
                    if self.owned:self._cmd('-break-delete '+' '.join(self.owned));self.owned=[]
                self._resume()  # Receipt covers the completed stop before forwarding.
                for event in events:self._forward(event)
                if control_done:
                    self.state='CONTROL_PRESSURE_WITNESSED';return self.snapshot()
            if self.machine.state=='PROJECT_TIMEOUT_WITNESSED':self.state='PROJECT_TIMEOUT_WITNESSED'
            elif self.machine.state=='PRESSURED_FRAME_COMPLETED':self._fail('pressure-frame-completed-without-timeout')
            elif (stop_event.is_set() or self.cancel.is_set()) and self.mode!='withheld':self.state='CONTROL_COLLECTION_FINISHED'
            elif not stop_event.is_set() and not self.cancel.is_set():self._fail('collector-activity-deadline')
        except Exception as error:self._fail(getattr(error,'category','GDB-collection-incomplete'))
        finally:self.collect_finished.set()
        return self.snapshot()
    def snapshot(self):return dict(state=self.state,category=self.failure,initial_clients=list(self.roles),
                                   debugger=self.debugger_receipt(),attached=self.attached,started=self.started,
                                   closed=self.closed,mode=self.mode,events=len(self.events),io_cleanup=self.io_cleanup)
    def close(self):
        """Disarm/resume/disconnect the owned GDB; never kill or call the guest."""
        if self.closed:return self.snapshot()
        self.cancel.set()
        if not self.collect_finished.wait(self.limits.command_seconds+.25):
            self._fail('collector-worker-not-joined')
            # No concurrent MI reader/writer. Terminate only the GDB child to
            # wake its bounded reader, leaving all guest ownership with root.
            try:
                if self.io:self.io_cleanup=self.io.close()
            except Exception as error:
                self.io_cleanup=getattr(self.io,'cleanup_receipt',None)
                self._fail(getattr(error,'category','owned-GDB-cleanup-incomplete'))
            if not self.collect_finished.wait(self.limits.command_seconds+.25):return self.snapshot()
        try:
            if self.attached and self.running:
                self._cmd('-exec-interrupt --all',cleanup=True);record=self.mi.stopped();self._pause_begin(record)
            if self.attached:
                if self.owned:self._cmd('-break-delete '+' '.join(self.owned),cleanup=True);self.owned=[]
                self._resume(cleanup=True);self._cmd('-target-disconnect',cleanup=True);self.attached=False
        except Exception as error:self._fail(getattr(error,'category','GDB-cleanup-incomplete'))
        finally:
            try:
                if self.io:self.io_cleanup=self.io.close()
            except Exception as error:
                self.io_cleanup=getattr(self.io,'cleanup_receipt',None)
                self._fail(getattr(error,'category','owned-GDB-cleanup-incomplete'))
            finally:
                if self.raw:self.raw.close()
                if self.meta:self.meta.close()
                self.closed=True
        return self.snapshot()
