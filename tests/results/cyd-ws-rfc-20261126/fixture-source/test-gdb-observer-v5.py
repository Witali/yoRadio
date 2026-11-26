"""Pure/scripted collector tests: fake MI only, no GDB, sockets or target."""
from copy import deepcopy
import importlib.util
import io
import hashlib
import ipaddress
import json
from pathlib import Path
import queue
import re
import sys
import tempfile
import threading
import unittest
from unittest import mock

PATH=Path(__file__).with_name('gdb-observer-v5.py')
SPEC=importlib.util.spec_from_file_location('private_r06_gdb_observer_v5',PATH)
g=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=g;SPEC.loader.exec_module(g)
TUPLE=dict(local_ip='10.0.2.15',remote_ip='10.0.2.2',local_port=80,remote_port=42000)
PCB='0x3ffb1234'


class Observer:
    def __init__(self):self.events=[];self.invalid=[];self.stop=threading.Event()
    def submit(self,event):self.events.append(event)
    def incomplete(self,reason):self.invalid.append(reason);self.stop.set()


class ScriptIO:
    def __init__(self,lines):self.lines=list(lines);self.writes=[];self.closed=False;self.returncode=0
    def write(self,body):self.writes.append(body)
    def read(self,timeout):
        if not self.lines:raise g.Incomplete('mi-record-deadline')
        return self.lines.pop(0)
    def close(self):self.closed=True


class AutoIO(ScriptIO):
    def __init__(self,*args):super().__init__([b'=thread-group-added,id="i1"\n',b'(gdb) \n']);self.breakpoints={};self.next_bp=0
    def write(self,body):
        super().write(body);match=re.match(rb'(\d+)(.*)\n$',body);token=match[1].decode();command=match[2].decode()
        payload='';klass='done';async_=b''
        if command=='-gdb-version':
            self.lines.append(('~'+json.dumps(g.GDB_VERSION+'\n')+'\n').encode())
        elif command.startswith('-interpreter-exec console ') and 'show environment XTENSA_GNU_CONFIG'in command:
            self.lines.append(('~'+json.dumps('XTENSA_GNU_CONFIG = '+str(g.DEFAULT_CONFIG.resolve())+'\n')+'\n').encode())
        elif command.startswith('-target-select'):
            klass='connected';async_=b'*stopped,reason="signal-received",signal-name="SIGTRAP",frame={addr="0x400f155c"}\n'
        elif command.startswith('-exec-interrupt'):
            async_=b'*stopped,reason="signal-received",signal-name="SIGINT",frame={addr="0x400f155c"}\n'
        elif command.startswith('-exec-continue'):klass='running';async_=b'*running,thread-id="all"\n'
        elif command.startswith('-data-read-memory-bytes'):
            address=int(command.split()[1],16);prefix=next(p for a,p in g.SITES.values() if a==address)
            payload=',memory=[{begin="0x0",offset="0x0",end="0x0",contents="'+prefix+'"}]'
        elif command=='-break-list':
            body_=','.join('bkpt={number="'+n+'",type="hw breakpoint",addr="'+addr+'"}'for n,addr in self.breakpoints.items())
            payload=',BreakpointTable={nr_rows="'+str(len(self.breakpoints))+'",body=['+body_+']}'
        elif command.startswith('-break-insert -h '):
            self.next_bp+=1;number=str(self.next_bp);address=command.split('*')[1];self.breakpoints[number]=address
            payload=',bkpt={number="'+number+'",type="hw breakpoint",addr="'+address+'"}'
        elif command.startswith('-break-delete '):
            for number in command.split()[1:]:self.breakpoints.pop(number,None)
        self.lines.extend([(token+'^'+klass+payload+'\n').encode(),*([async_]if async_ else [])])


def sample(**changes):
    value=dict(fd=54,sp=0x3ffb9000,tick=100,deadline_us=2000000,client_deadline_us=2000000,
        closing=False,sent=-1,errno=11,write_ready=True,requested=1024,written=128,frame_kind='status',
        pcb=dict(identity=PCB,tuple=TUPLE.copy(),snd_wnd=0,snd_buf=0,snd_queuelen=16,unsent='0x3ffb2000',unacked='0x3ffb2100'))
    value.update(changes);return value


def pressure(machine):
    assert machine.consume('errno',sample())==[]
    return machine.consume('retry_clock',sample(now_us=1500000))


def zero_timeout(machine):
    machine.consume('select_before',sample(wait_us=500000,tick=100))
    machine.consume('select_after',sample(select_result=0,tick=600))
    machine.consume('return',sample(result=-3,tick=600))
    machine.consume('finish_status',sample(graceful=False,closing=True,client_deadline_us=0))
    return machine.consume('shutdown',sample(graceful=False,closing=True,client_deadline_us=0))


class ParserTests(unittest.TestCase):
    def test_nested_lists_repeated_list_keys_and_stream_escapes(self):
        record=g.parse_mi('17^done,stack=[frame={level="0",addr="0x1"},frame={level="1",addr="0x2"}],ids=["1","2"]')
        self.assertEqual(record['token'],17);self.assertEqual(len(record['payload']['stack']),2)
        self.assertEqual(g.parse_mi('~"one\\nquote\\\" octal\\101 hex\\x42"')['text'],'one\nquote" octalA hexB')
        self.assertEqual(g.parse_mi('(gdb)')['kind'],'prompt')
    def test_async_before_result_retained(self):
        io_=ScriptIO([b'*stopped,reason="breakpoint-hit",frame={addr="0x400f1620"}\n',b'1^done\n'])
        mi=g.MI(io_,g.Limits(),io.BytesIO());mi.command('-break-list')
        self.assertEqual(mi.stopped()['payload']['reason'],'breakpoint-hit')
    def test_exit_zero_does_not_override_MI_error(self):
        mi=g.MI(ScriptIO([b'1^error,msg="scripted rejection"\n']),g.Limits(),io.BytesIO())
        with self.assertRaisesRegex(g.Incomplete,'mi-command-error'):mi.command('-break-list')
    def test_wrong_token_rejected(self):
        mi=g.MI(ScriptIO([b'88^done\n']),g.Limits(),io.BytesIO())
        with self.assertRaisesRegex(g.Incomplete,'token'):mi.command('-break-list')
    def test_malformed_truncated_and_duplicate_MI_rejected(self):
        for text in ('^done,x="unterminated','^done,x="1",x="2"','~"bad\\z"','garbage','^done,x={a="1"'):
            with self.subTest(text=text),self.assertRaises(g.Incomplete):g.parse_mi(text)
    def test_raw_bound_and_idle_poll(self):
        mi=g.MI(ScriptIO([]),g.Limits(max_raw_bytes=8),io.BytesIO())
        with self.assertRaisesRegex(g.Incomplete,'raw-log-bound'):mi.command('-break-list')
        mi=g.MI(ScriptIO([]),g.Limits(),io.BytesIO());self.assertIsNone(mi.stopped(.01,poll=True))
    def test_unsolicited_result_while_waiting_is_rejected(self):
        mi=g.MI(ScriptIO([b'99^done\n']),g.Limits(),io.BytesIO())
        with self.assertRaisesRegex(g.Incomplete,'unsolicited'):mi.stopped()


