"""Private, finite pressure fixture. Importing this module never opens a socket.

Root owns execution and the trusted GDB/PCAP observer. This is a NEW finite
experiment, not a retry of R06. run() accepts an Observer; root can bind it and
submit events from its own controller. No socket is opened by the script entry
point. Read this declaration before running against an endpoint.

The 8 MiB envelope is UNIQUE server TCP payload, including TLS ciphertext, not
IP/TCP headers or retransmissions. Legal application output is bounded below;
2 MiB is separately reserved for TLS/handshake overhead. This reserve is NOT a
record-count proof. A root PCAP guard armed before connecting and final complete
accounting are mandatory for PASS. Host received bytes never replace that proof.
The caller must supply real source/ELF/fd/PCB/frame-bound GDB evidence; accepting
its schema does not authenticate the controller. EOF/Close/time/queue occupancy
never create a guest witness. Controls have separate outcomes from the pressure
objective. All application commands are exactly b'getindex'; Ping barriers are
protocol controls, not padding or application mutations.
"""
from __future__ import annotations

import contextlib
import copy
import dataclasses
import hashlib
import importlib.util
import ipaddress
import json
import math
from pathlib import Path
import re
import socket
import ssl
import sys
import threading
import time
import types

FROZEN_SHA256 = "3dcfc669de604238fd237ee5490e794f9988e547aa7de3a8c343d8fa57bae9f0"
FROZEN_PATH = Path(__file__).resolve().parents[1] / "cws-stream26/client-draft/rfc-target-client.py"
assert hashlib.sha256(FROZEN_PATH.read_bytes()).hexdigest() == FROZEN_SHA256
_spec = importlib.util.spec_from_file_location("pressure_frozen_rfc_client", FROZEN_PATH)
client = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = client
_spec.loader.exec_module(client)

