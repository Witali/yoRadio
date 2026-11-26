"""Scripted orchestration only: fake guest/GDB/PCAP, no sockets/processes/Git."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
from unittest import mock

BASE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("scripted_pressure_root_v5", BASE / "run-pressure-v5.py")
r = importlib.util.module_from_spec(spec); sys.modules[spec.name] = r; spec.loader.exec_module(r)
p = r.import_pinned("pressure-peer-v2.py")
H = "a" * 64
SOURCE = "95672e8f673ec977b6f61b78eeba6958d0d992ac"
ELF = "3811af87f91fb563ead8e61ae5c188bc74f4495b07bb9e230834e4cef50f85bb"


def event(observer, kind, bad_clock=False):
    value = dict(vars(observer.binding), origin="root-gdb-send-frame", kind=kind,
                 evidence_sha256=H, frame_id="actual-scripted-frame", start_us=200,
                 deadline_us=1000200, observed_us=300, start_basis="derived-from-stored-deadline",
                 entry_clock_observed=False, source_constructor_budget_us=1000000,
                 debugger=dict(max_stops=512, max_single_stop_seconds=2.0, max_total_pause_seconds=30.0,
                               stops=2, max_observed_stop_seconds=.01, total_observed_pause_seconds=.02,
                               budget_exceeded=False))
    if kind == "guest-pressure":
        value.update(errno="EAGAIN", clock_basis="actual-target-retry-clock", would_block_write=True,
                     pressure_basis="zero-peer-window",guest_queue_sample_site="actual-would-block-branch",
                     guest_queue=dict(snd_wnd=0, snd_buf=0, snd_queuelen=4, unsent="0x1234", unacked="0x0"))
    else:
        value.update(observed_us=1000200, result="HTTPD_SOCK_ERR_TIMEOUT", timeout_basis="actual-target-clock-expired",caller_result=-3)
    if bad_clock:
        value["entry_clock_observed"] = True
    return value


def good_peer_report(mode, *, transport="ws", fault=None, observer=None):
    token=p.timeout_token(observer.snapshot())if observer is not None and observer.timeout else None
    return dict(mode=mode, errors=[], threads_joined=True, healthy_progress_after_stimulus=True,
                slow_transport_eof=True, slow_resume_pong=mode != "withheld", commands_attempted=3,
                attempted_client_ws_bytes=42, decoded_server_ws_bytes=1000, partial_command_frames=0,
                elapsed_seconds=.01, withheld_read_calls=0, sender_joined_before_read=True,
                slow_closed_before_reader=False, slow_io_overlaps=0, healthy_io_overlaps=0,
                slow_remote_reset=False,slow_termination_kind="orderly-eof",slow_secure=transport=="wss",
                slow_clean_tls_eof=True if transport=="wss"else None,slow_close_seen=mode!="withheld",
                slow_normal_close_sent=mode!="withheld" and fault!="normal-close-not-sent",
                slow_normal_close_received=mode!="withheld" and fault!="normal-close-wrong-payload",
                slow_reader_timeout_token=token,slow_termination_token=token,local_closed_at_termination=False,
                watchdog_fired=fault=="watchdog",observation_exhausted=fault=="observation-exhausted")


def terminal(role, *, reset=False, peer_only=False):
    """Valid nine-key PCAPv2 receipt; scalar/header metadata only."""
    result=deepcopy(role)
    n=700 if role["role"]=="slow" else 300
    def side(payload,other):
        return dict(payload_bytes=payload,fin_offset=None if reset else payload,
                    sequence_end=payload+(not reset),fin_acked=not reset,
                    max_ack=other+(not reset),rsts=0)
    result.update(terminal_basis="captured-rst-with-sequence-and-ack-consistency" if reset else "both-fins-and-acknowledgments",
                  server=side(n,42),peer=side(42,n),captured_ranges_contiguous=True,missing_bytes_inferred=False)
    if reset:result["peer"if peer_only else"server"]["rsts"]=1
    return result


class World:
    def __init__(self, output, fault=None, transport="ws"):
        self.output, self.fault, self.events, self.observer = output, fault, [], None
        self.live, self.collecting, self.closed = False, False, False
        self.guard_roles = None
        self.options = types.SimpleNamespace(output=output, transport=transport, ca=None,
            qualification=output.parent / "qualification.json")
        service = 443 if transport == "wss" else 80
        self.rows = [dict(guest_fd=54+i, pcb=hex(0x3ffb1234+i), closing=False,
                          guest_tuple=dict(local_ip="10.0.2.15", remote_ip="10.0.2.2",
                                           local_port=service, remote_port=43001+i)) for i in range(2)]
        if fault == "role-map": self.rows[1]["guest_tuple"]["remote_port"] = 49999
        self.initial = dict(boot_id="scripted-boot", uptime_ms=100, allocation_failures=0,
                            decoder_sequence=0, stream_sequence=0, output_failures=0,
                            write_errors=0, write_timeouts=0, short_writes=0)
        world = self

        class Guest:
            def __init__(self, options, prepared):
                self.private = output.parent / "fake-private"
                self.endpoint = types.SimpleNamespace(url=transport+"://localhost:9000/ws")
                self.binding = {}; self.gdb_port = 3333
                self.client = dict(health_summary=lambda x: x, health_verdict=p.client.health_verdict)
                self.report = dict(initial_health=deepcopy(world.initial))
                self.health = self
            def __enter__(self):
                output.mkdir(); world.live=True; world.events.append("guest-enter"); return self
            def check(self):
                if not world.live: raise r.RunFailure("guest-not-live")
                return "scripted-safe-uart"
            def read(self, path="/api/native/health"):
                assert world.observer.connections_closed.is_set() and world.closed
                assert world.live
                world.events.append("health")
                if path.endswith("status"): return dict(audio=False)
                value=deepcopy(world.initial); value["uptime_ms"]+=10
                if fault == "allocation": value["allocation_failures"]=1
                if fault == "boot": value["boot_id"]="different-boot"
                if fault == "missing-boot": value["boot_id"]=None
                return value
            def close(self): pass
            def save(self): pass
            def __exit__(self, *args):
                assert not world.collecting
                world.live=False; world.events.append("guest-exit")
                for key in ("owned_guest_stopped","all_input_pins_still_match","host_and_launcher_pins_still_match",
                            "checkout_commit_still_matches","flash_unchanged","fatal_markers_absent",
                            "capture_write_errors_absent","capture_stopped"):
                    self.report[key]=True
                if fault == "capture-stopped": self.report.pop("capture_stopped")
                if fault == "dump-write": self.report["capture_write_errors_absent"]=False
                return False

        class Collector:
            def __init__(self, observer, run_id, inputs_sha256, log_dir, **kwargs):
                world.observer=observer;self.observer=observer;self.mode=kwargs["mode"]
                self.state="INCOMPLETE";self.owned=[];self.attached=False;self.closed=False
                self.io=types.SimpleNamespace(child=types.SimpleNamespace(poll=lambda: 0),
                                              reader=types.SimpleNamespace(is_alive=lambda: False))
            def start(self, endpoint):
                assert endpoint=="127.0.0.1:3333" and world.observer.ready
                self.attached=True;world.events.append("gdb-start");return deepcopy(world.rows[::-1])
            def bind_slow(self, fd, pcb, guest_tuple):
                assert fd==54 and pcb==world.rows[0]["pcb"] and guest_tuple==world.rows[0]["guest_tuple"]
                world.events.append("gdb-bind")
            def arm(self):
                assert world.guard_roles is not None
                self.owned=["1","2"];world.events.append("gdb-arm")
            def collect(self, stop_event, *, seconds):
                assert stop_event is not self.observer.stop and 0 < seconds <= 1
                world.collecting=True;world.events.append("collect-start")
                try:
                    assert self.observer.stimulus_armed.wait(.3)
                    if self.mode!="drained":
                        self.observer.submit(event(self.observer,"guest-pressure",fault=="clock"))
                        if self.mode=="withheld": self.observer.submit(event(self.observer,"guest-timeout"))
                        self.state="PROJECT_TIMEOUT_WITNESSED" if self.mode=="withheld" else "CONTROL_PRESSURE_WITNESSED"
                    else:
                        stop_event.wait(.5);self.state="CONTROL_COLLECTION_FINISHED"
                finally:
                    world.collecting=False;world.events.append("collect-end")
                return {}
            def close(self):
                assert not world.collecting
                self.owned=[];self.attached=False;self.closed=True;world.closed=True
                world.events.append("gdb-close")
                return dict(state=self.state,category="cleanup-failed" if fault=="gdb-close" else None,
                            closed=True,attached=False)

        class Guard:
            def __init__(self, path): world.events.append("guard-created")
            def expect_flows(self, records):
                assert len(records)==2 and {x["role"] for x in records}=={"slow","healthy"}
                world.guard_roles=records;world.events.append("expect-flows");return self
            def sample(self, *, final=False, capture_write_errors_absent=None, capture_stopped=None):
                if final:
                    assert not world.live and world.observer.connections_closed.is_set() and world.closed
                    assert capture_write_errors_absent is True and capture_stopped is True
                    world.events.append("pcap-final")
                    if fault=="terminal": raise ValueError("unsupported-selected-terminal")
                coverage=[]
                if final:
                    coverage=[terminal(row,reset=row["role"]=="slow" and (world.mode=="withheld"or fault=="control-reset"),
                                       peer_only=fault=="peer-only-reset")for row in world.guard_roles]
                    if fault=="missing-slow-terminal":coverage=[row for row in coverage if row["role"]!="slow"]
                    if fault=="mismatched-slow-fd":coverage[0]["guest_fd"]+=5
                    if fault=="mismatched-slow-pcb":coverage[0]["pcb"]="0x3ffb9999"
                    if fault=="mismatched-slow-tuple":coverage[0]["guest_tuple"]["remote_port"]+=5
                    if fault=="duplicate-slow-terminal":coverage=[coverage[0],deepcopy(coverage[0])]
                    if fault=="malformed-slow-terminal":coverage[0]["server"].pop("sequence_end")
                return dict(final_wire_complete=final or fault=="live-final",
                            record_alignment_complete=True,unique_tcp_payload_bytes=1000,
                            capture_sha256=H,selected_terminal_coverage=coverage)

        def run(url, observer, **kwargs):
            assert observer.guard and not observer.ready
            world.observer=observer;world.mode=kwargs["mode"];world.events.append("peer-connect")
            observer.ready=dict(slow=("127.0.0.1",43001),healthy=("127.0.0.1",43002),declaration={"scripted":True})
            until=time.monotonic()+.7
            while not observer.stimulus_armed.wait(.002):
                if observer.incomplete_reasons: break
                assert time.monotonic()<until
            if not observer.incomplete_reasons and kwargs["mode"]!="drained":
                while not (observer.timeout if kwargs["mode"]=="withheld" else observer.pressure):
                    if observer.incomplete_reasons: break
                    assert time.monotonic()<until
                    time.sleep(.002)
            world.events.append("peer-closed");observer.connections_closed.set()
            result=good_peer_report(kwargs["mode"],transport=transport,fault=fault,observer=observer)
            if fault in ("remote-reset","peer-only-reset"):
                result.update(slow_transport_eof=False,slow_remote_reset=True,slow_termination_kind="remote-reset")
            if fault=="ragged-control":result.update(slow_termination_kind="tls-ragged-eof",slow_clean_tls_eof=False)
            if fault=="mismatched-timeout-token":result["slow_termination_token"]="wrong-token"
            return p.finish_report(result,observer)

        peer=types.SimpleNamespace(Observer=p.Observer,Binding=p.Binding,run=run,finish_report=p.finish_report,
                                   declaration=lambda: {"scripted":True},CASE_SECONDS=.8,CLEANUP_SECONDS=.05,TCP_LIMIT=p.TCP_LIMIT)
        host=types.SimpleNamespace(Guest=Guest,API={"write":lambda path,value:path.write_text(json.dumps(value),encoding="utf-8")})
        self.modules=types.SimpleNamespace(host=host,peer=peer,gdb=types.SimpleNamespace(
            Collector=Collector,SOURCE=SOURCE,ELF_SHA=ELF),pcap=types.SimpleNamespace(CaptureGuard=Guard))

    def execute(self, mode="withheld"):
        with mock.patch.object(socket,"socket",side_effect=AssertionError("live socket forbidden")), \
             mock.patch.object(socket,"create_connection",side_effect=AssertionError("live connection forbidden")), \
             mock.patch.object(subprocess,"Popen",side_effect=AssertionError("process forbidden")), \
             mock.patch.object(subprocess,"run",side_effect=AssertionError("process forbidden")), \
             mock.patch.object(subprocess,"check_output",side_effect=AssertionError("Git/process forbidden")):
            return r.run_fixture(self.modules,self.options,(),mode,H,"scripted-pressure",lambda:self.fault!="pins",
                timing=r.Timing(outer=2,cleanup_reserve=.5,poll=.002,wire_poll=.002,collector_join=.3,watcher_join=.3,final_peer_join=.2))


class OrchestrationTests(unittest.TestCase):
    def run_world(self, mode="withheld", fault=None, transport="ws"):
        with tempfile.TemporaryDirectory(prefix="pressure-scripted-") as directory:
            world=World(Path(directory)/"result",fault,transport)
            report=world.execute(mode)
            self.assertFalse(any(t.name.startswith("root-pressure-") for t in threading.enumerate()))
            self.assertFalse(world.live)
            return report,world.events

    def test_withheld_order_and_final_recomputation(self):
        report,events=self.run_world()
        self.assertEqual(report["state"],"PASS",report)
        self.assertEqual(report["pressure_objective"],"PASS")
        for before,after in [("guard-created","peer-connect"),("peer-connect","gdb-start"),
                             ("expect-flows","gdb-arm"),("collect-end","gdb-close"),
                             ("peer-closed","health"),("gdb-close","health"),("health","guest-exit"),
                             ("guest-exit","pcap-final")]:
            self.assertLess(events.index(before),events.index(after))
        self.assertTrue(report["observer"]["wire"]["final"])

    def test_control_modes_and_wss_service_mapping(self):
        for mode in ("drained","read-resume"):
            with self.subTest(mode=mode):
                report,_=self.run_world(mode,transport="wss")
                self.assertEqual(report["state"],"PASS",report)
                self.assertEqual(report["control_state"],"PASS")
                self.assertEqual(report["pressure_objective"],"INCOMPLETE")
                self.assertTrue(all(x["guest_tuple"]["local_port"]==443 for x in report["roles"]))

    def test_each_missing_or_bad_proof_prevents_pass(self):
        for fault in ("role-map","allocation","boot","missing-boot","capture-stopped","dump-write",
                      "terminal","live-final","pins","gdb-close","clock",
                      "missing-slow-terminal","mismatched-slow-fd","mismatched-slow-pcb",
                      "mismatched-slow-tuple","duplicate-slow-terminal","malformed-slow-terminal",
                      "peer-only-reset"):
            with self.subTest(fault=fault):
                report,_=self.run_world(fault=fault)
                self.assertNotEqual(report["state"],"PASS",report)
                self.assertTrue(report["errors"])

    def test_role_map_has_no_fallback_or_ambiguous_owner(self):
        ready=dict(slow=("127.0.0.1",43001),healthy=("127.0.0.1",43002),declaration={})
        with tempfile.TemporaryDirectory() as directory:
            world=World(Path(directory)/"out")
            for change in ("port","pcb","closing","count"):
                rows=deepcopy(world.rows)
                if change=="port":rows[1]["guest_tuple"]["remote_port"]=43001
                elif change=="pcb":rows[1]["pcb"]=rows[0]["pcb"]
                elif change=="closing":rows[0]["closing"]=True
                else:rows.append(deepcopy(rows[0]))
                with self.subTest(change=change),self.assertRaises(r.RunFailure):
                    r.map_roles(ready,rows,80)

    def test_control_close_or_reset_failure_never_qualifies(self):
        for mode in ("drained", "read-resume"):
            for fault in ("normal-close-not-sent", "normal-close-wrong-payload", "control-reset"):
                with self.subTest(mode=mode, fault=fault):
                    report, _ = self.run_world(mode, fault=fault, transport="wss")
                    self.assertNotEqual(report["state"], "PASS", report)
                    self.assertEqual(report["control_state"], "INCOMPLETE")
                    self.assertTrue(report["guest_stopped"])
                    self.assertTrue(report["peer_joined"])

    def test_expired_fixture_cannot_be_promoted_by_final_wire(self):
        for fault in ("watchdog", "observation-exhausted"):
            with self.subTest(fault=fault):
                report, _ = self.run_world(fault=fault)
                self.assertNotEqual(report["state"], "PASS", report)
                self.assertTrue(report["wire"]["final_wire_complete"])
                self.assertTrue(report["guest_stopped"])

    def test_wire_alignment_is_not_final_proof(self):
        binding=p.Binding("scripted-pressure",SOURCE,ELF,54,"0x1234",H)
        with self.assertRaises(r.RunFailure):
            r.wire_event(binding,dict(record_alignment_complete=True,final_wire_complete=False,
                                     unique_tcp_payload_bytes=4,capture_sha256=H),True)

    def test_main_dryrun_and_option_check_never_launch(self):
        for check in (False,True):
            opts=types.SimpleNamespace(check_options=check,execute=False)
            host=types.SimpleNamespace(API={"options":lambda argv:opts})
            modules=types.SimpleNamespace(host=host)
            with mock.patch.object(r,"load_modules",return_value=modules), \
                 mock.patch.object(r,"prepare",return_value=((),{},H,lambda:True)), \
                 mock.patch.object(r,"run_fixture",side_effect=AssertionError("guest forbidden")), \
                 mock.patch("builtins.print"):
                self.assertEqual(r.main(["--mode","drained"]),0)


class ConfigurationPreflightTests(unittest.TestCase):
    def configure(self, world, directory):
        config=directory/"xtensa_esp32.so"
        config.write_bytes(b"tiny scripted official-config identity")
        executable=directory/"fixture-direct-gdb"
        executable.write_bytes(b"never executed")
        qualification=directory/"qualification.json"
        qualification.write_bytes(b"scripted qualification identity")
        world.options.qualification=qualification
        world.options.certificate=world.options.openssl=None
        world.options.check_options=False;world.options.execute=True
        gdb=world.modules.gdb
        gdb.DEFAULT_CONFIG=config;gdb.CONFIG_BYTES=config.stat().st_size
        gdb.CONFIG_SHA=r.identity(config)["sha256"]
        gdb.DEFAULT_GDB=executable;gdb.GDB_SHA=r.identity(executable)["sha256"]
        gdb.QUAL_SHA=r.identity(qualification)["sha256"]
        q=dict(source_commit=SOURCE,elf=dict(sha256=ELF))
        prepared=(q,{},None,[],{},{},{},{qualification:r.identity(qualification)})
        world.modules.host.API.update(preflight=lambda options:prepared,SOURCE=SOURCE,CHECKOUT="b"*40,
                                      options=lambda argv:world.options)
        return config

    def test_exact_config_is_in_shared_before_after_manifest(self):
        with tempfile.TemporaryDirectory(prefix="pressure-v5-config-") as directory:
            directory=Path(directory);world=World(directory/"out")
            config=self.configure(world,directory)
            prepared,manifest,digest,recheck=r.prepare(world.modules,world.options)
            self.assertEqual(prepared[-1][config],r.identity(config))
            self.assertIn(r.identity(config),manifest["inputs"].values())
            self.assertEqual(len(digest),64)
            self.assertTrue(recheck())
            self.assertFalse(world.live)
            self.assertFalse(world.output.exists())

    def test_missing_or_changed_config_fails_before_actual_action(self):
        for fault in ("missing","wrong-size","same-size-wrong-hash"):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory(prefix="pressure-v5-config-") as directory:
                directory=Path(directory);world=World(directory/"out")
                config=self.configure(world,directory)
                if fault=="missing":config.unlink()
                elif fault=="wrong-size":config.write_bytes(config.read_bytes()+b"x")
                else:
                    body=bytearray(config.read_bytes());body[0]^=1;config.write_bytes(body)
                with mock.patch.object(r,"load_modules",return_value=world.modules), \
                     mock.patch.object(r,"run_fixture",side_effect=AssertionError("actual action forbidden")) as action, \
                     mock.patch.object(subprocess,"Popen",side_effect=AssertionError("process forbidden")), \
                     mock.patch.object(socket,"socket",side_effect=AssertionError("socket forbidden")), \
                     mock.patch("builtins.print"):
                    with self.assertRaises((FileNotFoundError,r.RunFailure)):
                        r.main(["--mode","drained","--execute"])
                    action.assert_not_called()
                self.assertFalse(world.live)
                self.assertFalse(world.output.exists())

    def test_config_mutated_after_guest_exit_vetoes_overall_pass(self):
        with tempfile.TemporaryDirectory(prefix="pressure-v5-config-") as directory:
            directory=Path(directory);world=World(directory/"out")
            config=self.configure(world,directory)
            prepared,manifest,digest,recheck=r.prepare(world.modules,world.options)
            original_guest=world.modules.host.Guest
            class ChangedConfigGuest(original_guest):
                def __exit__(self,*args):
                    result=super().__exit__(*args)
                    body=bytearray(config.read_bytes());body[0]^=1;config.write_bytes(body)
                    return result
            world.modules.host.Guest=ChangedConfigGuest
            with mock.patch.object(socket,"socket",side_effect=AssertionError("live socket forbidden")), \
                 mock.patch.object(socket,"create_connection",side_effect=AssertionError("live connection forbidden")), \
                 mock.patch.object(subprocess,"Popen",side_effect=AssertionError("process forbidden")), \
                 mock.patch.object(subprocess,"run",side_effect=AssertionError("process forbidden")), \
                 mock.patch.object(subprocess,"check_output",side_effect=AssertionError("Git/process forbidden")):
                report=r.run_fixture(world.modules,world.options,prepared,"withheld",digest,"scripted-v5-config",recheck,
                    timing=r.Timing(outer=2,cleanup_reserve=.5,poll=.002,wire_poll=.002,collector_join=.3,watcher_join=.3,final_peer_join=.2))
            self.assertFalse(recheck())
            self.assertEqual(report["state"],"INCOMPLETE",report)
            self.assertIn("final-input-pin-recheck-failed",report["errors"])
            self.assertEqual(report["peer"]["state"],"PASS")
            self.assertTrue(report["wire"]["final_wire_complete"])
            self.assertFalse(world.live)
            self.assertFalse(any(t.name.startswith("root-pressure-") for t in threading.enumerate()))


if __name__=="__main__":
    unittest.main(verbosity=2)