class FrameTests(unittest.TestCase):
    def machine(self):return g.FrameMachine(54,PCB,TUPLE.copy())
    def test_real_select_zero_witness_has_no_invented_postwait_time(self):
        m=self.machine();p,=pressure(m);self.assertEqual(p['observed_us'],1500000)
        event,=zero_timeout(m)
        self.assertIsNone(event['observed_us']);self.assertEqual(event['timeval_us'],500000)
        self.assertEqual(event['tick_delta'],500);self.assertEqual(event['caller_result'],-3)
        self.assertEqual(m.frame['start_us'],1000000)
    def test_actual_target_clock_path_distinct(self):
        m=self.machine();pressure(m)
        m.consume('select_before',sample(wait_us=500000))
        m.consume('select_after',sample(select_result=1,tick=101))
        m.consume('loop_clock',sample(now_us=2000001))
        m.consume('return',sample(result=-3))
        m.consume('finish_text',sample(graceful=False,closing=True,client_deadline_us=0))
        event,=m.consume('shutdown',sample(graceful=False,closing=True,client_deadline_us=0))
        self.assertEqual(event['timeout_basis'],'actual-target-clock-expired');self.assertEqual(event['observed_us'],2000001)
    def test_wrong_fd_cannot_create_pressure(self):
        m=self.machine();self.assertEqual(m.consume('errno',sample(fd=55)),[])
        self.assertIsNone(m.frame);self.assertEqual(m.state,'INCOMPLETE')
        with self.assertRaises(g.Incomplete):g.FrameMachine(53,PCB,TUPLE)
    def test_wrong_PCB_or_tuple_rejected(self):
        for key,value in (('identity','0x3ffb4321'),('tuple',dict(TUPLE,remote_port=42001))):
            s=sample();s['pcb'][key]=value
            with self.subTest(key=key),self.assertRaises(g.Incomplete):self.machine().consume('errno',s)
    def test_changed_deadline_rejected(self):
        m=self.machine();pressure(m)
        with self.assertRaisesRegex(g.Incomplete,'deadline-changed'):
            m.consume('select_before',sample(deadline_us=2000001,client_deadline_us=2000001,wait_us=500001))
    def test_no_queue_or_read_want_is_not_pressure(self):
        for kind in ('empty','WANT_READ'):
            m=self.machine();s=sample()
            if kind=='empty':s['pcb'].update(snd_wnd=65535,snd_buf=5760,snd_queuelen=0,unsent='0x0',unacked='0x0')
            else:s['write_ready']=False
            m.consume('errno',s);self.assertEqual(m.consume('retry_clock',sample(now_us=1500000)),[])
            self.assertIsNone(m.frame)
    def test_host_elapsed_cannot_replace_actual_clock(self):
        m=self.machine();m.consume('errno',sample())
        with self.assertRaisesRegex(g.Incomplete,'actual-target-clock-missing'):
            m.consume('retry_clock',sample(host_elapsed_us=9999999))
    def test_renewed_timeval_early_tick_and_wrong_return_rejected(self):
        m=self.machine();pressure(m)
        with self.assertRaisesRegex(g.Incomplete,'remainder'):m.consume('select_before',sample(wait_us=1000000))
        m=self.machine();pressure(m);m.consume('select_before',sample(wait_us=500000))
        with self.assertRaisesRegex(g.Incomplete,'tick-too-early'):m.consume('select_after',sample(select_result=0,tick=101))
        m=self.machine();pressure(m)
        with self.assertRaisesRegex(g.Incomplete,'other-transport'):m.consume('return',sample(result=-1))
    def test_partial_chunks_keep_D_while_stack_can_change_after_return(self):
        m=self.machine();pressure(m)
        m.consume('return',sample(result=1024));self.assertTrue(m.allow_new_call)
        m.consume('errno',sample(sp=0x3ffb8800));self.assertEqual(m.frame['deadline_us'],2000000)
        m.consume('retry_clock',sample(sp=0x3ffb8800,now_us=1501000))
        self.assertEqual(m.frame['sp'],0x3ffb8800)
    def test_tick_wrap(self):
        m=self.machine();pressure(m);m.consume('select_before',sample(wait_us=500000,tick=0xffffff00))
        m.consume('select_after',sample(select_result=0,tick=(0xffffff00+500)&0xffffffff))
        self.assertEqual(m.cause['tick_delta'],500)
    def test_transient_TX_full_does_not_bind_old_frame(self):
        m=self.machine();s=sample();s['pcb']['snd_wnd']=32768
        m.consume('errno',s);self.assertEqual(m.consume('retry_clock',sample(now_us=1500000)),[])
        self.assertIsNone(m.frame)
        m.consume('errno',sample(deadline_us=3000000,client_deadline_us=3000000))
        event,=m.consume('retry_clock',sample(deadline_us=3000000,client_deadline_us=3000000,now_us=2500000))
        self.assertEqual(event['kind'],'guest-pressure');self.assertEqual(m.frame['deadline_us'],3000000)
    def test_zero_pointer_strings_do_not_prove_retained_queue(self):
        m=self.machine();s=sample();s['pcb'].update(unsent='0x0',unacked='0x0')
        m.consume('errno',s);self.assertEqual(m.consume('retry_clock',sample(now_us=1500000)),[])
        self.assertIsNone(m.frame)
    def test_clock_before_derived_start_cannot_prove_pressure(self):
        m=self.machine();m.consume('errno',sample())
        with self.assertRaisesRegex(g.Incomplete,'original-frame-budget'):
            m.consume('retry_clock',sample(now_us=999999))
    def test_success_transition_retires_frame_only_on_verified_edge(self):
        m=self.machine();pressure(m);m.consume('return',sample(result=1024))
        self.assertIn('status_clear',m.sites)
        m.consume('status_clear',sample(sp=0x3ffba000,success_path=True))
        self.assertIsNone(m.frame);self.assertEqual(m.state,'PRESSURED_FRAME_COMPLETED')
        m=self.machine();s=sample(frame_kind='text');m.consume('errno',s)
        m.consume('retry_clock',sample(now_us=1500000));m.consume('return',sample(result=1024))
        with self.assertRaisesRegex(g.Incomplete,'success-transition'):
            m.consume('text_clear',sample(success_path=False))