CASE_SECONDS = 30.0
CLEANUP_SECONDS = 3.0
TCP_LIMIT = 8 * 1024 * 1024
TLS_RESERVE = 2 * 1024 * 1024
CONTROL_RESERVE = 64 * 1024
COMMAND = b"getindex"
TLS_CIPHER = "ECDHE-RSA-AES256-GCM-SHA384"
RCVBUF = 2048
STATUS_FRAME_MAX = 5119 + 4  # Source capacity 5120 reserves its NUL; one FIN frame.
CURRENT_FRAME_MAX = len(b'{"current":65535}') + 2
MODE_FRAME_MAX = len(b'{"playermode":"modeweb"}') + 2
PLAYLIST_FRAME_MAX = len(b'{"file":"/data/playlist.csv"}') + 2
GROUP_MAX = STATUS_FRAME_MAX + CURRENT_FRAME_MAX + MODE_FRAME_MAX + PLAYLIST_FRAME_MAX
# Both peers may change on every 100 ms poll. Include current/playlist every
# time, even though actual nonmutating operation normally sends much less.
UNSOLICITED_RESERVE = 2 * (math.ceil(CASE_SECONDS / .1) + 1) * GROUP_MAX
INITIAL_RESERVE = 2 * GROUP_MAX
COMMAND_CAP = min(1024, (TCP_LIMIT - TLS_RESERVE - CONTROL_RESERVE -
                         UNSOLICITED_RESERVE - INITIAL_RESERVE) // GROUP_MAX)
assert 16 < COMMAND_CAP <= 1024 and COMMAND_CAP * 14 < 16 * 1024
APP_BOUND = COMMAND_CAP * GROUP_MAX + UNSOLICITED_RESERVE + INITIAL_RESERVE + CONTROL_RESERVE
assert APP_BOUND + TLS_RESERVE <= TCP_LIMIT
SLOW_COMMANDS = min(COMMAND_CAP-14, (16383-2048)//28)


class FixtureError(Exception):
    pass


class StopStimulus(Exception):
    pass


class ReceiveReset(ConnectionResetError):
    """Actual recv-origin reset, distinct from sender errors and local cleanup."""
    def __init__(self, gate):
        super().__init__("remote-receive-reset")
        self.gate = gate


def need(value, category):
    if not value:
        raise FixtureError(category)


def declaration():
    return dict(case_watchdog_seconds=CASE_SECONDS, io_cutoff_seconds=CASE_SECONDS-CLEANUP_SECONDS,
                cleanup_seconds=CLEANUP_SECONDS, max_commands=COMMAND_CAP,
                hard_max_commands=1024, command_payload_bytes=8,
                max_command_wire_bytes=COMMAND_CAP*14, max_application_ws_bytes=APP_BOUND,
                slow_stimulus_commands=SLOW_COMMANDS, planned_total_commands=SLOW_COMMANDS+13,
                max_total_attempted_client_ws_bytes=16383,
                max_legal_group_bytes=GROUP_MAX, unsolicited_reserve=UNSOLICITED_RESERVE,
                initialization_reserve=INITIAL_RESERVE, control_reserve=CONTROL_RESERVE,
                separate_tls_reserve=TLS_RESERVE, max_unique_server_tcp_payload=TCP_LIMIT,
                tls_cipher=TLS_CIPHER, tls_record_count_inferred=False, receive_buffer_requested=RCVBUF,
                max_inflight_stimulus_bytes=14, syscall_timeout_seconds=.1,
                frozen_client_sha256=FROZEN_SHA256)


@dataclasses.dataclass(frozen=True)
class Binding:
    run_id: str
    source_commit: str
    elf_sha256: str
    guest_fd: int
    pcb: str
    inputs_sha256: str

    def __post_init__(self):
        need(bool(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", self.run_id)), "binding-run")
        need(bool(re.fullmatch(r"[0-9a-f]{40}", self.source_commit)), "binding-source")
        need(bool(re.fullmatch(r"[0-9a-f]{64}", self.elf_sha256)), "binding-elf")
        need(type(self.guest_fd) is int and self.guest_fd >= 0, "binding-fd")
        need(bool(re.fullmatch(r"0x[0-9a-f]+", self.pcb)), "binding-pcb")
        need(bool(re.fullmatch(r"[0-9a-f]{64}", self.inputs_sha256)), "binding-inputs")


def validate_guest_tuple(value):
    need(isinstance(value,dict) and set(value)=={"local_ip","remote_ip","local_port","remote_port"},"guest-tuple-shape")
    for key in ("local_ip","remote_ip"):
        need(isinstance(value[key],str),"guest-tuple-ip")
        try: need(str(ipaddress.IPv4Address(value[key]))==value[key],"guest-tuple-ip")
        except ipaddress.AddressValueError: raise FixtureError("guest-tuple-ip")
    need(type(value["local_port"])is int and value["local_port"]in(80,443) and
         type(value["remote_port"])is int and 0<value["remote_port"]<65536,"guest-tuple-ports")
    return dict(value)


def pointer(value, *, nonzero=False):
    need(isinstance(value,str) and re.fullmatch(r"0x(?:0|[1-9a-f][0-9a-f]{0,7})",value),"queue-pointer")
    need(not nonzero or int(value,16)>0,"queue-pointer-zero")
    return value


def pressure_queue(event):
    queue=event.get("guest_queue")
    need(isinstance(queue,dict),"guest-queue-missing")
    base={"snd_wnd","snd_buf","snd_queuelen","unsent","unacked"}
    need(all(type(queue.get(k))is int and 0<=queue[k]<=0xffffffff for k in
             ("snd_wnd","snd_buf","snd_queuelen")) and queue["snd_queuelen"]>0,"guest-queue-counts")
    for key in ("unsent","unacked"): pointer(queue.get(key))
    need(int(queue["unsent"],16)>0 or int(queue["unacked"],16)>0,"guest-tx-queue-not-retained")
    basis=event.get("pressure_basis")
    need(event.get("guest_queue_sample_site")=="actual-would-block-branch","guest-queue-site")
    if basis=="zero-peer-window":
        need(set(queue)==base and queue["snd_wnd"]==0,"zero-window-proof")
    elif basis=="positive-peer-window-unsent-head-blocked":
        need(set(queue)==base|{"cwnd","lastack","unsent_head"},"positive-window-queue-shape")
        need(all(type(queue.get(k))is int and 0<=queue[k]<=0xffffffff for k in ("cwnd","lastack")),"positive-window-scalars")
        head=queue["unsent_head"]
        need(isinstance(head,dict) and set(head)=={"pointer","tcphdr_pointer","len","seqno_raw","seqno_host","seqno_conversion","seq_distance","sequence_end"},"unsent-head-shape")
        pointer(head["pointer"],nonzero=True);pointer(head["tcphdr_pointer"],nonzero=True)
        need(head["pointer"]==queue["unsent"],"unsent-head-owner")
        need(type(head["len"])is int and 0<head["len"]<=65535,"unsent-head-length")
        need(all(type(head[k])is int and 0<=head[k]<=0xffffffff for k in ("seqno_raw","seqno_host","seq_distance","sequence_end")),"unsent-head-sequence-scalars")
        need(head["seqno_conversion"]=="ntohl-u32-from-little-endian-target" and
             int.from_bytes(head["seqno_raw"].to_bytes(4,"little"),"big")==head["seqno_host"],"unsent-head-network-order")
        delta=(head["seqno_host"]-queue["lastack"])&0xffffffff
        end=delta+head["len"]
        need(delta<0x80000000 and end<0x80000000 and head["seq_distance"]==delta and
             head["sequence_end"]==end,"unsent-head-sequence-envelope")
        need(queue["snd_buf"]==0 and 0<queue["snd_wnd"]<=queue["cwnd"] and end>queue["snd_wnd"],"positive-window-head-not-blocked")
    else: raise FixtureError("pressure-basis-missing")
    return copy.deepcopy(queue)


def selected_terminal(value, binding, expected_tuple):
    need(isinstance(value,dict) and set(value)=={"role","guest_fd","pcb","guest_tuple","terminal_basis","server","peer","captured_ranges_contiguous","missing_bytes_inferred"},"terminal-proof-shape")
    need(value["role"]=="slow" and type(value["guest_fd"])is int and value["guest_fd"]==binding.guest_fd and
         value["pcb"]==binding.pcb,"terminal-proof-owner")
    need(expected_tuple is not None and validate_guest_tuple(value["guest_tuple"])==expected_tuple,"terminal-proof-tuple")
    need(value["captured_ranges_contiguous"]is True and value["missing_bytes_inferred"]is False,"terminal-proof-coverage")
    for name in ("server","peer"):
        side=value[name]
        need(isinstance(side,dict) and set(side)=={"payload_bytes","fin_offset","sequence_end","fin_acked","max_ack","rsts"},"terminal-side-shape")
        need(all(type(side[k])is int and 0<=side[k]<0x80000000 for k in ("payload_bytes","sequence_end","max_ack","rsts")) and
             side["payload_bytes"]>0 and side["rsts"]<=32768 and type(side["fin_acked"])is bool,"terminal-side-scalars")
        fin=side["fin_offset"]
        need(fin is None or (type(fin)is int and fin==side["payload_bytes"]),"terminal-fin-offset")
        need(side["sequence_end"]==side["payload_bytes"]+(fin is not None) and
             (fin is not None or side["fin_acked"]is False),"terminal-sequence-end")
    need(value["server"]["max_ack"]<=value["peer"]["sequence_end"] and
         value["peer"]["max_ack"]<=value["server"]["sequence_end"],"terminal-ack-envelope")
    basis=value["terminal_basis"]
    if basis=="both-fins-and-acknowledgments":
        need(all(value[n]["fin_offset"]is not None and value[n]["fin_acked"]is True and value[n]["rsts"]==0 for n in ("server","peer")),"terminal-orderly-proof")
    elif basis=="captured-rst-with-sequence-and-ack-consistency":
        need(value["server"]["rsts"]+value["peer"]["rsts"]>0,"terminal-reset-missing")
    else: raise FixtureError("terminal-proof-basis")
    return copy.deepcopy(value)


class Observer:
    """Thread-safe PUSH interface; no unbounded external callback is invoked.

    Before run, arm_wire_guard() with the reviewed PCAP observer's binding.
    Root watches ready, maps the slow socket to its real guest fd/PCB, and bind()s
    before stimulus. Root calls submit() immediately on each real guest event.
    Required common keys: origin, run_id, source_commit, elf_sha256, guest_fd,
    pcb, inputs_sha256, evidence_sha256. Guest events additionally carry frame_id,
    the actual stored deadline, explicitly derived start and bounded debugger
    receipt. Actual-clock and source-bound select-zero timeout bases are distinct;
    the latter MUST use observed_us=None, actual remainder/timeval/ticks/select0
    and caller -3. Timeout must refer to the SAME first pressure frame.
    PCAP events carry unique_tcp_payload_bytes and final (coverage from connect).
    Host-only events, counters, elapsed time, EOF and Close are not accepted.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.binding = None
        self.guest_tuple = None
        self.guard = None
        self.ready = None
        self.connections_closed = threading.Event()
        self.stimulus_armed = threading.Event()
        self.phase = None
        self.pressure = self.timeout = self.wire = None
        self.invalid = []
        self.incomplete_reasons = []

    def incomplete(self, reason):
        need(isinstance(reason,str) and re.fullmatch(r"[a-z0-9-]{1,80}",reason),"incomplete-reason-token")
        with self.lock:
            if len(self.incomplete_reasons)<8:self.incomplete_reasons.append(reason)
            self.stop.set()

    def arm_stimulus(self):
        with self.lock:
            need(self.binding is not None and self.guard is not None and not self.stop.is_set(),"stimulus-arm-order")
            self.stimulus_armed.set()

    def arm_wire_guard(self, run_id, source_commit, elf_sha256, evidence_sha256, *, inputs_sha256):
        Binding(run_id, source_commit, elf_sha256, 0, "0x0", inputs_sha256)
        need(bool(re.fullmatch(r"[0-9a-f]{64}", evidence_sha256)), "wire-guard-evidence")
        with self.lock:
            need(self.guard is None and self.ready is None, "wire-guard-must-precede-connect")
            self.guard = dict(run_id=run_id, source_commit=source_commit, elf_sha256=elf_sha256,
                              inputs_sha256=inputs_sha256,
                              evidence_sha256=evidence_sha256, max_unique_server_tcp_payload=TCP_LIMIT,
                              coverage="all-owned-server-connections-from-connect")

    def bind(self, binding, *, guest_tuple=None):
        need(isinstance(binding, Binding), "binding-type")
        tuple_value=validate_guest_tuple(guest_tuple) if guest_tuple is not None else None
        with self.lock:
            need(self.binding is None and self.guard is not None, "binding-order")
            need(all(getattr(binding, k) == self.guard[k] for k in ("run_id", "source_commit", "elf_sha256", "inputs_sha256")), "binding-guard")
            self.binding = binding
            self.guest_tuple = tuple_value

    def submit(self, event):
        # Only retain selected, bounded evidence fields; never arbitrary log text.
        try:
            with self.lock:
                b = self.binding
                need(b is not None and isinstance(event, dict), "witness-unbound")
                need(all(event.get(k) == getattr(b, k) for k in dataclasses.asdict(b)), "witness-binding")
                need(bool(re.fullmatch(r"[0-9a-f]{64}", event.get("evidence_sha256", ""))), "witness-evidence")
                kind = event.get("kind")
                fields = tuple(dataclasses.asdict(b)) + ("kind", "origin", "evidence_sha256")
                if kind == "wire-accounting":
                    need(event.get("origin") == "root-pcap-unique-tcp" and event.get("coverage") == self.guard["coverage"], "wire-accounting-origin")
                    total = event.get("unique_tcp_payload_bytes")
                    need(type(total) is int and 0 <= total <= TCP_LIMIT, "wire-envelope-exceeded")
                    need(self.wire is None or total >= self.wire["unique_tcp_payload_bytes"], "wire-counter-regressed")
                    need(type(event.get("final")) is bool, "wire-final-type")
                    terminal=event.get("selected_slow_terminal")
                    need(event["final"] or terminal is None,"live-terminal-proof-forbidden")
                    if terminal is not None:
                        terminal=selected_terminal(terminal,b,self.guest_tuple)
                        need(terminal["server"]["payload_bytes"]<=total,"terminal-payload-envelope")
                    need(not event["final"] or self.connections_closed.is_set(), "wire-final-before-cleanup")
                    need(self.wire is None or not self.wire["final"], "wire-after-final")
                    fields += ("unique_tcp_payload_bytes", "final", "coverage")
                    self.wire = {k: event[k] for k in fields}
                    if terminal is not None:self.wire["selected_slow_terminal"]=terminal
                    return
                need(kind in ("guest-pressure", "guest-timeout") and event.get("origin") == "root-gdb-send-frame", "not-guest-send-witness")
                dbg=event.get("debugger")
                need(isinstance(dbg,dict),"debugger-bounds-missing")
                need(dbg.get("max_stops")==512 and dbg.get("max_single_stop_seconds")==2.0 and dbg.get("max_total_pause_seconds")==30.0 and dbg.get("budget_exceeded") is False,"debugger-declared-bounds")
                need(type(dbg.get("stops")) is int and 1<=dbg["stops"]<=512,"debugger-stop-count")
                actual=[dbg.get(k) for k in ("max_observed_stop_seconds","total_observed_pause_seconds")]
                need(all(type(v) in (int,float) and math.isfinite(v) and v>=0 for v in actual) and actual[0]<=2.0 and actual[0]<=actual[1]<=30.0,"debugger-observed-bounds")
                debugger={k:dbg[k] for k in ("max_stops","max_single_stop_seconds","max_total_pause_seconds","stops","max_observed_stop_seconds","total_observed_pause_seconds","budget_exceeded")}
                need(bool(re.fullmatch(r"[A-Za-z0-9_:.-]{1,80}", event.get("frame_id", ""))), "witness-frame")
                a, d, t = (event.get(k) for k in ("start_us", "deadline_us", "observed_us"))
                need(all(type(x) is int and x >= 0 for x in (a, d)) and d-a == 1000000, "witness-one-frame-deadline")
                need(event.get("start_basis")=="derived-from-stored-deadline" and event.get("entry_clock_observed") is False and event.get("source_constructor_budget_us")==1000000,"witness-derived-start-basis")
                fields += ("frame_id", "start_us", "deadline_us", "observed_us", "start_basis", "entry_clock_observed", "source_constructor_budget_us")
                extra = {"debugger":debugger}
                if kind == "guest-pressure":
                    need(event.get("errno") in ("EAGAIN", "EWOULDBLOCK") and type(t) is int and a<=t<d and event.get("clock_basis")=="actual-target-retry-clock" and event.get("would_block_write") is True, "not-guest-would-block")
                    queue=pressure_queue(event)
                    fields += ("errno","clock_basis","would_block_write","pressure_basis","guest_queue_sample_site")
                    extra["guest_queue"]=queue
                    if self.timeout is not None:
                        need(all(event[k]==self.timeout[k] for k in ("frame_id","start_us","deadline_us")),"pressure-other-frame")
                    if self.pressure is None:
                        self.pressure = dict({k:event[k] for k in fields},**extra)
                    else:
                        need(all(event[k]==self.pressure[k] for k in ("frame_id","start_us","deadline_us")),"pressure-other-frame")
                else:
                    need(event.get("result")=="HTTPD_SOCK_ERR_TIMEOUT", "not-guest-frame-timeout")
                    need(type(event.get("caller_result"))is int and event["caller_result"]==-3,"not-caller-timeout-result")
                    basis=event.get("timeout_basis")
                    if basis=="actual-target-clock-expired":
                        need(type(t) is int and t>=d,"not-actual-expired-clock")
                    elif basis=="select-zero-original-remainder":
                        before=event.get("preselect_us");remaining=event.get("remaining_us")
                        need(t is None and type(before) is int and a<=before<d and type(remaining) is int and remaining==d-before and event.get("timeval_us")==remaining,"not-original-select-remainder")
                        need(type(event.get("select_result")) is int and event["select_result"]==0 and type(event.get("caller_result")) is int and event["caller_result"]==-3,"not-exact-select-timeout-path")
                        tb,ta,delta,hz=(event.get(k) for k in ("tick_before","tick_after","tick_delta","tick_hz"))
                        need(all(type(x) is int and 0<=x<=4294967295 for x in (tb,ta,delta)) and hz==1000 and delta==((ta-tb)&0xffffffff) and delta<2147483648,"select-tick-source")
                        # Pinned Hz1000 clock has one-tick quantization. Allow
                        # scheduling lateness, never invent a post-select timer.
                        need(delta*1000+1000>=remaining,"select-tick-interval-too-short")
                        extra.update(post_select_timer_observed=False,tick_quantization_us=1000,
                                     tick_lateness_estimate_us=max(0,delta*1000-remaining))
                        fields += ("preselect_us","remaining_us","timeval_us","select_result","caller_result","tick_before","tick_after","tick_delta","tick_hz")
                    else:
                        raise FixtureError("timeout-basis-missing")
                    if self.pressure is not None:
                        need(all(event[k] == self.pressure[k] for k in ("frame_id", "start_us", "deadline_us")), "timeout-other-frame")
                    fields += ("result","timeout_basis","caller_result")
                    self.timeout = dict({k:event[k] for k in fields},**extra)
                # Push cancellation immediately. One already in-flight tiny
                # write (<=14 bytes, <=100 ms syscall timeout) cannot be recalled.
                self.stop.set()
        except (FixtureError, TypeError) as exc:
            with self.lock:
                if len(self.invalid) < 8:
                    self.invalid.append(str(exc) if isinstance(exc, FixtureError) else "witness-type")
            self.stop.set()  # Invalid observer input aborts safely, never proves PASS.
            raise

    def snapshot(self):
        with self.lock:
            return dict(binding=dataclasses.asdict(self.binding) if self.binding else None,
                        guest_tuple=copy.deepcopy(self.guest_tuple),
                        wire_guard=dict(self.guard) if self.guard else None,
                        pressure=copy.deepcopy(self.pressure) if self.pressure else None,
                        timeout=copy.deepcopy(self.timeout) if self.timeout else None,
                        wire=copy.deepcopy(self.wire) if self.wire else None, invalid=list(self.invalid),
                        incomplete_reasons=list(self.incomplete_reasons),
                        connections_closed=self.connections_closed.is_set())


class SocketFactory:
    """Only dial injection into exact frozen Endpoint.dial bytecode."""
    def __init__(self, factory=None):
        self.factory = socket.socket if factory is None else factory
        self.actual_buffers = []

    def __getattr__(self, key):
        return getattr(socket, key)

    def create_connection(self, address, timeout):
        host, port = address
        raw = self.factory(socket.AF_INET6 if ":" in host else socket.AF_INET, socket.SOCK_STREAM)
        try:
            raw.settimeout(timeout)
            raw.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RCVBUF)
            self.actual_buffers.append(raw.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
            raw.connect((host, port))
            return raw
        except BaseException:
            raw.close()
            raise


class Endpoint(client.Endpoint):
    def __post_init__(self):
        super().__post_init__()
        self.socket_factory = SocketFactory()
        self.gates = []
        if self.secure:
            self.context.set_ciphers(TLS_CIPHER)

    def dial(self, budget, *, context=None, name=None):
        # Execute the ORIGINAL strict verifier, replacing only its dial factory.
        # No global/module monkeypatch, copied TLS verifier, or disabled checks.
        original = client.Endpoint.dial
        namespace = dict(original.__globals__, socket=self.socket_factory)
        dial = types.FunctionType(original.__code__, namespace, original.__name__, original.__defaults__, original.__closure__)
        dial.__kwdefaults__ = original.__kwdefaults__
        sock, metadata = dial(self, budget, context=context, name=name)
        if self.secure:
            need(metadata["cipher"] == TLS_CIPHER, "unexpected-tls-aes-gcm-profile")
        return sock, metadata

    def abort_owned(self):
        for gate in self.gates:
            gate.local_closed = True
        super().abort_owned()


class SocketGate:
    def __init__(self, sock):
        self.sock = sock
        self.withheld = False
        self.read_calls = self.read_bytes = 0
        self.local_closed = self.remote_eof = False
        self.remote_reset = False
        self.io_state_lock = threading.Lock()
        self.io_owner = None
        self.io_depth = self.io_overlaps = 0

    @contextlib.contextmanager
    def operation(self):
        # Diagnostic ownership check, not a lock held across blocking I/O.
        # A second thread is rejected immediately instead of serializing behind
        # a read. Same-thread recursive Pong sends remain valid.
        ident=threading.get_ident()
        with self.io_state_lock:
            if self.io_owner is not None and self.io_owner!=ident:
                self.io_overlaps+=1
                raise FixtureError("cross-thread-same-socket-io")
            self.io_owner=ident;self.io_depth+=1
        try:
            yield
        finally:
            with self.io_state_lock:
                self.io_depth-=1
                if not self.io_depth:self.io_owner=None

    def __getattr__(self, key):
        return getattr(self.sock, key)

    def recv(self, maximum):
        need(not self.withheld, "hidden-read-during-withhold")
        need(self.read_bytes < APP_BOUND + 2*client.MAX_HTTP, "decrypted-read-bound")
        self.read_calls += 1
        try:
            body = self.sock.recv(min(maximum, APP_BOUND + 2*client.MAX_HTTP-self.read_bytes))
        except ConnectionResetError as error:
            if not self.local_closed:
                self.remote_reset=True
                raise ReceiveReset(self) from error
            raise
        except ssl.SSLEOFError:
            self.remote_eof = not self.local_closed
            raise
        self.read_bytes += len(body)
        if not body and not self.local_closed:
            self.remote_eof = True
        return body

    def close(self):
        self.local_closed = True
        self.sock.close()


class Meter:
    def __init__(self):
        self.lock = threading.Lock()
        self.client_ws_bytes = self.server_ws_bytes = 0

    def add(self, direction, size):
        with self.lock:
            key = "client_ws_bytes" if direction=="client" else "server_ws_bytes"
            value = getattr(self,key)+size
            need(value < 16384 if direction=="client" else value <= APP_BOUND, "aggregate-wire-bound")
            setattr(self,key,value)


class Session(client.Session):
    def __init__(self, wire, metadata=None):
        super().__init__(wire, metadata)
        self.send_lock = threading.Lock()
        self.server_ws_bytes = 0
        self.transport_eof = False
        self.transport_reset = False
        self.termination_kind = None
        self.normal_close_sent = False
        self.clean_tls_eof = None
        self.meter = Meter()

    def send_raw(self, body, budget):
        with self.wire.sock.operation(), self.send_lock:
            self.meter.add("client",len(body))  # Reserve whole attempted write.
            super().send_raw(body, budget)

    def record_frame(self, direction, opcode, final, payload):
        super().record_frame(direction, opcode, final, payload)
        if direction=="client" and opcode==8:
            self.normal_close_sent=bool(final and payload==client.close_payload())
        if direction == "server":
            # Actual production emits one FIN text frame; unexpected fragment
            # shape invalidates this fixture's byte proof, not RFC support.
            need(opcode >= 8 or (opcode == 1 and final), "fixture-server-frame-shape")
            need(opcode >= 8 or len(payload) <= 5119, "fixture-text-capacity")
            self.server_ws_bytes += len(payload) + (2 if len(payload)<126 else 4 if len(payload)<=65535 else 10)
            self.meter.add("server",len(payload) + (2 if len(payload)<126 else 4 if len(payload)<=65535 else 10))

    def event(self, budget):
        need(not self.wire.sock.withheld, "hidden-session-read-during-withhold")
        try:
            with self.wire.sock.operation():
                return super().event(budget)
        except client.PeerEOF as ended:
            if self.wire.sock.remote_eof:
                self.transport_eof, self.clean_tls_eof = True, ended.clean_tls
                self.termination_kind="tls-ragged-eof" if self.wire.secure and ended.clean_tls is False else "orderly-eof"
            raise
        except ReceiveReset as ended:
            if ended.gate is self.wire.sock and self.wire.sock.remote_reset and not self.wire.sock.local_closed:
                self.transport_reset=True
                self.termination_kind="remote-reset"
            raise


def open_peer(endpoint, budget):
    base, status, _ = client.upgrade(endpoint, budget)
    need(status == 101, "upgrade-not-101")
    gate = SocketGate(base.wire.sock)
    endpoint.gates.append(gate)
    base.wire.sock = gate
    session = Session(base.wire, base.tls_metadata)
    session.handshake_metadata = base.handshake_metadata
    return session


def validate_status(obj):
    status, payload = obj.get("status"), obj.get("payload")
    need(isinstance(status, dict) and isinstance(payload, list), "calibration-status-shape")
    strings = ("station", "title", "format")
    bools = ("connecting", "audio", "smartstart", "normalization", "network_online", "ap_enabled", "rssi_valid")
    ints = ("bitrate", "generation", "volume", "balance", "current", "count", "normgain", "normtarget", "normtime", "rssi")
    need(set(status) == set(strings+bools+ints), "calibration-status-keys")
    need(all(type(status[k]) is str for k in strings) and all(type(status[k]) is bool for k in bools) and all(type(status[k]) is int for k in ints), "calibration-status-types")
    for key in ("current","count","normtime"):
        need(0 <= status[key] <= 65535, "calibration-status-u16")
    for key in ("generation","bitrate"):
        need(0 <= status[key] <= 4294967295, "calibration-status-u32")
    ids = ("nameset", "meta", "volume", "balance", "rssi", "heap", "bitrate", "fmt", "playerwrap")
    need(all(isinstance(x, dict) and set(x)=={"id","value"} for x in payload), "calibration-payload-shape")
    need(len(payload)==len(ids) and {x["id"] for x in payload}==set(ids), "calibration-payload-ids")
    values = {x["id"]:x["value"] for x in payload}
    need(all(type(values[k]) is str for k in ("nameset","meta","fmt","playerwrap")) and all(type(values[k]) is int for k in ("volume","balance","rssi","heap","bitrate")), "calibration-payload-types")
    need(values["meta"]==status["title"] and values["fmt"]==status["format"] and values["playerwrap"]==("playing" if status["audio"] else "stopped") and all(values[k]==status[k] for k in ("volume","balance","rssi","bitrate")), "calibration-payload-consistency")


def validate_event(kind, obj):
    if kind=="status":validate_status(obj)
    elif kind=="current":need(set(obj)=={"current"} and type(obj["current"]) is int and 0<=obj["current"]<=65535,"calibration-current-range")
    elif kind=="playermode":need(obj=={"playermode":"modeweb"},"calibration-playermode-value")
    elif kind=="playlist-event":need(obj=={"file":"/data/playlist.csv"},"calibration-playlist")
    else:need(kind in ("ping","pong","close"),"unexpected-getindex-response")


class Budget:
    def __init__(self, end, stop=None):
        self.end, self.stop = end, stop

    def remaining(self):
        if self.stop is not None and self.stop.is_set():
            raise StopStimulus()
        left = self.end-time.monotonic()
        need(left > 0, "activity-deadline")
        return min(.1, left)  # Bound cancellation latency of every socket syscall.


class Commands:
    def __init__(self):
        self.lock = threading.Lock()
        self.attempted = self.completed = 0
        self.partial = 0

    def one(self, session, budget):
        with self.lock:
            need(self.attempted < COMMAND_CAP, "command-cap")
            self.attempted += 1  # Includes partial/failed sends, never undercounts.
        before=session.wire.sent_bytes
        try:
            session.send(1, COMMAND, budget=budget)
        finally:
            actual=session.wire.sent_bytes-before
            if 0<actual<14:
                with self.lock:self.partial+=1
        with self.lock:
            self.completed += 1


def barrier_group(session, budget, token, commands):
    """Getindex then Ping gives a serialized delimiter, including trailing playlist.

    No sleep/quiet-time guess. Existing initialization may precede the group;
    all complete messages through the matching Pong are consumed and checked.
    """
    need(len(token)==8, "barrier-token-width")
    before = session.server_ws_bytes
    commands.one(session, budget)
    session.send(9, token, budget=budget)
    groups, stage, current, status_item = 0, 0, None, None
    while True:
        try:
            kind, obj = session.event(budget)
        except (socket.timeout, TimeoutError):
            budget.remaining()
            continue
        if kind == "pong" and obj == token:
            need(groups >= 1 and stage != 2, "incomplete-getindex-group")
            return dict(complete_groups=groups, server_ws_bytes=session.server_ws_bytes-before)
        need(kind != "close", "closed-during-getindex-calibration")
        validate_event(kind,obj)
        if kind == "status":
            stage, status_item = 1, obj["status"]["current"]
        elif kind == "current":
            need(set(obj)=={"current"} and type(obj["current"]) is int and stage==1 and obj["current"]==status_item, "calibration-current")
            stage, current = 2, obj["current"]
        elif kind == "playermode":
            need(obj=={"playermode":"modeweb"} and stage==2 and current is not None, "calibration-playermode")
            groups, stage = groups+1, 0


def timeout_token(obs):
    need(not obs["invalid"] and not obs["incomplete_reasons"],"abort-observer-incomplete")
    binding,pressure,timeout=(obs.get(k)for k in ("binding","pressure","timeout"))
    need(binding and pressure and timeout,"abort-witness-missing")
    need(all(pressure[k]==timeout[k]for k in ("frame_id","start_us","deadline_us")),"abort-other-frame")
    need(all(pressure[k]==timeout[k]==binding[k]for k in binding),"abort-other-binding")
    need(type(timeout.get("caller_result"))is int and timeout["caller_result"]==-3,"abort-caller-timeout-missing")
    return dict(binding,guest_tuple=copy.deepcopy(obs.get("guest_tuple")),
                **{k:timeout[k]for k in ("frame_id","start_us","deadline_us","timeout_basis","caller_result")})


def termination_ok(report, obs, terminal):
    if not terminal:return False
    mode=report["mode"];kind=report.get("slow_termination_kind")
    secure=report.get("slow_secure")
    orderly=(report.get("slow_transport_eof")is True and report.get("slow_remote_reset")is False and
             kind=="orderly-eof" and type(secure)is bool and
             (report.get("slow_clean_tls_eof")is True if secure else report.get("slow_clean_tls_eof")is None))
    if mode in ("drained","read-resume"):
        return bool(orderly and report.get("slow_normal_close_sent")is True and
                    report.get("slow_normal_close_received")is True and
                    terminal["terminal_basis"]=="both-fins-and-acknowledgments" and
                    all(terminal[n]["fin_offset"]is not None and terminal[n]["fin_acked"]is True and
                        terminal[n]["rsts"]==0 for n in ("server","peer")))
    try:token=timeout_token(obs)
    except FixtureError:return False
    if not (report.get("slow_reader_timeout_token")==token and report.get("slow_termination_token")==token and
            report.get("sender_joined_before_read")is True and report.get("slow_closed_before_reader")is False and
            report.get("local_closed_at_termination")is False):return False
    if kind=="remote-reset":
        return bool(report.get("slow_remote_reset")is True and report.get("slow_transport_eof")is False and
                    terminal["terminal_basis"]=="captured-rst-with-sequence-and-ack-consistency" and
                    terminal["server"]["rsts"]>0)
    ragged=(kind=="tls-ragged-eof" and secure is True and report.get("slow_clean_tls_eof")is False and
            report.get("slow_transport_eof")is True and report.get("slow_remote_reset")is False)
    return bool((orderly or ragged) and (terminal["server"]["fin_offset"]is not None or terminal["server"]["rsts"]>0))


def finish_report(report, observer):
    """Root calls again after final PCAP accounting if run returned INCOMPLETE."""
    obs = observer.snapshot()
    same_frame = bool(obs["pressure"] and obs["timeout"] and all(obs["pressure"][k]==obs["timeout"][k] for k in ("frame_id","start_us","deadline_us")))
    terminal=obs["wire"].get("selected_slow_terminal")if obs["wire"]else None
    wire_ok = bool(obs["wire_guard"] and obs["wire"] and obs["wire"]["final"] and terminal and obs["wire"]["unique_tcp_payload_bytes"]<=TCP_LIMIT)
    bounds_ok = (0<=report.get("commands_attempted",-1)<=COMMAND_CAP and
                 0<=report.get("attempted_client_ws_bytes",-1)<16384 and
                 0<=report.get("decoded_server_ws_bytes",-1)<=APP_BOUND and
                 report.get("partial_command_frames",-1)==0 and
                 0<=report.get("elapsed_seconds",-1)<=CASE_SECONDS)
    withheld_ok = report["mode"]=="drained" or (report.get("withheld_read_calls")==0 and report.get("sender_joined_before_read") is True and report.get("slow_closed_before_reader") is False)
    ownership_ok = report.get("slow_io_overlaps",-1)==0 and report.get("healthy_io_overlaps",-1)==0
    good = not report["errors"] and not obs["invalid"] and not obs["incomplete_reasons"] and report["threads_joined"] and report["healthy_progress_after_stimulus"] and wire_ok and bounds_ok and withheld_ok and ownership_ok and report.get("watchdog_fired")is False and report.get("observation_exhausted")is False
    mode = report["mode"]
    ended=termination_ok(report,obs,terminal)
    objective = good and mode=="withheld" and same_frame and ended
    control = good and mode in ("drained","read-resume") and report["slow_resume_pong"] and ended and not obs["timeout"] and (mode=="drained" or bool(obs["pressure"]))
    failed=bool(report["errors"] or obs["invalid"] or not report["threads_joined"])
    report.update(state="FAIL" if failed else "PASS" if objective or control else "INCOMPLETE", pressure_objective="PASS" if objective else "INCOMPLETE", control_state="PASS" if control else "INCOMPLETE", observer=obs)
    return report


def run(url, observer, *, mode="withheld", ca=None, certificate_sha256=None, peer_factory=None):
    """Root-only future entry. peer_factory is solely for pure scripted tests.

    Arm PCAP guard BEFORE entry. Root maps/binds fd/PCB after observer.ready,
    arms its GDB collector, then calls observer.arm_stimulus(). Both setup peers
    remain drained until that handshake completes. The collector's stop event
    MUST differ from observer.stop, so pressure can stop commands while the
    collector continues to the actual guest timeout. Collector exhaustion must
    call observer.incomplete(reason_token); it must not fabricate a timeout.
    No receiver touches slow Session/FrameReader while SocketGate.withheld.
    All fixture-owned threads are stopped, socket-unblocked and joined.
    """
    need(mode in ("withheld","drained","read-resume"), "mode")
    need(observer.snapshot()["wire_guard"] is not None, "pcap-guard-not-armed")
    need(not observer.stop.is_set(),"observer-already-stopped")
    start = time.monotonic(); end = start+CASE_SECONDS-CLEANUP_SECONDS
    stopped = threading.Event(); resumed_pong = threading.Event()
    setup_stop = threading.Event()
    endpoints = []; sessions = []; threads = []; errors = []; commands = Commands()
    report = dict(mode=mode, declaration=declaration(), errors=errors, threads_joined=False,
                  healthy_progress_after_stimulus=False, slow_transport_eof=False,
                  slow_resume_pong=False, slow_close_seen=False, slow_local_close=False,
                  watchdog_fired=False, observation_exhausted=False)
    report.update(sender_joined_before_read=False,slow_closed_before_reader=None,
                  slow_remote_reset=False,slow_termination_kind=None,slow_secure=None,
                  slow_normal_close_sent=False,slow_normal_close_received=False,
                  slow_reader_timeout_token=None,slow_termination_token=None,local_closed_at_termination=None)
    meter = Meter()
    withheld_delta = None

    def abort():
        stopped.set(); observer.stop.set();setup_stop.set()
        for ep in endpoints:
            ep.abort_owned()

    def watchdog():
        report["watchdog_fired"]=True
        abort()

    timer = threading.Timer(CASE_SECONDS-CLEANUP_SECONDS, watchdog)
    timer.name = "pressure-watchdog";timer.start()

    def worker(name, work):
        def wrapped():
            try:
                work()
            except (StopStimulus, client.PeerEOF):
                pass
            except BaseException as exc:
                if isinstance(exc,FixtureError) and str(exc)=="activity-deadline":
                    report["observation_exhausted"]=True
                elif not stopped.is_set():
                    errors.append(client.error_category(exc) if not isinstance(exc,FixtureError) else str(exc))
                stopped.set()
        t = threading.Thread(target=wrapped,name=name);threads.append(t);t.start()

    try:
        setup_threads=[]
        report["initialization"]=[];report["calibration"]=[]
        for role in ("slow","healthy"):
            ep = Endpoint(url, ca, certificate_sha256);endpoints.append(ep)
            session = open_peer(ep, client.Budget(max(.001,end-time.monotonic()))) if peer_factory is None else peer_factory(role,ep)
            session.meter = meter
            sessions.append(session)
            report["initialization"].append(barrier_group(session,Budget(end),b"initSlo1" if role=="slow" else b"initHea1",commands))
            report["calibration"].append(barrier_group(session,Budget(end),b"calSlow1" if role=="slow" else b"calHeal1",commands))
            need(report["calibration"][-1]["complete_groups"]==1,"calibration-command-group-count")
            def setup_reader(s=session):
                while not stopped.is_set() and not setup_stop.is_set():
                    try:kind,obj=s.event(Budget(end))
                    except (socket.timeout,TimeoutError):continue
                    need(kind!="close","closed-during-initialization")
                    validate_event(kind,obj)
            worker("pressure-setup-"+role,setup_reader)
            setup_threads.append(threads[-1])
        slow, healthy = sessions
        report["slow_secure"]=slow.wire.secure
        report["receive_buffers"]=[dict(requested=RCVBUF,actual=list(ep.socket_factory.actual_buffers)) for ep in endpoints]
        report["tls"]=[s.tls_metadata for s in sessions]
        observer.ready = {"slow":slow.wire.sock.getsockname(),"healthy":healthy.wire.sock.getsockname(),"declaration":declaration()}
        while observer.snapshot()["binding"] is None:
            need(not observer.stop.is_set() and not stopped.is_set(),"observer-stopped-before-bind")
            Budget(end).remaining();stopped.wait(.01)
        while not observer.stimulus_armed.wait(.01):
            need(not observer.stop.is_set() and not stopped.is_set(),"observer-stopped-before-arm")
            Budget(end).remaining()
        setup_stop.set()
        for t in setup_threads:t.join(max(0,end-time.monotonic()))
        need(all(not t.is_alive() for t in setup_threads),"setup-reader-not-joined")
        need(not stopped.is_set(),"setup-worker-aborted")
        gate = slow.wire.sock
        gate.withheld = mode != "drained"
        withheld_reads = gate.read_calls
        report["withheld_prefetched_ws_bytes"]=len(slow.wire.buffer)
        observer.phase=dict(mode=mode,slow_read_calls=withheld_reads,
                            slow_prefetched_ws_bytes=len(slow.wire.buffer))
        def reader():
            if stopped.is_set():return
            gate.withheld = False
            if mode in ("drained","read-resume"):
                slow.send(9,b"resume01",budget=Budget(end))
            while not stopped.is_set():
                try:kind,obj=slow.event(Budget(end))
                except (socket.timeout,TimeoutError):continue
                except ReceiveReset:
                    need(mode=="withheld","reset-is-not-control-termination")
                    record_termination("remote-reset")
                    return  # Candidate only. Final server-origin PCAP RST is required.
                except client.PeerEOF:
                    if mode=="withheld":record_termination(slow.termination_kind)
                    raise
                if kind=="close" and not slow.close_sent:slow.send(8,obj,budget=Budget(end))
                elif kind=="pong" and obj==b"resume01":
                    resumed_pong.set()
                    if not slow.close_sent:slow.send(8,client.close_payload(),budget=Budget(end))
                else:validate_event(kind,obj)

        def record_termination(kind):
            token=timeout_token(observer.snapshot())
            need(report["slow_reader_timeout_token"]==token and report["sender_joined_before_read"]is True and
                 report["slow_closed_before_reader"]is False and not gate.local_closed and
                 not stopped.is_set() and not errors and commands.partial==0,"unqualified-remote-termination")
            need(kind in ("remote-reset","orderly-eof","tls-ragged-eof"),"remote-termination-kind")
            report.update(slow_termination_token=token,local_closed_at_termination=False)

        def sender():
            for _ in range(SLOW_COMMANDS):
                if stopped.is_set() or observer.stop.is_set():return
                # An in-flight 14-byte frame may complete after cancellation;
                # do not create an intentionally truncated command. All its
                # partial sends share one <=100 ms absolute deadline.
                commands.one(slow,Budget(min(end,time.monotonic()+.1)))
                if observer.stop.wait(.01):return

        def drained_owner():
            for _ in range(SLOW_COMMANDS):
                if stopped.is_set():return
                if observer.stop.is_set():break
                try:barrier_group(slow,Budget(end,observer.stop),b"drained1",commands)
                except StopStimulus:break
                if observer.stop.wait(.01):break
            reader()  # Same thread owns every slow send/read, including Close.

        def healthy_work():
            for n in range(8):
                if stopped.is_set():return
                barrier_group(healthy,Budget(end),b"healthy1",commands)
                if observer.stop.is_set():report["healthy_progress_after_stimulus"]=True
                if stopped.wait(.15):return

        sender_thread=None;reader_started=False
        if mode=="drained":
            worker("pressure-drained-owner",drained_owner)
            reader_started=True
        else:
            worker("pressure-sender",sender);sender_thread=threads[-1]
        worker("pressure-healthy",healthy_work)
        while not stopped.is_set():
            Budget(end).remaining();obs=observer.snapshot()
            need(not obs["invalid"],"invalid-observer-input")
            if obs["incomplete_reasons"]:
                report["observation_exhausted"]=True
                raise FixtureError("observer-incomplete")
            if mode!="drained" and not reader_started:
                need(gate.read_calls==withheld_reads,"hidden-read-during-withhold")
                if observer.stop.is_set():
                    sender_thread.join(min(.5,max(0,end-time.monotonic())))
                    need(not sender_thread.is_alive(),"sender-not-terminal-before-read")
                    report.update(sender_joined_before_read=True,
                                  slow_closed_before_reader=gate.local_closed,
                                  slow_eof_observed_at_sender_join=slow.transport_eof)
                if (mode=="read-resume" and obs["pressure"]) or (mode=="withheld" and obs["timeout"]):
                    need(report["sender_joined_before_read"] and not gate.local_closed,"unsafe-read-resume-transfer")
                    if mode=="withheld":
                        need(not errors and not stopped.is_set() and commands.partial==0,"sender-failed-before-read")
                        report["slow_reader_timeout_token"]=timeout_token(obs)
                    withheld_delta=gate.read_calls-withheld_reads
                    worker("pressure-reader-owner",reader)
                    reader_started=True
            if slow.transport_eof or slow.transport_reset:break
            stopped.wait(.01)
        need(not stopped.is_set(),"worker-aborted")
        # No concurrent healthy reader while the final complete-group check runs.
        healthy_thread=next(t for t in threads if t.name=="pressure-healthy")
        healthy_thread.join(max(0,end-time.monotonic()))
        need(not healthy_thread.is_alive(),"healthy-worker-not-joined")
        barrier_group(healthy,Budget(end),b"postHeal",commands)
        report["healthy_progress_after_stimulus"]=True
        healthy.normal_close(client.Budget(max(.001,end-time.monotonic())))
        report.update(slow_transport_eof=slow.transport_eof,slow_close_seen=slow.close_seen,
                      slow_resume_pong=resumed_pong.is_set(),slow_clean_tls_eof=slow.clean_tls_eof,
                      slow_remote_reset=slow.transport_reset,slow_termination_kind=slow.termination_kind,
                      slow_normal_close_sent=slow.normal_close_sent,
                      slow_normal_close_received=bool(slow.close_seen and slow.close_received==client.close_payload()),
                      withheld_read_calls=withheld_delta,
                      slow_received_ws_bytes=slow.server_ws_bytes,healthy_received_ws_bytes=healthy.server_ws_bytes)
    except BaseException as exc:
        if (isinstance(exc,FixtureError) and str(exc)=="activity-deadline") or report["watchdog_fired"] or report["observation_exhausted"] or observer.snapshot()["incomplete_reasons"]:
            report["observation_exhausted"]=True
        else:
            errors.append(client.error_category(exc) if not isinstance(exc,FixtureError) else str(exc))
    finally:
        # Snapshot remote EOF before LOCAL cleanup; never relabel it afterwards.
        if sessions:
            report["slow_transport_eof"]=sessions[0].transport_eof
            report["slow_close_seen"]=sessions[0].close_seen
            report["slow_remote_reset"]=sessions[0].transport_reset
            report["slow_termination_kind"]=sessions[0].termination_kind
            report["slow_clean_tls_eof"]=sessions[0].clean_tls_eof
            report["slow_normal_close_sent"]=sessions[0].normal_close_sent
            report["slow_normal_close_received"]=bool(sessions[0].close_seen and sessions[0].close_received==client.close_payload())
        abort();timer.cancel()
        for t in threads+[timer]:t.join(max(0,start+CASE_SECONDS-time.monotonic()))
        report["threads_joined"]=all(not t.is_alive() for t in threads+[timer])
        need(report["threads_joined"],"owned-thread-join-failed")
        observer.connections_closed.set()
        report.update(commands_attempted=commands.attempted,commands_completed=commands.completed,
                      partial_command_frames=commands.partial,
                      max_command_input_bytes=commands.attempted*14,elapsed_seconds=time.monotonic()-start,
                      attempted_client_ws_bytes=meter.client_ws_bytes,decoded_server_ws_bytes=meter.server_ws_bytes,
                      slow_local_close=bool(sessions and sessions[0].wire.sock.local_closed))
        report["slow_io_overlaps"]=sessions[0].wire.sock.io_overlaps if sessions else 0
        report["healthy_io_overlaps"]=sessions[1].wire.sock.io_overlaps if len(sessions)>1 else 0
    return finish_report(report,observer)


if __name__ == "__main__":
    print(json.dumps(declaration(),indent=2))
