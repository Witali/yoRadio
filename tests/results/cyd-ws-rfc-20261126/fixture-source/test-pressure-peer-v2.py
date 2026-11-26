"""Pure/scripted tests only. No endpoint, listener, CA file or guest is used."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys
import threading
import time
import unittest
from unittest import mock

P=Path(__file__).with_name("pressure-peer-v2.py")
spec=importlib.util.spec_from_file_location("private_pressure_peer_v2",P)
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
HASH="a"*64
B=p.Binding("scripted-run","b"*40,HASH,7,"0x1234",HASH)
TUPLE=dict(local_ip="10.0.2.15",remote_ip="10.0.2.2",local_port=80,remote_port=42000)


def observer():
    o=p.Observer();o.arm_wire_guard(B.run_id,B.source_commit,B.elf_sha256,HASH,inputs_sha256=HASH);o.bind(B,guest_tuple=TUPLE);o.arm_stimulus();return o


def witness(kind="guest-pressure",**changes):
    e=dict(run_id=B.run_id,source_commit=B.source_commit,elf_sha256=B.elf_sha256,
           guest_fd=B.guest_fd,pcb=B.pcb,evidence_sha256=HASH,kind=kind,
           origin="root-gdb-send-frame",frame_id="frame-1",start_us=200,
           deadline_us=1000200,observed_us=300,errno="EAGAIN")
    e.update(inputs_sha256=HASH,start_basis="derived-from-stored-deadline",entry_clock_observed=False,
             source_constructor_budget_us=1000000,clock_basis="actual-target-retry-clock",would_block_write=True,
             pressure_basis="zero-peer-window",guest_queue_sample_site="actual-would-block-branch",
             guest_queue=dict(snd_wnd=0,snd_buf=0,snd_queuelen=4,unsent="0x123456",unacked="0x0"))
    e["debugger"]=dict(max_stops=512,max_single_stop_seconds=2.0,max_total_pause_seconds=30.0,
                       stops=2,max_observed_stop_seconds=.01,total_observed_pause_seconds=.02,budget_exceeded=False)
    if kind=="guest-timeout":e.update(observed_us=1000200,result="HTTPD_SOCK_ERR_TIMEOUT",timeout_basis="actual-target-clock-expired",caller_result=-3)
    e.update(changes);return e


def terminal(*,server_rst=0,peer_rst=0,fin=True,**changes):
    def side(length,rst):
        return dict(payload_bytes=length,fin_offset=length if fin else None,sequence_end=length+int(fin),
                    fin_acked=fin,max_ack=0,rsts=rst)
    server,peer=side(200,server_rst),side(80,peer_rst)
    server["max_ack"]=peer["sequence_end"];peer["max_ack"]=server["sequence_end"]
    value=dict(role="slow",guest_fd=B.guest_fd,pcb=B.pcb,guest_tuple=dict(TUPLE),
               terminal_basis="captured-rst-with-sequence-and-ack-consistency" if server_rst or peer_rst else "both-fins-and-acknowledgments",
               server=server,peer=peer,captured_ranges_contiguous=True,missing_bytes_inferred=False)
    value.update(changes);return value


def wire(o,**changes):
    e=witness("wire-accounting",origin="root-pcap-unique-tcp",unique_tcp_payload_bytes=1000,
              final=True,coverage="all-owned-server-connections-from-connect")
    e["selected_slow_terminal"]=terminal()
    e.update(changes);o.connections_closed.set();o.submit(e)


def status():
    s=dict(station="station",title="title",format="Opus",connecting=False,audio=False,
           smartstart=False,normalization=False,network_online=True,ap_enabled=False,
           rssi_valid=False,bitrate=0,generation=1,volume=50,balance=0,current=1,count=1,
           normgain=0,normtarget=-12,normtime=1000,rssi=0)
    values=dict(nameset="name",meta="title",volume=50,balance=0,rssi=0,heap=0,
                bitrate=0,fmt="Opus",playerwrap="stopped")
    return dict(status=s,payload=[dict(id=k,value=v) for k,v in values.items()])


def frame(opcode,body):
    if not isinstance(body,bytes):body=json.dumps(body,separators=(",",":")).encode()
    return p.client.encode_frame(opcode,body,mask=False)


class ScriptSocket:
    """In-memory byte script. Reuses the frozen parser for client frames too."""
    def __init__(self,body=b"",on_command=None):
        self.body=bytearray(body);self.lock=threading.Lock();self.closed=False
        self.eof=False;self.on_command=on_command;self.commands=0;self.after_mode=None
    def settimeout(self,value):pass
    def getsockname(self):return ("127.0.0.1",12345)
    def close(self):self.closed=True
    def shutdown(self,*args):self.closed=True
    def append(self,body):
        with self.lock:self.body.extend(body)
    def recv(self,maximum):
        with self.lock:
            if self.body:
                part=bytes(self.body[:maximum]);del self.body[:maximum];return part
            if self.eof or self.closed:return b""
        raise socket.timeout()
    def send(self,body):
        # Every scripted write is a complete tiny client frame. A malformed
        # mask/direction/length must still fail in the original FrameReader.
        tiny=ScriptSocket(bytes(body));tiny.eof=True
        f=p.client.FrameReader(p.client.WireIO(tiny),expect_mask=True).read(p.client.Budget(1))
        if f["opcode"]==1:
            assert f["payload"]==b"getindex" and f["final"]
            self.commands+=1
            self.append(frame(1,status())+frame(1,{"current":1})+
                        frame(1,{"playermode":"modeweb"})+frame(1,{"file":"/data/playlist.csv"}))
            if self.on_command:self.on_command(self)
        elif f["opcode"]==9:self.append(frame(10,f["payload"]))
        elif f["opcode"]==8:
            self.append(frame(8,f["payload"]));self.eof=True
        return len(body)


def session(sock):
    return p.Session(p.client.WireIO(p.SocketGate(sock)))


class Tests(unittest.TestCase):
    def test_frozen_pin_and_exact_reader(self):
        self.assertEqual(hashlib.sha256(p.FROZEN_PATH.read_bytes()).hexdigest(),p.FROZEN_SHA256)
        s=session(ScriptSocket());self.assertIs(type(s.reader),p.client.FrameReader)
        self.assertTrue(issubclass(p.Session,p.client.Session))

    def test_declared_bounds(self):
        d=p.declaration();self.assertLessEqual(d["max_commands"],1024)
        self.assertLess(d["max_commands"],1024)
        self.assertLess(d["max_command_wire_bytes"],16384)
        self.assertLessEqual(d["max_application_ws_bytes"]+d["separate_tls_reserve"],8*1024*1024)
        self.assertEqual(d["case_watchdog_seconds"],30)
        self.assertEqual(d["io_cutoff_seconds"]+d["cleanup_seconds"],30)
        self.assertFalse(d["tls_record_count_inferred"])

    def test_preconnect_buffer_order_and_failure_cleanup(self):
        calls=[]
        class Raw:
            def settimeout(self,x):calls.append("timeout")
            def setsockopt(self,l,k,v):calls.append((k,v))
            def getsockopt(self,l,k):return 4096
            def connect(self,address):calls.append("connect")
            def close(self):calls.append("close")
        f=p.SocketFactory(lambda *args:Raw());f.create_connection(("127.0.0.1",123),1)
        self.assertLess(calls.index((socket.SO_RCVBUF,2048)),calls.index("connect"))
        self.assertEqual(f.actual_buffers,[4096])
        class Broken(Raw):
            def connect(self,address):raise OSError()
        with self.assertRaises(OSError):p.SocketFactory(lambda *args:Broken()).create_connection(("::1",1),1)
        self.assertEqual(calls[-1],"close")

    def test_wss_uses_exact_frozen_verifier_and_cipher(self):
        calls=[]
        class TLS:
            def version(self):return "TLSv1.2"
            def getpeercert(self,binary_form=False):return b"scripted-public-cert"
            def cipher(self):return (p.TLS_CIPHER,"TLSv1.2",256)
            def close(self):calls.append("tls-close")
        class Raw:
            def setsockopt(self,*a):pass
            def settimeout(self,*a):pass
            def close(self):calls.append("raw-close")
        class Context:
            verify_mode=p.ssl.CERT_REQUIRED;check_hostname=True;verify_flags=0
            def set_ciphers(self,c):calls.append(c)
            def wrap_socket(self,raw,**kw):calls.append(kw);return TLS()
        c=Context()
        with mock.patch.object(p.client,"strict_context",return_value=c):
            ep=p.Endpoint("wss://localhost:1/ws",Path("not-read.pem"))
        ep.socket_factory.create_connection=lambda *a,**k:Raw()
        _,m=ep.dial(p.client.Budget(1))
        self.assertEqual(m["cipher"],p.TLS_CIPHER)
        self.assertIn(dict(server_hostname="localhost",suppress_ragged_eofs=False),calls)
        self.assertTrue(m["host_date_verification_enabled"] and m["hostname_checked"])
        c.check_hostname=False
        with self.assertRaises(p.client.CheckFailure):ep.dial(p.client.Budget(1))

    def test_complete_group_trailing_playlist_and_initialization(self):
        initial=frame(1,status())+frame(1,{"current":1})+frame(1,{"playermode":"modeweb"})
        s=session(ScriptSocket(initial));r=p.barrier_group(s,p.Budget(time.monotonic()+1),b"calSlow1",p.Commands())
        self.assertEqual(r["complete_groups"],2)
        self.assertEqual(len(s.wire.buffer),0)
        self.assertGreater(r["server_ws_bytes"],len(json.dumps(status()).encode()))

    def test_status_schema_negative_controls(self):
        p.validate_status(status())
        for mutate in (lambda x:x["payload"].pop(),lambda x:x["status"].update(audio=1),
                       lambda x:x["payload"].append(x["payload"][0]),
                       lambda x:x["status"].pop("normtime"),
                       lambda x:x["status"].update(current=65536)):
            obj=status();mutate(obj)
            with self.assertRaises(p.FixtureError):p.validate_status(obj)

    def test_missing_wrong_fd_deadline_and_host_witness_rejected(self):
        bad=[dict(guest_fd=8),dict(pcb="0x9999"),dict(deadline_us=1000201),
             dict(origin="host-elapsed"),dict(evidence_sha256=""),dict(elf_sha256="c"*64)]
        for changes in bad:
            o=observer()
            with self.assertRaises(p.FixtureError):o.submit(witness(**changes))
            self.assertIsNone(o.snapshot()["pressure"])
        e=witness();del e["guest_fd"]
        with self.assertRaises(p.FixtureError):observer().submit(e)

    def test_same_frame_deadline_and_no_snapshot_mutation(self):
        o=observer();o.submit(witness());self.assertTrue(o.stop.is_set())
        snap=o.snapshot();snap["pressure"]["guest_fd"]=9
        self.assertEqual(o.snapshot()["pressure"]["guest_fd"],7)
        with self.assertRaises(p.FixtureError):o.submit(witness("guest-timeout",frame_id="frame-2"))
        good=observer();good.submit(witness());good.submit(witness("guest-timeout"))
        self.assertIsNotNone(good.snapshot()["timeout"])

    def test_select_zero_basis_actual_ticks_no_invented_clock(self):
        o=observer();o.submit(witness())
        e=witness("guest-timeout",observed_us=None,timeout_basis="select-zero-original-remainder",
                  preselect_us=300,remaining_us=999900,timeval_us=999900,select_result=0,
                  caller_result=-3,tick_before=4294967000,tick_after=704,tick_delta=1000,tick_hz=1000)
        o.submit(e);r=o.snapshot()["timeout"]
        self.assertIsNone(r["observed_us"]);self.assertFalse(r["post_select_timer_observed"])
        self.assertEqual(r["tick_lateness_estimate_us"],100)
        for change in (dict(timeval_us=999899),dict(tick_delta=1,tick_after=4294967001),
                       dict(select_result=1),dict(caller_result=0),dict(tick_hz=100)):
            x=observer();x.submit(witness());bad=dict(e,**change)
            with self.assertRaises(p.FixtureError):x.submit(bad)
        for change in (dict(would_block_write=False),dict(guest_queue={}),dict(inputs_sha256="0"*64)):
            with self.assertRaises(p.FixtureError):observer().submit(witness(**change))
        e=witness();e["debugger"]["max_observed_stop_seconds"]=3
        with self.assertRaises(p.FixtureError):observer().submit(e)

    def test_no_reads_while_withheld_and_close_not_eof(self):
        s=session(ScriptSocket(frame(8,p.client.close_payload())))
        g=s.wire.sock;g.withheld=True
        with self.assertRaises(p.FixtureError):s.event(p.client.Budget(1))
        self.assertEqual(g.read_calls,0)
        s.wire.buffer.extend(frame(10,b"buffered"))
        before=bytes(s.wire.buffer)
        with self.assertRaises(p.FixtureError):s.event(p.client.Budget(1))
        self.assertEqual(bytes(s.wire.buffer),before)
        s.wire.buffer.clear()
        g.withheld=False;self.assertEqual(s.event(p.client.Budget(1))[0],"close")
        self.assertFalse(s.transport_eof)
        s.close_transport()
        with self.assertRaises(p.client.PeerEOF):s.event(p.client.Budget(1))
        self.assertFalse(s.transport_eof)
        remote=session(ScriptSocket());remote.wire.sock.sock.eof=True
        with self.assertRaises(p.client.PeerEOF):remote.event(p.client.Budget(1))
        self.assertTrue(remote.transport_eof)

    def test_command_and_io_bounds_and_stop_before_send(self):
        s=session(ScriptSocket());cmd=p.Commands();cmd.attempted=p.COMMAND_CAP
        with self.assertRaises(p.FixtureError):cmd.one(s,p.client.Budget(1))
        o=observer();o.submit(witness());cmd=p.Commands()
        with self.assertRaises(p.StopStimulus):cmd.one(s,p.Budget(time.monotonic()+1,o.stop))
        self.assertEqual(s.wire.sent_bytes,0)
        m=p.Meter();m.add("client",16383)
        with self.assertRaises(p.FixtureError):m.add("client",1)
        with self.assertRaises(p.FixtureError):m.add("server",p.APP_BOUND+1)
        with self.assertRaises(p.FixtureError):p.Budget(time.monotonic()-1).remaining()

    def test_no_witness_no_final_accounting_no_eof_promotion(self):
        base=dict(mode="withheld",errors=[],threads_joined=True,healthy_progress_after_stimulus=True,
                  slow_resume_pong=False,slow_transport_eof=True,slow_close_seen=True,
                  commands_attempted=4,attempted_client_ws_bytes=100,decoded_server_ws_bytes=1000,
                  elapsed_seconds=1,withheld_read_calls=0,partial_command_frames=0,
                  sender_joined_before_read=True,slow_closed_before_reader=False,
                  slow_io_overlaps=0,healthy_io_overlaps=0)
        base.update(slow_remote_reset=False,slow_secure=False,slow_clean_tls_eof=None,
                    slow_termination_kind="orderly-eof",local_closed_at_termination=False,
                    watchdog_fired=False,observation_exhausted=False)
        o=observer();wire(o)
        self.assertEqual(p.finish_report(dict(base),o)["state"],"INCOMPLETE")
        o=observer();o.submit(witness());o.submit(witness("guest-timeout"))
        self.assertEqual(p.finish_report(dict(base),o)["state"],"INCOMPLETE")
        wire(o);base.update(slow_reader_timeout_token=p.timeout_token(o.snapshot()),slow_termination_token=p.timeout_token(o.snapshot()))
        self.assertEqual(p.finish_report(dict(base),o)["pressure_objective"],"PASS")
        o.incomplete("debugger-budget-exhausted")
        self.assertEqual(p.finish_report(dict(base),o)["state"],"INCOMPLETE")
        no_eof=dict(base,slow_transport_eof=False)
        self.assertEqual(p.finish_report(no_eof,o)["state"],"INCOMPLETE")
        with self.assertRaises(p.FixtureError):wire(observer(),unique_tcp_payload_bytes=p.TCP_LIMIT+1)

    def test_final_wire_accounting_cannot_precede_cleanup(self):
        o=observer();e=witness("wire-accounting",origin="root-pcap-unique-tcp",unique_tcp_payload_bytes=1000,
                             final=True,coverage="all-owned-server-connections-from-connect")
        with self.assertRaises(p.FixtureError):o.submit(e)

    def test_scripted_watchdog_joins_all_workers(self):
        o=observer()
        def factory(role,ep):
            sock=ScriptSocket();s=session(sock)
            ep.owned_sockets.append(sock);ep.gates.append(s.wire.sock);return s
        with mock.patch.object(p.socket,"socket",side_effect=AssertionError("live socket forbidden")),mock.patch.object(p,"CASE_SECONDS",.5),mock.patch.object(p,"CLEANUP_SECONDS",.2):
            r=p.run("ws://localhost:1/ws",o,peer_factory=factory)
        self.assertTrue(r["threads_joined"],r)
        self.assertTrue(r["observation_exhausted"],r)
        self.assertLess(r["elapsed_seconds"],.6)
        self.assertEqual(r["state"],"INCOMPLETE",r)
        self.assertFalse(any(t.name.startswith("pressure-") for t in threading.enumerate()))

    def test_same_socket_cross_thread_io_rejected_without_read_lock(self):
        entered=threading.Event();release=threading.Event();result=[]
        class Blocked(ScriptSocket):
            def recv(self,maximum):
                entered.set();release.wait(1);raise socket.timeout()
        s=session(Blocked())
        def read():
            try:s.event(p.client.Budget(1))
            except socket.timeout:result.append("read-unblocked")
        t=threading.Thread(target=read);t.start();self.assertTrue(entered.wait(1))
        began=time.monotonic()
        try:
            with self.assertRaises(p.FixtureError):s.send(9,b"control1",budget=p.client.Budget(1))
            self.assertLess(time.monotonic()-began,.2)
        finally:release.set();t.join(1)
        self.assertFalse(t.is_alive());self.assertEqual(result,["read-unblocked"])
        self.assertEqual(s.wire.sock.io_overlaps,1)

    def test_scripted_modes_threads_cleanup_no_live_socket(self):
        # Small bounded scripted runs exercise the actual ownership/thread paths.
        # Socket constructor is forbidden; peer_factory supplies in-memory scripts.
        for mode in ("withheld","read-resume","drained"):
            o=observer();sockets={}
            def on_command(sock):
                if mode!="drained" and sock.commands==3:
                    slow=sockets["slow"][1]
                    self.assertTrue(slow.wire.sock.withheld)
                    self.assertEqual(slow.wire.sock.read_calls,o.phase["slow_read_calls"])
                    o.submit(witness())
                    if mode=="withheld":
                        o.submit(witness("guest-timeout"));sock.eof=True
            def factory(role,ep):
                sock=ScriptSocket(on_command=on_command if role=="slow" else None)
                s=session(sock);ep.owned_sockets.append(sock);ep.gates.append(s.wire.sock)
                sockets[role]=(sock,s,0)
                return s
            # Calibration read count is learned before the third command callback.
            original=p.barrier_group
            def barrier(s,*a):
                r=original(s,*a)
                if "slow" in sockets and s is sockets["slow"][1]:
                    sockets["slow"]=(sockets["slow"][0],s,s.wire.sock.read_calls)
                return r
            with mock.patch.object(p.socket,"socket",side_effect=AssertionError("live socket forbidden")),mock.patch.object(p,"barrier_group",side_effect=barrier):
                r=p.run("ws://localhost:1/ws",o,mode=mode,peer_factory=factory)
            self.assertTrue(r["threads_joined"],r)
            self.assertFalse(any(t.name.startswith("pressure-") for t in threading.enumerate()))
            self.assertLessEqual(r["commands_attempted"],p.COMMAND_CAP)
            self.assertEqual(r["slow_io_overlaps"],0,r)
            self.assertEqual(r["healthy_io_overlaps"],0,r)
            if mode!="drained":
                self.assertTrue(r["sender_joined_before_read"],r)
                self.assertFalse(r["slow_closed_before_reader"],r)
                self.assertFalse(r["slow_eof_observed_at_sender_join"],r)
            self.assertEqual(r["state"],"INCOMPLETE") # No PCAP final event yet.
            wire(o);p.finish_report(r,o)
            self.assertEqual(r["state"],"PASS",r)
            self.assertEqual(r["pressure_objective"],"PASS" if mode=="withheld" else "INCOMPLETE")


def complete_report(o,kind="remote-reset",mode="withheld",secure=False):
    token=p.timeout_token(o.snapshot())if o.snapshot()["timeout"]else None
    return dict(mode=mode,errors=[],threads_joined=True,healthy_progress_after_stimulus=True,
        slow_resume_pong=mode!="withheld",slow_transport_eof=kind!="remote-reset",slow_close_seen=mode!="withheld",
        commands_attempted=3,attempted_client_ws_bytes=42,decoded_server_ws_bytes=1000,elapsed_seconds=1,
        withheld_read_calls=0,partial_command_frames=0,sender_joined_before_read=True,slow_closed_before_reader=False,
        slow_io_overlaps=0,healthy_io_overlaps=0,slow_remote_reset=kind=="remote-reset",slow_secure=secure,
        slow_clean_tls_eof=False if kind=="tls-ragged-eof" else True if secure else None,
        slow_termination_kind=kind,local_closed_at_termination=False,slow_reader_timeout_token=token,
        slow_termination_token=copy.deepcopy(token),slow_normal_close_sent=mode!="withheld",slow_normal_close_received=mode!="withheld",
        watchdog_fired=False,observation_exhausted=False)


class RemoteTerminationTests(unittest.TestCase):
    def timed(self):
        o=observer();o.submit(witness());o.submit(witness("guest-timeout"));return o

    def test_receive_reset_distinct_from_EOF_and_local_or_send_reset(self):
        class Reset(ScriptSocket):
            def recv(self,n):raise ConnectionResetError("fixture")
        s=session(Reset())
        with self.assertRaises(p.ReceiveReset):s.event(p.client.Budget(1))
        self.assertTrue(s.transport_reset);self.assertFalse(s.transport_eof)
        self.assertEqual(s.termination_kind,"remote-reset")
        local=session(Reset());local.close_transport()
        with self.assertRaises(ConnectionResetError)as caught:local.event(p.client.Budget(1))
        self.assertNotIsInstance(caught.exception,p.ReceiveReset)
        self.assertFalse(local.transport_reset);self.assertFalse(local.transport_eof)
        class SendReset(ScriptSocket):
            def send(self,body):raise ConnectionResetError("fixture send")
        send=session(SendReset(frame(9,b"pingdata")))
        with self.assertRaises(ConnectionResetError)as caught:send.event(p.client.Budget(1))
        self.assertNotIsInstance(caught.exception,p.ReceiveReset)
        self.assertFalse(send.transport_reset)

    def test_ragged_tls_and_verification_failure_are_not_reset(self):
        class Ragged(ScriptSocket):
            def recv(self,n):raise p.ssl.SSLEOFError()
        s=p.Session(p.client.WireIO(p.SocketGate(Ragged()),secure=True))
        with self.assertRaises(p.client.PeerEOF)as caught:s.event(p.client.Budget(1))
        self.assertIs(caught.exception.clean_tls,False)
        self.assertTrue(s.transport_eof);self.assertFalse(s.transport_reset)
        self.assertEqual(s.termination_kind,"tls-ragged-eof")
        class Verify(ScriptSocket):
            def recv(self,n):raise p.ssl.SSLCertVerificationError("fixture verification")
        s=p.Session(p.client.WireIO(p.SocketGate(Verify()),secure=True))
        with self.assertRaises(p.ssl.SSLCertVerificationError):s.event(p.client.Budget(1))
        self.assertFalse(s.transport_eof or s.transport_reset)

    def test_reset_pending_until_final_matching_server_RST(self):
        o=self.timed();report=complete_report(o)
        self.assertEqual(p.finish_report(report,o)["state"],"INCOMPLETE")
        wire(o,selected_slow_terminal=terminal(server_rst=1,fin=False))
        self.assertEqual(p.finish_report(report,o)["pressure_objective"],"PASS")
        self.assertFalse(report["slow_transport_eof"])
        self.assertEqual(report["slow_termination_kind"],"remote-reset")

    def test_peer_only_RST_missing_witness_or_bad_handoff_never_pass(self):
        for change in (dict(sender_joined_before_read=False),dict(local_closed_at_termination=True),
                       dict(slow_closed_before_reader=True),dict(withheld_read_calls=1),dict(partial_command_frames=1),
                       dict(slow_reader_timeout_token=None),dict(slow_termination_token=None),dict(errors=["ConnectionResetError"])):
            o=self.timed();report=complete_report(o);report.update(change)
            wire(o,selected_slow_terminal=terminal(server_rst=1,fin=False))
            with self.subTest(change=change):self.assertNotEqual(p.finish_report(report,o)["state"],"PASS")
        o=self.timed();report=complete_report(o)
        wire(o,selected_slow_terminal=terminal(peer_rst=1,fin=False))
        self.assertEqual(p.finish_report(report,o)["state"],"INCOMPLETE")
        o=observer();report=complete_report(o)
        wire(o,selected_slow_terminal=terminal(server_rst=1,fin=False))
        self.assertNotEqual(p.finish_report(report,o)["state"],"PASS")

    def test_plain_and_ragged_EOF_require_real_abort_and_server_termination(self):
        for kind,secure in (("orderly-eof",False),("tls-ragged-eof",True)):
            for proof,expected in ((terminal(server_rst=1,fin=False),"PASS"),
                                   (terminal(),"PASS"),(terminal(peer_rst=1,fin=False),"INCOMPLETE")):
                o=self.timed();report=complete_report(o,kind,secure=secure);wire(o,selected_slow_terminal=proof)
                with self.subTest(kind=kind,proof=proof["terminal_basis"],server=proof["server"]["rsts"]):
                    self.assertEqual(p.finish_report(report,o)["state"],expected)
                    self.assertFalse(report["slow_remote_reset"])

    def test_controls_require_exact_normal_Close_and_orderly_TLS(self):
        for mode in ("drained","read-resume"):
            for kind,secure,proof,change,expected in (
                ("orderly-eof",False,terminal(),{},"PASS"),
                ("orderly-eof",True,terminal(),{},"PASS"),
                ("remote-reset",False,terminal(server_rst=1,fin=False),{},"INCOMPLETE"),
                ("tls-ragged-eof",True,terminal(),{},"INCOMPLETE"),
                ("orderly-eof",False,terminal(),dict(slow_normal_close_sent=False),"INCOMPLETE"),
                ("orderly-eof",False,terminal(),dict(slow_normal_close_received=False),"INCOMPLETE"),
                ("orderly-eof",False,terminal(),dict(slow_resume_pong=False),"INCOMPLETE")):
                o=observer()
                if mode=="read-resume":o.submit(witness())
                report=complete_report(o,kind,mode,secure);report.update(change);wire(o,selected_slow_terminal=proof)
                with self.subTest(mode=mode,kind=kind,change=change):self.assertEqual(p.finish_report(report,o)["state"],expected)

    def test_exact_close_payload_recorded_only_after_complete_send(self):
        s=session(ScriptSocket());s.send(8,p.client.close_payload())
        self.assertTrue(s.normal_close_sent)
        s=session(ScriptSocket());s.send(8,p.client.close_payload(1001))
        self.assertFalse(s.normal_close_sent)

    def test_both_timeout_bases_require_actual_caller_minus_three(self):
        for value in (None,0,False,-2):
            o=observer();o.submit(witness())
            e=witness("guest-timeout",caller_result=value)
            with self.subTest(value=value),self.assertRaises(p.FixtureError):o.submit(e)

    def test_final_proof_never_promotes_expired_or_missing_watchdog_state(self):
        for field in ("watchdog_fired","observation_exhausted"):
            for value in (True,None):
                o=self.timed();report=complete_report(o);report[field]=value
                wire(o,selected_slow_terminal=terminal(server_rst=1,fin=False))
                with self.subTest(field=field,value=value):self.assertNotEqual(p.finish_report(report,o)["state"],"PASS")

    def test_final_proof_shape_owner_tuple_and_no_inference(self):
        mutations=[lambda x:x.update(role="healthy"),lambda x:x.update(guest_fd=8),lambda x:x.update(pcb="0x9999"),
                   lambda x:x["guest_tuple"].update(remote_port=42001),lambda x:x.update(missing_bytes_inferred=True),
                   lambda x:x.update(captured_ranges_contiguous=False),lambda x:x["server"].update(sequence_end=2),
                   lambda x:x["server"].update(fin_offset=1),lambda x:x["peer"].update(max_ack=999999),
                   lambda x:x["server"].update(rsts=True),lambda x:x["server"].update(payload_bytes=0),
                   lambda x:x.update(extra="forbidden")]
        for mutate in mutations:
            o=self.timed();proof=terminal(server_rst=1,fin=False);mutate(proof)
            with self.subTest(mutate=mutate),self.assertRaises(p.FixtureError):wire(o,selected_slow_terminal=proof)
        o=self.timed()
        with self.assertRaises(p.FixtureError):wire(o,final=False)
        o=self.timed();wire(o,selected_slow_terminal=terminal(server_rst=1,fin=False))
        snap=o.snapshot();snap["wire"]["selected_slow_terminal"]["server"]["rsts"]=999
        self.assertEqual(o.snapshot()["wire"]["selected_slow_terminal"]["server"]["rsts"],1)

    def test_actual_reader_reset_handoff_and_sender_reset_never_promoted(self):
        for sender_failure in (False,True):
            o=observer();sockets={}
            class ResetAfterDrain(ScriptSocket):
                reset=False
                def recv(self,n):
                    with self.lock:empty=not self.body
                    if self.reset and empty:raise ConnectionResetError("fixture actual receive")
                    return super().recv(n)
            def on_command(sock):
                if sock.commands==3:
                    self.assertTrue(sockets["slow"].wire.sock.withheld)
                    o.submit(witness());o.submit(witness("guest-timeout"))
                    if sender_failure:raise ConnectionResetError("fixture sender")
                    sock.reset=True
            def factory(role,ep):
                sock=ResetAfterDrain(on_command=on_command if role=="slow" else None)
                s=session(sock);ep.owned_sockets.append(sock);ep.gates.append(s.wire.sock);sockets[role]=s;return s
            with mock.patch.object(p.socket,"socket",side_effect=AssertionError("live socket forbidden")):
                report=p.run("ws://localhost:1/ws",o,peer_factory=factory)
            self.assertTrue(report["threads_joined"])
            self.assertFalse(any(t.name.startswith("pressure-") for t in threading.enumerate()))
            wire(o,selected_slow_terminal=terminal(server_rst=1,fin=False));p.finish_report(report,o)
            if sender_failure:
                self.assertEqual(report["state"],"FAIL",report)
                self.assertIn("ConnectionResetError",report["errors"])
            else:
                self.assertEqual(report["pressure_objective"],"PASS",report)
                self.assertTrue(report["slow_remote_reset"]);self.assertFalse(report["slow_transport_eof"])
                self.assertTrue(report["sender_joined_before_read"])
                self.assertFalse(report["local_closed_at_termination"])


class PositiveWindowTests(unittest.TestCase):
    def event(self,*,seq=1000,lastack=1000):
        raw=int.from_bytes(seq.to_bytes(4,"big"),"little");delta=(seq-lastack)&0xffffffff
        queue=dict(snd_wnd=286,snd_buf=0,snd_queuelen=4,unsent="0x123456",unacked="0x234567",cwnd=24500,lastack=lastack,
                   unsent_head=dict(pointer="0x123456",tcphdr_pointer="0x345678",len=1440,seqno_raw=raw,seqno_host=seq,
                                    seqno_conversion="ntohl-u32-from-little-endian-target",seq_distance=delta,sequence_end=delta+1440))
        return witness(pressure_basis="positive-peer-window-unsent-head-blocked",guest_queue=queue)

    def test_positive_small_window_head_and_wrap_supported(self):
        for seq,lastack in ((1000,1000),(0x10,0xfffffff0)):
            o=observer();e=self.event(seq=seq,lastack=lastack);o.submit(e)
            self.assertEqual(o.snapshot()["pressure"]["guest_queue"],e["guest_queue"])
            self.assertTrue(o.stop.is_set())

    def test_false_positive_window_and_endian_relations_rejected(self):
        changes=[lambda q:q.update(snd_buf=1),lambda q:q.update(cwnd=200),lambda q:q.update(snd_wnd=0),
                 lambda q:q["unsent_head"].update(tcphdr_pointer="0x0"),lambda q:q["unsent_head"].update(pointer="0x1111"),
                 lambda q:q["unsent_head"].update(len=0),lambda q:q["unsent_head"].update(seqno_host=1001),
                 lambda q:q["unsent_head"].update(sequence_end=1441),lambda q:q.update(lastack=1001),
                 lambda q:q["unsent_head"].update(seqno_conversion="host-assumed")]
        for change in changes:
            e=self.event();change(e["guest_queue"])
            with self.subTest(change=change),self.assertRaises(p.FixtureError):observer().submit(e)


if __name__=="__main__":
    unittest.main()