class CollectorTests(unittest.TestCase):
    def make(self,path,**kwargs):return g.Collector(Observer(),'test-run','0'*64,path,**kwargs)
    def test_constructor_and_invalid_start_never_launch(self):
        with mock.patch.object(g.subprocess,'Popen',side_effect=AssertionError('No process allowed')):
            c=self.make(Path('unused'))
            self.assertFalse(c.started)
            with self.assertRaises(g.Incomplete):c.start('192.0.2.1:1234')
    def test_pin_failure_precedes_IO_factory(self):
        factory=mock.Mock(side_effect=AssertionError('Factory must not run'))
        with tempfile.TemporaryDirectory()as td:
            elf=Path(td)/'bad.elf';elf.write_bytes(b'not the pinned ELF')
            c=self.make(Path(td)/'logs',elf=elf,io_factory=factory)
            with self.assertRaisesRegex(g.Incomplete,'ELF-pin'):c.start('127.0.0.1:1234')
            factory.assert_not_called()
    def test_fake_start_returns_two_bindings_and_preserves_guest_ownership(self):
        io_=AutoIO()
        with tempfile.TemporaryDirectory()as td,mock.patch.object(g.subprocess,'Popen',side_effect=AssertionError('No process allowed')):
            c=self.make(Path(td)/'logs',io_factory=lambda argv,limits,**kwargs:io_)
            def values(expr):
                if len(expr)==4:return [0x3ffb67e8,0x3ffb6c6c,0x3ffb31cc,4]
                return [1,54 if '[0]'in expr[0] else 55]
            with mock.patch.object(c,'_verify_pins'),mock.patch.object(c,'_values',side_effect=values),\
                 mock.patch.object(c,'_client',return_value=dict(closing=False,deadline=0)),\
                 mock.patch.object(c,'_pcb',side_effect=lambda fd:dict(identity=PCB if fd==54 else '0x3ffb5678',tuple=dict(TUPLE,remote_port=42000+fd-54))):
                roles=c.start('127.0.0.1:1234');self.assertEqual(len(roles),2);self.assertTrue(c.running)
                with self.assertRaisesRegex(g.Incomplete,'selected-role'):c.bind_slow(54,'0x1234',TUPLE)
                c.bind_slow(54,PCB,TUPLE);c.arm();self.assertEqual(len(c.owned),2)
                c.close();self.assertTrue(io_.closed)
            commands=b''.join(io_.writes)
            for forbidden in (b'-exec-run',b'-data-write',b'-exec-jump',b'-gdb-exit',b' kill'):
                self.assertNotIn(forbidden,commands)
            self.assertIn(b'-target-disconnect',commands);self.assertIn(b'-break-insert -h',commands)
    def test_more_than_two_breakpoints_rejected(self):
        c=self.make(Path('unused'));c.owned=['1','2','3']
        c._cmd=lambda *a,**k:({'BreakpointTable':{'body':[{'bkpt':{'number':str(i)}}for i in (1,2,3)]}},[])
        with self.assertRaisesRegex(g.Incomplete,'more-than-two'):c._check_breakpoints()
    def test_pause_budget_invalidates_old_witness(self):
        now=[0.];c=self.make(Path('unused'),clock=lambda:now[0]);c._cmd=lambda *a,**k:({},[])
        c._pause_begin();now[0]=2.01
        with self.assertRaises(g.Incomplete)as error:c._resume()
        c._fail(error.exception.category)
        self.assertTrue(c.observer.invalid);self.assertTrue(c.debugger_receipt()['budget_exceeded'])
    def test_query_newline_and_unreadable_fields(self):
        c=self.make(Path('unused'));captured=[]
        def command(text):
            captured.append(text);return {},[{'kind':'~','text':'R06V1 54 123\n'}]
        c._cmd=command;self.assertEqual(c._values(['$a3','$a1']),[54,123])
        console=json.loads(captured[0].split(' ',2)[2]);self.assertIn('\\n',console)
        c._cmd=lambda *a:({},[{'kind':'~','text':'<optimized out>\n'}])
        with self.assertRaisesRegex(g.Incomplete,'unreadable'):c._values(['$a3'])
    def test_limits_cannot_silently_expand(self):
        with self.assertRaises(g.Incomplete):g.Limits(max_stops=513)
    def test_MI_console_error_is_not_a_numeric_snapshot(self):
        c=self.make(Path('unused'))
        c._cmd=lambda *a:({},[{'kind':'&','text':'scripted scalar error\n'}])
        with self.assertRaises(g.Incomplete):c._values(['$a3'])
    def test_software_breakpoint_reply_rejected(self):
        c=self.make(Path('unused'));c._check_breakpoints=lambda:[]
        c._cmd=lambda *a,**k:({'bkpt':{'number':'1','type':'breakpoint','addr':'0x400f1620'}},[])
        with self.assertRaisesRegex(g.Incomplete,'hardware-breakpoint'):c._arm(('errno',))
    def test_current_peer_Observer_accepts_scripted_schema_without_network(self):
        peer_path=PATH.with_name('pressure-peer.py')
        spec=importlib.util.spec_from_file_location('r06_peer_observer_compatibility',peer_path)
        peer=importlib.util.module_from_spec(spec);sys.modules[spec.name]=peer
        with mock.patch.object(g.subprocess,'Popen',side_effect=AssertionError('No process allowed')):
            spec.loader.exec_module(peer)
            observer=peer.Observer();inputs='0'*64
            observer.arm_wire_guard('test-run',g.SOURCE,g.ELF_SHA,'1'*64,inputs_sha256=inputs)
            observer.bind(peer.Binding('test-run',g.SOURCE,g.ELF_SHA,54,PCB,inputs))
            c=g.Collector(observer,'test-run',inputs,Path('unused'))
            # Exercise the real numeric _pcb decoder before the state machine
            # and public Observer, rather than hand-crafting a pointer shape.
            ip=lambda text:int.from_bytes(ipaddress.IPv4Address(text).packed,'little')
            returns=iter([[0x3ffb1000],[int(PCB,16),16],
                          [ip(TUPLE['local_ip']),ip(TUPLE['remote_ip']),80,42000,4,0,0,16,300,100,0x3ffb2000,0x3ffb2100]])
            expressions=[]
            def values(expr):expressions.extend(expr);return next(returns)
            c._values=values;decoded=c._pcb(54)
            self.assertEqual(decoded['unsent'],'0x3ffb2000');self.assertEqual(decoded['unacked'],'0x3ffb2100')
            self.assertFalse(any('!='in e for e in expressions))
            c.machine=g.FrameMachine(54,decoded['identity'],decoded['tuple'])
            c.mi=type('ScriptedEvidence',(),{'sha':hashlib.sha256(b'fake MI evidence'),'bytes':16})()
            c.stops=3;c.max_pause=.01;c.total_pause=.02
            c.machine.consume('errno',sample(pcb=decoded))
            event,=c.machine.consume('retry_clock',sample(now_us=1500000,pcb=decoded));c._forward(event)
            self.assertTrue(observer.stop.is_set())
            event,=zero_timeout(c.machine);c._forward(event)
            result=observer.snapshot()
            self.assertFalse(result['invalid']);self.assertFalse(result['incomplete_reasons'])
            self.assertIsNone(result['timeout']['observed_us'])
            self.assertEqual(result['pressure']['guest_queue']['unsent'],'0x3ffb2000')
    def test_read_resume_control_disarms_at_first_pressure_without_timeout(self):
        c=self.make(Path('unused'),mode='read-resume');c.started=True;c.attached=True;c.running=True
        c.machine=g.FrameMachine(54,PCB,TUPLE.copy())
        records=iter([dict(payload=dict(reason='breakpoint-hit',frame=dict(addr=hex(g.SITES[n][0]))))
                      for n in ('errno','retry_clock')])
        c.mi=type('ScriptedMI',(),{'sha':hashlib.sha256(b'fake MI'),'bytes':7,
            'stopped':lambda self,*a,**k:next(records)})()
        samples=iter([sample(),sample(now_us=1500000)])
        c._snapshot=lambda *a:next(samples)
        def arm(*a):c.owned=['1','2']
        c._arm=arm;c._cmd=lambda *a,**k:({},[])
        def resume():c.running=True;c.stop_at=None
        c._resume=resume
        result=c.collect(threading.Event(),seconds=1)
        self.assertEqual(result['state'],'CONTROL_PRESSURE_WITNESSED');self.assertFalse(c.owned)
        self.assertEqual([e['kind']for e in c.observer.events],['guest-pressure'])
        self.assertFalse(c.observer.invalid)
    def test_per_stop_deadline_clamps_all_queries(self):
        now=[0.];c=self.make(Path('unused'),clock=lambda:now[0]);c._pause_begin()
        class Commands:
            def __init__(self):self.seconds=[]
            def command(self,text,**kwargs):self.seconds.append(kwargs['seconds']);now[0]+=1.25;return {},[]
        c.mi=Commands();c._cmd('-break-list');self.assertEqual(c.mi.seconds,[2.0])
        c._cmd('-break-list');self.assertEqual(c.mi.seconds,[2.0,.75])
        with self.assertRaisesRegex(g.Incomplete,'single-stop'):c._cmd('-break-list')
    def test_close_before_start_is_safe_and_idempotent(self):
        c=self.make(Path('unused'));self.assertFalse(c.close()['attached']);self.assertTrue(c.closed)
        self.assertTrue(c.close()['closed'])


class TimedIO(ScriptIO):
    def __init__(self,steps,now):super().__init__([]);self.steps=list(steps);self.now=now
    def read(self,timeout):
        if not self.steps:self.now[0]+=timeout;raise g.Incomplete('mi-record-deadline')
        delay,line=self.steps[0]
        if delay>timeout:self.now[0]+=timeout;raise g.Incomplete('mi-record-deadline')
        self.steps.pop(0);self.now[0]+=delay;return line


class MemoryPipe:
    def __init__(self):self.lines=queue.Queue();self.closed=False
    def readline(self,limit):return self.lines.get()
    def close(self):self.closed=True


class OwnedFakeProcess:
    """In-memory child handle and pipes; never invokes an OS subprocess."""
    def __init__(self,*,stdin_exit=True,terminate_exit=True,kill_exit=True):
        self.stdout=MemoryPipe();self.returncode=None;self.calls=[]
        self.stdin_exit=stdin_exit;self.terminate_exit=terminate_exit;self.kill_exit=kill_exit
        owner=self
        class Input:
            closed=False
            def write(self,body):owner.calls.append(('write',body))
            def flush(self):pass
            def close(self):
                self.closed=True;owner.calls.append(('stdin-close',))
                if owner.stdin_exit:owner.exit(0)
        self.stdin=Input()
    def exit(self,code):
        if self.returncode is None:self.returncode=code;self.stdout.lines.put(b'')
    def poll(self):return self.returncode
    def wait(self,timeout):
        self.calls.append(('wait',timeout))
        if self.returncode is None:raise g.subprocess.TimeoutExpired(['owned-fake'],timeout)
        return self.returncode
    def terminate(self):
        self.calls.append(('terminate',))
        if self.terminate_exit:self.exit(-15)
    def kill(self):
        self.calls.append(('kill',))
        if self.kill_exit:self.exit(-9)


class StartupCleanupTests(unittest.TestCase):
    def test_config_matches_official_no_target_equivalence_proof(self):
        c=g.Collector(Observer(),'config-test','0'*64,Path('unused'));c._verify_config()
        proof=json.loads(PATH.with_name('esp32-gdb-config-probe-01').joinpath('receipt.json').read_bytes())
        self.assertEqual(proof['configuration_sha256'],g.CONFIG_SHA)
        self.assertEqual(proof['configuration_bytes'],g.CONFIG_BYTES)
        self.assertEqual(len(proof['rows']),2)
        self.assertTrue(all(row['configuration_matches_expected'] and row['process_stopped'] and
                            row['exit_code']==0 for row in proof['rows']))
        self.assertEqual(len({row['register_table_sha256'] for row in proof['rows']}),1)
        self.assertEqual(len({row['stdout_sha256'] for row in proof['rows']}),1)
        self.assertTrue(all(row['stdout_bytes']==13778 for row in proof['rows']))
        actual=PATH.with_name('esp32-gdb-config-probe-01').joinpath('direct-esp32-config.stdout.txt').read_bytes()
        self.assertEqual(hashlib.sha256(actual).hexdigest(),proof['rows'][0]['stdout_sha256'])
        selected=[line for line in actual.decode().splitlines() if line.startswith('XTENSA_GNU_CONFIG = ')]
        self.assertEqual(len(selected),1)
        c._cmd=lambda *args:({},[{'kind':'~','text':selected[0]+'\n'}]);c._verify_runtime_config()
    def test_missing_changed_or_misplaced_config_is_rejected(self):
        c=g.Collector(Observer(),'config-test','0'*64,Path('unused'))
        with mock.patch.object(g.Path,'read_bytes',side_effect=FileNotFoundError),self.assertRaisesRegex(g.Incomplete,'config-unavailable'):
            c._verify_config()
        for body in (b'',b'\0'*g.CONFIG_BYTES):
            with self.subTest(size=len(body)),mock.patch.object(g.Path,'read_bytes',return_value=body),\
                 self.assertRaisesRegex(g.Incomplete,'config-pin'):c._verify_config()
        c.config=Path('wrong-config.so')
        with self.assertRaisesRegex(g.Incomplete,'config-path-pin'):c._verify_config()
    def test_child_environment_is_explicit_and_parent_unchanged(self):
        c=g.Collector(Observer(),'config-test','0'*64,Path('unused'))
        with mock.patch.dict(g.os.environ,{'XTENSA_GNU_CONFIG':'inherited-wrong-config','FIXTURE_UNRELATED':'keep'}):
            env=c._child_environment()
            self.assertEqual(env['XTENSA_GNU_CONFIG'],str(g.DEFAULT_CONFIG.resolve()))
            self.assertEqual(env['FIXTURE_UNRELATED'],'keep')
            self.assertEqual(g.os.environ['XTENSA_GNU_CONFIG'],'inherited-wrong-config')
        child=OwnedFakeProcess()
        with mock.patch.object(g.subprocess,'Popen',return_value=child)as popen:
            transport=g._ProcessIO(['pinned-direct-no-python'],g.Limits(),env=env);transport.close()
        self.assertIs(popen.call_args.kwargs['env'],env)
        self.assertNotIn('shell',popen.call_args.kwargs)
    def test_runtime_environment_requires_exact_single_expected_value(self):
        c=g.Collector(Observer(),'config-test','0'*64,Path('unused'));commands=[]
        def streams(text):
            commands.append(text)
            return {},[{'kind':'~','text':'XTENSA_GNU_CONFIG = '+str(g.DEFAULT_CONFIG.resolve())+'\n'}]
        c._cmd=streams;c._verify_runtime_config()
        self.assertEqual(json.loads(commands[0].split(' ',2)[2]),'show environment XTENSA_GNU_CONFIG')
        for value in ('XTENSA_GNU_CONFIG = wrong-config\n','Environment variable "XTENSA_GNU_CONFIG" not defined.\n',
                      'XTENSA_GNU_CONFIG = '+str(g.DEFAULT_CONFIG.resolve())+'\nUNRELATED=not-allowed\n'):
            c._cmd=lambda *args,value=value:({},[{'kind':'~','text':value}])
            with self.subTest(value=value),self.assertRaisesRegex(g.Incomplete,'runtime-config'):c._verify_runtime_config()
    def test_wrong_child_runtime_environment_cannot_attach(self):
        class WrongConfigIO(AutoIO):
            def write(self,body):
                if b'show environment XTENSA_GNU_CONFIG'in body:
                    self.writes.append(body);token=body.split(b'-')[0]
                    self.lines.extend([b'~"XTENSA_GNU_CONFIG = wrong-config\\n"\n',token+b'^done\n'])
                else:super().write(body)
        io_=WrongConfigIO()
        with tempfile.TemporaryDirectory()as td:
            c=g.Collector(Observer(),'config-test','0'*64,Path(td)/'logs',io_factory=lambda *args,**kwargs:io_)
            with mock.patch.object(c,'_verify_pins'),self.assertRaisesRegex(g.Incomplete,'runtime-config-pin'):
                c.start('127.0.0.1:1234')
            self.assertTrue(io_.closed);self.assertFalse(c.attached);self.assertEqual(c.stops,0)
            self.assertNotIn(b'-target-select',b''.join(io_.writes))
    def test_exact_saved_direct_bootstrap_trace(self):
        probe=PATH.with_name('direct-gdb-no-target-probe-01.json')
        raw=probe.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'26ff0740762969ca7628fdc010136c27d34885ad5028d1b8845e9d031d8c1b5c')
        saved=json.loads(raw)
        self.assertEqual(saved['binary_sha256'],g.GDB_SHA)
        self.assertEqual(saved['binary_bytes'],g.GDB_BYTES)
        now=[0.];previous=0.;steps=[]
        for row in saved['rows']:
            steps.append((row['elapsed']-previous,(row['line']+'\n').encode()))
            previous=row['elapsed']
        io_=TimedIO(steps,now);mi=g.MI(io_,g.Limits(),io.BytesIO(),lambda:now[0])
        mi.ready();self.assertAlmostEqual(now[0],2.75);self.assertFalse(io_.writes)
        self.assertEqual(len(io_.steps),3)
        mi.command('-gdb-set pagination off');self.assertEqual(len(io_.writes),1)
    def test_unexpected_initialization_notifications_fail_closed(self):
        cases=[
            '=cmd-param-changed,param="auto-load gdb-scripts",value="on"',
            '=cmd-param-changed,param="auto-load python-scripts",value="off"',
            '=cmd-param-changed,param="auto-load local-gdbinit",value="off",extra="1"',
            '=thread-group-added,id="i2"',
            '=thread-created,id="1",group-id="i1"',
            '=library-loaded,id="unexpected"',
            '1=cmd-param-changed,param="auto-load gdb-scripts",value="off"',
        ]
        for line in cases:
            io_=ScriptIO([(line+'\n').encode(),b'(gdb)\n'])
            with self.subTest(line=line),self.assertRaisesRegex(g.Incomplete,'pre-command'):
                g.MI(io_,g.Limits(),io.BytesIO()).ready()
            self.assertFalse(io_.writes)
    def test_duplicate_expected_initialization_notification_rejected(self):
        line=b'=cmd-param-changed,param="auto-load gdb-scripts",value="off"\n'
        io_=ScriptIO([line,line,b'(gdb)\n'])
        with self.assertRaisesRegex(g.Incomplete,'pre-command'):g.MI(io_,g.Limits(),io.BytesIO()).ready()
        self.assertFalse(io_.writes)
    def test_collector_startup_failure_closes_without_command_or_attach(self):
        io_=ScriptIO([])
        with tempfile.TemporaryDirectory()as td:
            c=g.Collector(Observer(),'startup-test','0'*64,Path(td)/'logs',io_factory=lambda *args,**kwargs:io_)
            with mock.patch.object(c,'_verify_pins'),self.assertRaisesRegex(g.Incomplete,'startup-readiness-deadline'):
                c.start('127.0.0.1:1234')
            self.assertTrue(io_.closed);self.assertTrue(c.closed);self.assertFalse(c.attached)
            self.assertFalse(io_.writes);self.assertEqual(c.stops,0)
            self.assertTrue(c.raw.closed);self.assertTrue(c.meta.closed)
            self.assertIn('GDB-startup-readiness-deadline',c.observer.invalid)
    def test_wrong_runtime_version_cannot_attach(self):
        class WrongVersionIO(AutoIO):
            def write(self,body):
                if b'-gdb-version'in body:
                    self.writes.append(body);token=body.split(b'-')[0]
                    self.lines.extend([b'~"GNU gdb wrong-version\\n"\n',token+b'^done\n'])
                else:super().write(body)
        io_=WrongVersionIO()
        with tempfile.TemporaryDirectory()as td:
            c=g.Collector(Observer(),'version-test','0'*64,Path(td)/'logs',io_factory=lambda *args,**kwargs:io_)
            with mock.patch.object(c,'_verify_pins'),self.assertRaisesRegex(g.Incomplete,'runtime-version-pin'):
                c.start('127.0.0.1:1234')
            self.assertTrue(io_.closed);self.assertFalse(c.attached);self.assertEqual(c.stops,0)
            self.assertNotIn(b'-target-select',b''.join(io_.writes))
    def test_original_guest_pins_sites_and_limits_are_preserved(self):
        original=PATH.with_name('gdb-observer.py')
        spec=importlib.util.spec_from_file_location('immutable_original_gdb_observer',original)
        old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
        for key in ('SOURCE','ELF_SHA','QUAL_SHA','SITES','DEFAULT_ELF'):
            self.assertEqual(getattr(g,key),getattr(old,key))
        for key,value in vars(old.Limits()).items():self.assertEqual(getattr(g.Limits(),key),value)
        self.assertEqual(g.GDB_BYTES,14596096);self.assertEqual(g.DEFAULT_GDB.name,'xtensa-esp-elf-gdb-no-python.exe')
    def test_delayed_prompt_is_read_before_any_command(self):
        now=[0.];io_=TimedIO([(2.937,b'=thread-group-added,id="i1"\n'),(.01,b'(gdb) \n'),(.1,b'1^done\n')],now)
        mi=g.MI(io_,g.Limits(),io.BytesIO(),lambda:now[0]);mi.ready()
        self.assertFalse(io_.writes);self.assertAlmostEqual(now[0],2.947)
        mi.command('-gdb-set pagination off');self.assertEqual(len(io_.writes),1)
        self.assertEqual(mi.limits.command_seconds,2.0)
    def test_missing_prompt_is_bounded_and_never_writes(self):
        now=[0.];io_=TimedIO([(5.1,b'(gdb)\n')],now)
        with self.assertRaisesRegex(g.Incomplete,'startup-readiness-deadline'):
            g.MI(io_,g.Limits(),io.BytesIO(),lambda:now[0]).ready()
        self.assertEqual(now[0],5.);self.assertFalse(io_.writes)
    def test_early_exit_before_prompt_is_not_ready(self):
        class ExitIO(ScriptIO):
            def read(self,timeout):raise g.Incomplete('gdb-exited-without-MI-result')
        io_=ExitIO([])
        with self.assertRaisesRegex(g.Incomplete,'gdb-exited'):
            g.MI(io_,g.Limits(),io.BytesIO()).ready()
        self.assertFalse(io_.writes)
    def test_stop_or_result_before_startup_prompt_is_rejected(self):
        for line in (b'1^done\n',b'*stopped,reason="breakpoint-hit"\n'):
            with self.subTest(line=line),self.assertRaisesRegex(g.Incomplete,'pre-command'):
                g.MI(ScriptIO([line]),g.Limits(),io.BytesIO()).ready()
    def test_ordinary_command_stays_two_seconds_after_ready(self):
        now=[0.];io_=TimedIO([(2.9,b'(gdb)\n'),(2.1,b'1^done\n')],now)
        mi=g.MI(io_,g.Limits(),io.BytesIO(),lambda:now[0]);mi.ready()
        with self.assertRaisesRegex(g.Incomplete,'mi-record-deadline'):mi.command('-gdb-set pagination off')
        self.assertAlmostEqual(now[0],4.9)
    def test_pipe_EOF_and_child_exit_are_explicit(self):
        child=OwnedFakeProcess()
        with mock.patch.object(g.subprocess,'Popen',return_value=child)as popen:
            transport=g._ProcessIO(['pinned-direct-no-python'],g.Limits(),env={'XTENSA_GNU_CONFIG':str(g.DEFAULT_CONFIG.resolve())});child.exit(0)
            with self.assertRaisesRegex(g.Incomplete,'gdb-pipe-EOF|gdb-exited'):transport.read(.1)
            receipt=transport.close()
        self.assertEqual(popen.call_count,1);self.assertTrue(receipt['process_stopped'])
        self.assertTrue(receipt['reader_joined']);self.assertTrue(receipt['pipe_EOF'])
        self.assertTrue(receipt['stdin_closed']);self.assertTrue(receipt['stdout_closed'])
        self.assertFalse(receipt['issues']);self.assertEqual(receipt,transport.close())
    def test_cleanup_terminates_only_owned_handle_and_joins_reader(self):
        child=OwnedFakeProcess(stdin_exit=False)
        with mock.patch.object(g.subprocess,'Popen',return_value=child):
            transport=g._ProcessIO(['pinned-direct-no-python'],g.Limits(),env={'XTENSA_GNU_CONFIG':str(g.DEFAULT_CONFIG.resolve())});receipt=transport.close()
        self.assertIn(('terminate',),child.calls);self.assertNotIn(('kill',),child.calls)
        self.assertTrue(receipt['reader_joined']);self.assertTrue(receipt['stdout_closed'])
        self.assertTrue(receipt['process_stopped']);self.assertFalse(receipt['issues'])
    def test_cleanup_kill_fallback_uses_same_owned_handle(self):
        child=OwnedFakeProcess(stdin_exit=False,terminate_exit=False)
        with mock.patch.object(g.subprocess,'Popen',return_value=child):
            transport=g._ProcessIO(['pinned-direct-no-python'],g.Limits(),env={'XTENSA_GNU_CONFIG':str(g.DEFAULT_CONFIG.resolve())});receipt=transport.close()
        self.assertIn(('terminate',),child.calls);self.assertIn(('kill',),child.calls)
        self.assertTrue(receipt['process_stopped']);self.assertTrue(receipt['reader_joined'])
    def test_failed_reader_join_is_explicit_incomplete(self):
        child=OwnedFakeProcess();child.exit(0)
        transport=object.__new__(g._ProcessIO);transport.child=child;transport.limits=g.Limits()
        transport.closed=False;transport.cleanup_receipt=None;transport.eof=threading.Event()
        transport.reader=mock.Mock();transport.reader.is_alive.return_value=True
        with self.assertRaisesRegex(g.Incomplete,'owned-GDB-cleanup'):transport.close()
        self.assertFalse(transport.cleanup_receipt['reader_joined'])
        self.assertIn('owned-reader-not-joined',transport.cleanup_receipt['issues'])
        self.assertFalse(child.stdout.closed)
    def test_startup_limit_cannot_expand_or_change_observation_limits(self):
        with self.assertRaises(g.Incomplete):g.Limits(startup_seconds=5.01)
        limit=g.Limits();self.assertEqual((limit.startup_seconds,limit.command_seconds,limit.attach_seconds),(5.,2.,5.))
        self.assertEqual((limit.max_single_stop_seconds,limit.max_total_pause_seconds,limit.max_stops),(2.,30.,512))


class PositiveWindowTests(unittest.TestCase):
    def queue(self,*,seq=1000,lastack=1000,length=1000,wnd=286,cwnd=5840):
        q=sample()['pcb'];q.update(snd_wnd=wnd,snd_buf=0,snd_queuelen=4,unacked='0x0',cwnd=cwnd,lastack=lastack)
        q['unsent_head']=dict(pointer=q['unsent'],tcphdr_pointer='0x3ffb2500',len=length,
                              seqno_raw=int.from_bytes(seq.to_bytes(4,'big'),'little'))
        return q
    def test_positive_small_window_and_complete_same_frame_timeout(self):
        q=self.queue();m=g.FrameMachine(54,PCB,TUPLE.copy())
        m.consume('errno',sample(pcb=q));event,=m.consume('retry_clock',sample(pcb=q,now_us=1500000))
        self.assertEqual(event['pressure_basis'],'positive-peer-window-unsent-head-blocked')
        h=event['guest_queue']['unsent_head'];self.assertEqual(h['seqno_host'],1000)
        self.assertEqual(h['seqno_raw'],int.from_bytes((1000).to_bytes(4,'big'),'little'))
        self.assertEqual((h['seq_distance'],h['sequence_end']),(0,1000))
        self.assertEqual(h['pointer'],event['guest_queue']['unsent'])
        timeout,=zero_timeout(m);self.assertEqual(timeout['caller_result'],-3)
        self.assertEqual(m.state,'PROJECT_TIMEOUT_WITNESSED')
    def test_positive_basis_does_not_require_empty_unacked_queue(self):
        q=self.queue();q['unacked']='0x3ffb2100'
        self.assertEqual(g.queue_pressure(q)['pressure_basis'],'positive-peer-window-unsent-head-blocked')
    def test_actual_snapshot_scalar_path_attaches_positive_proof(self):
        c=g.Collector(Observer(),'snapshot-test','0'*64,Path('unused'));c.machine=g.FrameMachine(54,PCB,TUPLE.copy())
        q=self.queue();raw=q['unsent_head']['seqno_raw'];q.pop('unsent_head')
        answers=iter([[g.SITES['errno'][0],0x3ffb9000,54,100],[2000000,0,1024,128],[0xffffffff,11,1],
            [int(PCB,16),int(q['unsent'],16),0x3ffb2500,1000,5840,1000],[raw]])
        c._values=lambda *args:next(answers)
        c._client=lambda *args:dict(closing=False,deadline=2000000)
        c._pcb=lambda *args:q;c._frame_kind=lambda:'status'
        s=c._snapshot('errno');self.assertEqual(s['pcb']['unsent_head']['seqno_raw'],raw)
        self.assertTrue(s['write_ready']);self.assertEqual(s['errno'],11)
        c.machine.consume('errno',s)
        event,=c.machine.consume('retry_clock',sample(pcb=q,now_us=1500000))
        self.assertEqual(event['pressure_basis'],'positive-peer-window-unsent-head-blocked')
    def test_equal_or_larger_peer_window_fits_and_is_not_pressure(self):
        for wnd in (1000,1001,5840):
            with self.subTest(wnd=wnd):self.assertIsNone(g.queue_pressure(self.queue(wnd=wnd)))
    def test_congestion_only_or_available_buffer_is_not_pressure(self):
        for cwnd in (0,100,285):
            with self.subTest(cwnd=cwnd):self.assertIsNone(g.queue_pressure(self.queue(cwnd=cwnd)))
        q=self.queue();q['snd_buf']=1;self.assertIsNone(g.queue_pressure(q))
    def test_no_head_header_or_positive_length_is_not_pressure(self):
        q=self.queue();q['unsent']='0x0';q['unacked']='0x3ffb2100';self.assertIsNone(g.queue_pressure(q))
        q=self.queue();q.pop('unsent_head');self.assertIsNone(g.queue_pressure(q))
        q=self.queue();q['unsent_head']['tcphdr_pointer']='0x0';self.assertIsNone(g.queue_pressure(q))
        self.assertIsNone(g.queue_pressure(self.queue(length=0)))
    def test_stale_sequence_and_half_space_are_not_pressure(self):
        self.assertIsNone(g.queue_pressure(self.queue(seq=999,lastack=1000)))
        self.assertIsNone(g.queue_pressure(self.queue(seq=0x80000000,lastack=0)))
        self.assertIsNone(g.queue_pressure(self.queue(seq=0x7fffffff,lastack=0,length=1)))
    def test_valid_sequence_wrap_is_derived_without_host_endian_guess(self):
        proof=g.queue_pressure(self.queue(seq=0x10,lastack=0xfffffff0,length=500))
        h=proof['guest_queue']['unsent_head'];self.assertEqual(h['seq_distance'],32)
        self.assertEqual(h['sequence_end'],532);self.assertEqual(h['seqno_host'],16)
        self.assertEqual(h['seqno_conversion'],'ntohl-u32-from-little-endian-target')
        self.assertIsNone(g.queue_pressure(self.queue(seq=0xfffffff0,lastack=0x10)))
    def test_malformed_owner_header_and_scalar_proofs_fail_closed(self):
        edits=(('pointer','0x1234'),('tcphdr_pointer',True),('len',True),('len',65536),
               ('seqno_raw',-1),('seqno_raw',0x100000000),('seqno_raw',True))
        for key,value in edits:
            q=self.queue();q['unsent_head'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(g.Incomplete):g.queue_pressure(q)
        q=self.queue();q['cwnd']=True
        with self.assertRaises(g.Incomplete):g.queue_pressure(q)
    def test_zero_window_preserves_no_head_dereference_basis(self):
        q=sample()['pcb'];proof=g.queue_pressure(q)
        self.assertEqual(proof['pressure_basis'],'zero-peer-window')
        self.assertNotIn('unsent_head',proof['guest_queue'])
    def test_real_scalar_head_decoder_feeds_pressure_machine(self):
        c=g.Collector(Observer(),'head-test','0'*64,Path('unused'));q=self.queue();q.pop('unsent_head');q['identity']=PCB
        raw=int.from_bytes((1000).to_bytes(4,'big'),'little')
        answers=iter([[int(PCB,16),int(q['unsent'],16),0x3ffb2500,1000,5840,1000],[raw]])
        expressions=[]
        def values(expr):expressions.extend(expr);return next(answers)
        c._values=values;c._positive_unsent_head(54,q)
        self.assertEqual(q['unsent_head']['seqno_raw'],raw)
        self.assertEqual(len(expressions),7)
        for forbidden in ('payload','->p->','tls','->next'):self.assertFalse(any(forbidden in e for e in expressions))
        m=g.FrameMachine(54,PCB,TUPLE.copy());m.consume('errno',sample(pcb=q))
        event,=m.consume('retry_clock',sample(pcb=q,now_us=1500000))
        self.assertEqual(event['guest_queue']['unsent_head']['sequence_end'],1000)
    def test_changed_decoder_owner_rejected_before_header_read(self):
        c=g.Collector(Observer(),'head-test','0'*64,Path('unused'));q=self.queue();q['identity']=PCB
        c._values=mock.Mock(return_value=[int(PCB,16)+4,int(q['unsent'],16),0x3ffb2500,1000,5840,1000])
        with self.assertRaisesRegex(g.Incomplete,'owner-changed'):c._positive_unsent_head(54,q)
        self.assertEqual(c._values.call_count,1)
    def test_null_header_decoder_never_dereferences_it(self):
        c=g.Collector(Observer(),'head-test','0'*64,Path('unused'));q=self.queue();q['identity']=PCB
        c._values=mock.Mock(return_value=[int(PCB,16),int(q['unsent'],16),0,1000,5840,1000])
        c._positive_unsent_head(54,q);self.assertEqual(c._values.call_count,1)
        self.assertIsNone(g.queue_pressure(q))
    def test_positive_basis_matches_pinned_lwip_unsigned_comparison(self):
        path=Path('C:/Work/yoRadio/.idf/v6.0.2/components/lwip/lwip/src/core/tcp_out.c')
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),'f31f0eef0c9aba4402ebff73b6d99a560b1d7ec219b4e0e5791996c41a832308')
        for seq,lastack,length,wnd,cwnd in ((1000,1000,1000,286,5840),(0x10,0xfffffff0,500,286,5840),
                                          (1200,1000,86,286,5840),(1200,1000,87,286,5840)):
            q=self.queue(seq=seq,lastack=lastack,length=length,wnd=wnd,cwnd=cwnd)
            source_end=(((seq-lastack)&0xffffffff)+length)&0xffffffff
            self.assertEqual(g.queue_pressure(q)is not None,source_end>min(wnd,cwnd))


if __name__=='__main__':unittest.main(verbosity=2)
