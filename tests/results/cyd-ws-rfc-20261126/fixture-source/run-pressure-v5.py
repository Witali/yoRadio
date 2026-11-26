"""Dry-run-default owner of one pinned pressure fixture, GDB and PCAP observer.

Only --execute may start the existing Guest/peer/Collector. Raw material stays
in Guest.private outside repositories. Root must review before actual use.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import dataclasses
import hashlib
import importlib.util
import ipaddress
import json
import math
from pathlib import Path
import re
import sys
import threading
import time
import types
import uuid

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PINS = {
    "pressure-host.py": "845507b72af324e479b8abf934fc3fb4ea46bd2704336ba53317af09f8847944",
    "pressure-peer-v2.py": "36410cab029d49b9868bdb509ffa891f3b3603fa8e9e75611e946d611cf9b22c",
    "gdb-observer-v5.py": "6a9e8d1eca04840dedac2d7fdd975cba72ff7c7c45fce29bed04390d4d2b689e",
    "pcap-observer-v2.py": "c253815bf97fe2981a562cbf56e06ed12ce6854305b695922fa5de029e717723",
}
OUTER_SECONDS = 210.0
CLEANUP_RESERVE = 55.0


class RunFailure(Exception):
    pass


def need(condition, category):
    if not condition:
        raise RunFailure(category)


def category(error):
    value = getattr(error, "category", None)
    if value is None and isinstance(error, (RunFailure, ValueError)) and error.args:
        value = error.args[0]
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9-]{1,80}", value):
        value = re.sub(r"[^a-z0-9]+", "-", type(error).__name__.lower()).strip("-")
    return (value or "unknown-error")[:80]


def identity(path):
    body = Path(path).read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def import_pinned(filename):
    path = BASE / filename
    need(identity(path)["sha256"] == PINS[filename], "integration-module-pin-changed")
    name = "pressure_root_" + filename.replace("-", "_").replace(".", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # Required by dataclasses and nested typed APIs.
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def load_modules():
    return types.SimpleNamespace(host=import_pinned("pressure-host.py"),
                                 peer=import_pinned("pressure-peer-v2.py"),
                                 gdb=import_pinned("gdb-observer-v5.py"),
                                 pcap=import_pinned("pcap-observer-v2.py"))


def prepare(modules, options):
    """Existing full image/source/model/config/memory gate; starts no guest."""
    host, gdb = modules.host, modules.gdb
    prepared = host.API["preflight"](options)
    q = prepared[0]
    need(host.API["SOURCE"] == gdb.SOURCE and q["source_commit"] == gdb.SOURCE,
         "collector-source-does-not-match-guest")
    need(q["elf"]["sha256"] == gdb.ELF_SHA, "collector-elf-does-not-match-guest")
    need(identity(options.qualification)["sha256"] == gdb.QUAL_SHA,
         "collector-qualification-epoch-mismatch")
    need(identity(gdb.DEFAULT_GDB)["sha256"] == gdb.GDB_SHA, "collector-gdb-pin-changed")
    config_pin = identity(gdb.DEFAULT_CONFIG)
    need(config_pin == dict(bytes=gdb.CONFIG_BYTES, sha256=gdb.CONFIG_SHA),
         "collector-architecture-config-pin-changed")
    inputs = dict(prepared[-1])
    inputs.update({BASE / name: identity(BASE / name) for name in PINS})
    inputs[Path(__file__)] = identity(Path(__file__))
    inputs[gdb.DEFAULT_GDB] = identity(gdb.DEFAULT_GDB)
    inputs[gdb.DEFAULT_CONFIG] = config_pin
    # Public CA/certificate identity is part of WSS input binding; never record
    # a key body, credential location, argv or private-key fingerprint here.
    for path in (options.ca, options.certificate, options.openssl):
        if path is not None:
            inputs[path] = identity(path)
    prepared = (*prepared[:-1], inputs)
    safe_inputs = {}
    for index, (path, pin) in enumerate(sorted(inputs.items(), key=lambda pair: str(pair[0]))):
        try:
            label = path.relative_to(ROOT).as_posix()
        except ValueError:
            label = "external-input-" + str(index)
        safe_inputs[label] = pin
    manifest = dict(source_commit=gdb.SOURCE, elf_sha256=gdb.ELF_SHA,
                    checkout_commit=host.API["CHECKOUT"], inputs=safe_inputs)
    digest = hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return prepared, manifest, digest, lambda: all(identity(p) == pin for p, pin in inputs.items())


def map_roles(ready, rows, service_port):
    need(isinstance(ready, dict) and set(ready) == {"slow", "healthy", "declaration"}, "calibrated-role-map-missing")
    need(isinstance(rows, list) and len(rows) == 2, "exactly-two-guest-roles-required")
    ports = {}
    for role in ("slow", "healthy"):
        address = ready[role]
        need(isinstance(address, (tuple, list)) and len(address) == 2, "host-ipv4-tuple-required")
        need(ipaddress.IPv4Address(address[0]).is_loopback and type(address[1]) is int and
             0 < address[1] < 65536, "host-loopback-role-required")
        ports[role] = address[1]
    need(ports["slow"] != ports["healthy"], "host-role-port-collision")
    records = []
    for role in ("slow", "healthy"):
        matched = []
        for row in rows:
            guest = row.get("guest_tuple")
            need(isinstance(guest, dict) and set(guest) == {"local_ip", "remote_ip", "local_port", "remote_port"}, "exact-guest-tuple-required")
            for key in ("local_ip", "remote_ip"):
                ipaddress.IPv4Address(guest[key])
            need(type(guest["local_port"]) is int and guest["local_port"] == service_port and
                 type(guest["remote_port"]) is int and 0 < guest["remote_port"] < 65536,
                 "guest-service-port-mismatch")
            if guest["remote_port"] == ports[role]:
                matched.append(row)
        need(len(matched) == 1, "exact-host-port-guest-pcb-map-unavailable")
        row = matched[0]
        need(row.get("closing") is False and type(row.get("guest_fd")) is int and row["guest_fd"] >= 0,
             "live-guest-role-required")
        need(isinstance(row.get("pcb"), str) and re.fullmatch(r"0x[0-9a-f]+", row["pcb"]) and
             int(row["pcb"], 16) > 0, "canonical-live-pcb-required")
        records.append(dict(role=role, guest_fd=row["guest_fd"], pcb=row["pcb"], guest_tuple=dict(row["guest_tuple"])))
    need(len({r["guest_fd"] for r in records}) == len({r["pcb"] for r in records}) == 2,
         "guest-role-owner-collision")
    need(len({json.dumps(r["guest_tuple"], sort_keys=True) for r in records}) == 2,
         "guest-role-tuple-collision")
    return records


class Worker:
    def __init__(self, name, target, observer):
        self.name, self.result, self.error = name, None, None
        self.entered, self.done = threading.Event(), threading.Event()
        def invoke():
            self.entered.set()
            try:
                self.result = target()
            except BaseException as error:
                self.error = category(error)
                observer.incomplete((name + "-" + self.error)[:80])
            finally:
                self.done.set()
        self.thread = threading.Thread(target=invoke, name="root-pressure-" + name, daemon=True)

    def start(self):
        self.thread.start()
        return self

    def join(self, seconds):
        self.thread.join(max(0, seconds))
        return not self.thread.is_alive()


@dataclasses.dataclass(frozen=True)
class Timing:
    outer: float = OUTER_SECONDS
    cleanup_reserve: float = CLEANUP_RESERVE
    poll: float = .01
    wire_poll: float = .1
    collector_join: float = 2.5
    watcher_join: float = 2.5
    final_peer_join: float = 3.0

    def __post_init__(self):
        need(all(type(v) in (int, float) and math.isfinite(v) and v > 0
                 for v in dataclasses.asdict(self).values()), "positive-root-budgets-required")
        need(self.outer <= OUTER_SECONDS and self.cleanup_reserve < self.outer,
             "outer-budget-must-not-extend")


def wire_event(binding, sample, final, *, guest_tuple=None):
    need(type(sample.get("unique_tcp_payload_bytes")) is int, "wire-byte-count-missing")
    need(sample.get("final_wire_complete") is final, "wire-final-proof-state-mismatch")
    event = dict(dataclasses.asdict(binding), kind="wire-accounting", origin="root-pcap-unique-tcp",
                 coverage="all-owned-server-connections-from-connect",
                 unique_tcp_payload_bytes=sample["unique_tcp_payload_bytes"], final=final,
                 evidence_sha256=sample["capture_sha256"])
    if final:
        need(isinstance(guest_tuple, dict), "final-actual-slow-tuple-required")
        coverage = sample.get("selected_terminal_coverage")
        need(isinstance(coverage, list), "final-selected-terminal-coverage-missing")
        matching = [entry for entry in coverage if isinstance(entry, dict) and
                    entry.get("role") == "slow" and entry.get("guest_fd") == binding.guest_fd and
                    entry.get("pcb") == binding.pcb and entry.get("guest_tuple") == guest_tuple]
        need(len(matching) == 1, "final-exact-slow-terminal-proof-required")
        event["selected_slow_terminal"] = deepcopy(matching[0])
    return event


def run_fixture(modules, options, prepared, mode, inputs_sha256, run_id, recheck, *, timing=Timing()):
    """Injectable seam for pure scripted tests; CLI always uses pinned modules."""
    host, peer, gdb, pcap = modules.host, modules.peer, modules.gdb, modules.pcap
    need(mode in ("withheld", "drained", "read-resume"), "pressure-mode")
    observer = peer.Observer()
    observer.arm_wire_guard(run_id, gdb.SOURCE, gdb.ELF_SHA, PINS["pcap-observer-v2.py"], inputs_sha256=inputs_sha256)
    report = dict(state="INCOMPLETE", mode=mode, run_id=run_id, source_commit=gdb.SOURCE,
                  elf_sha256=gdb.ELF_SHA, inputs_sha256=inputs_sha256, physical_tested=False,
                  pressure_objective="INCOMPLETE", control_state="INCOMPLETE", errors=[],
                  raw_material_outside_repositories=True, original_peer_watchdog_unchanged=True)
    stop_collect, stop_watch = threading.Event(), threading.Event()
    need(stop_collect is not observer.stop, "collector-stop-must-be-independent")
    guard_lock = threading.Lock()
    collector = guard = guest = peer_worker = collect_worker = watch_worker = None
    collector_receipt = peer_report = wire_final = None
    collector_joined_before_close = peer_joined = watcher_joined = False
    live_samples = 0
    root_started = time.monotonic()
    outer_end = root_started + timing.outer
    action_end = outer_end - timing.cleanup_reserve
    peer_started = None

    def fail(reason):
        reason = reason[:80]
        if reason not in report["errors"] and len(report["errors"]) < 16:
            report["errors"].append(reason)
        observer.incomplete(reason)

    def remaining(end=action_end):
        value = end - time.monotonic()
        need(value > 0, "root-outer-activity-deadline")
        return value

    def monitor():
        remaining()
        guest.check()
        for worker in (peer_worker, collect_worker, watch_worker):
            need(worker is None or worker.error is None, "root-worker-error")
        snap = observer.snapshot()
        need(not snap["invalid"] and not snap["incomplete_reasons"], "observer-incomplete")

    def collect_cleanup():
        nonlocal collector_receipt, collector_joined_before_close
        stop_collect.set()
        collector_joined_before_close = collect_worker is None or collect_worker.join(timing.collector_join)
        if not collector_joined_before_close:
            fail("collector-not-joined-before-close")
        if collector is not None:
            try:
                # Frozen close() safely cancels/disarms/resumes/disconnects and
                # terminates only owned GDB if a faulty worker did not join.
                collector_receipt = collector.close()
            except BaseException as error:
                fail("collector-close-" + category(error))
        if collect_worker is not None and not collect_worker.join(timing.collector_join):
            fail("collector-worker-remains-live")

    try:
        with host.Guest(options, prepared) as guest:
            try:
                remaining()
                need(guest.private is not None and guest.endpoint is not None, "guest-private-endpoint-required")
                guard = pcap.CaptureGuard(guest.private / "wire.pcap")
                def watch():
                    nonlocal live_samples
                    while not stop_watch.is_set():
                        guest.check()
                        with guard_lock:
                            sample = guard.sample(final=False)
                        need(sample.get("final_wire_complete") is False, "live-wire-must-remain-provisional")
                        need(type(sample.get("unique_tcp_payload_bytes")) is int and
                             0 <= sample["unique_tcp_payload_bytes"] <= peer.TCP_LIMIT, "live-wire-envelope")
                        live_samples += 1
                        binding = observer.binding
                        if binding is not None:
                            observer.submit(wire_event(binding, sample, False))
                        if stop_watch.wait(timing.wire_poll):
                            break
                watch_worker = Worker("wire-watch", watch, observer).start()
                peer_started = time.monotonic()  # Host ownership budget only, never a guest T0.
                peer_worker = Worker("peer", lambda: peer.run(
                    guest.endpoint.url, observer, mode=mode, ca=options.ca,
                    certificate_sha256=guest.binding.get("certificate_sha256")), observer).start()
                setup_end = min(action_end, peer_started + peer.CASE_SECONDS - peer.CLEANUP_SECONDS)
                while observer.ready is None:
                    monitor()
                    need(not peer_worker.done.is_set(), "peer-exited-before-calibration")
                    remaining(setup_end)
                    peer_worker.done.wait(timing.poll)
                need(observer.ready["declaration"] == peer.declaration(), "peer-declaration-changed")
                collector = gdb.Collector(observer, run_id, inputs_sha256, guest.private / "gdb-observer",
                                          mode=mode, elf=options.qualification.parent / "compiled/yoradio_cyd2usb_native.elf",
                                          qualification=options.qualification)
                rows = collector.start("127.0.0.1:" + str(guest.gdb_port))
                roles = map_roles(observer.ready, rows, 443 if options.transport == "wss" else 80)
                report["roles"] = roles
                slow = next(r for r in roles if r["role"] == "slow")
                binding = peer.Binding(run_id, gdb.SOURCE, gdb.ELF_SHA, slow["guest_fd"], slow["pcb"], inputs_sha256)
                observer.bind(binding, guest_tuple=slow["guest_tuple"])
                collector.bind_slow(slow["guest_fd"], slow["pcb"], slow["guest_tuple"])
                with guard_lock:
                    guard.expect_flows(roles)
                collector.arm()
                seconds = remaining(min(action_end, peer_started + peer.CASE_SECONDS))
                collect_worker = Worker("collector", lambda: collector.collect(stop_collect, seconds=seconds), observer).start()
                need(collect_worker.entered.wait(min(.5, remaining())), "collector-worker-not-started")
                monitor()
                observer.arm_stimulus()
                while not peer_worker.done.wait(timing.poll):
                    monitor()
                    need(time.monotonic() < peer_started + peer.CASE_SECONDS + timing.final_peer_join,
                         "peer-root-join-deadline")
                peer_joined = peer_worker.join(timing.final_peer_join)
                need(peer_joined and peer_worker.error is None, "peer-worker-not-joined")
                peer_report = peer_worker.result
                need(isinstance(peer_report, dict) and peer_report.get("threads_joined") is True and
                     observer.connections_closed.is_set(), "peer-owned-cleanup-missing")
                need(not peer_report.get("errors"), "peer-fixture-errors")
                collect_cleanup()
                need(collector_joined_before_close and isinstance(collector_receipt, dict), "collector-cleanup-missing")
                need(collector_receipt.get("closed") is True and collector_receipt.get("attached") is False and
                     collector_receipt.get("category") is None and len(collector.owned) == 0, "collector-owner-cleanup-failed")
                io = collector.io
                need(io is not None and io.child.poll() is not None and not io.reader.is_alive(), "owned-gdb-child-or-reader-live")
                initial = guest.report.get("initial_health")
                final = guest.client["health_summary"](guest.health.read())
                status = guest.health.read("/api/native/status")
                guest.health.close()
                need(isinstance(initial, dict) and isinstance(initial.get("boot_id"), str) and bool(initial["boot_id"]) and
                     guest.client["health_verdict"](initial, final) == "PASS" and
                     final.get("allocation_failures") == 0 and final.get("boot_id") == initial.get("boot_id") and
                     type(initial.get("uptime_ms")) is int and type(final.get("uptime_ms")) is int and
                     final["uptime_ms"] >= initial["uptime_ms"] >= 0 and
                     status.get("audio") is False, "post-close-health-or-boot-failed")
                report["post_close_health"] = final
                report["health_after_peer_and_debugger_close"] = True
                guest.check()
            except BaseException as error:
                fail(category(error))
            finally:
                if collector_receipt is None:
                    collect_cleanup()
                if peer_worker is not None and not peer_worker.done.is_set():
                    fail("root-cancels-incomplete-peer")
                if peer_worker is not None:
                    left = max(0, min(outer_end - time.monotonic(),
                                     (peer_started + peer.CASE_SECONDS + timing.final_peer_join) - time.monotonic()))
                    peer_joined = peer_worker.join(left)
                    if not peer_joined:
                        fail("peer-worker-remains-live-before-guest-exit")
                    elif peer_report is None:
                        peer_report = peer_worker.result
                stop_watch.set()
                watcher_joined = watch_worker is None or watch_worker.join(timing.watcher_join)
                if not watcher_joined:
                    fail("wire-watcher-not-joined")
                guest.report["pressure_root_activity_state"] = "NONPASS" if report["errors"] else "COMPLETED"
                guest.save()
            if report["errors"]:
                raise RunFailure("root-pressure-activity-incomplete")
    except BaseException as error:
        fail(category(error))

    # Guest context has stopped QEMU and closed its log before any final sample.
    if peer_worker is not None and not peer_joined:
        peer_joined = peer_worker.join(min(timing.final_peer_join, max(0, outer_end - time.monotonic())))
    try:
        need(guest is not None, "guest-lifecycle-missing")
        required = ("owned_guest_stopped", "all_input_pins_still_match", "host_and_launcher_pins_still_match",
                    "checkout_commit_still_matches", "flash_unchanged", "fatal_markers_absent",
                    "capture_write_errors_absent", "capture_stopped")
        need(all(guest.report.get(key) is True for key in required), "final-guest-input-or-capture-gate-missing")
        need(peer_joined and peer_report is not None and peer_report.get("threads_joined") is True and
             observer.connections_closed.is_set() and watcher_joined, "final-peer-or-watcher-cleanup-missing")
        need(observer.binding is not None and guard is not None, "final-wire-role-binding-missing")
        with guard_lock:
            wire_final = guard.sample(final=True, capture_write_errors_absent=guest.report["capture_write_errors_absent"],
                                      capture_stopped=guest.report["capture_stopped"])
        need(wire_final.get("final_wire_complete") is True and len(wire_final.get("selected_terminal_coverage", [])) == 2,
             "final-two-role-terminal-wire-proof-missing")
        observer.submit(wire_event(observer.binding, wire_final, True, guest_tuple=slow["guest_tuple"]))
        peer_report = peer.finish_report(peer_report, observer)
        need(recheck() is True, "final-input-pin-recheck-failed")
        allowed = ("PROJECT_TIMEOUT_WITNESSED",) if mode == "withheld" else (
            "CONTROL_PRESSURE_WITNESSED", "CONTROL_COLLECTION_FINISHED")
        need(collector_receipt is not None and collector_receipt.get("state") in allowed and
             collector_receipt.get("category") is None and collector_joined_before_close, "guest-observer-final-evidence-missing")
        need(peer_report.get("state") == "PASS" and not report["errors"], "peer-pressure-or-control-not-proved")
        need(time.monotonic() <= outer_end, "root-outer-duration-exceeded")
        report.update(state="PASS", pressure_objective=peer_report["pressure_objective"],
                      control_state=peer_report["control_state"])
    except BaseException as error:
        fail(category(error))
    report.update(elapsed_seconds=round(time.monotonic() - root_started, 3), outer_seconds=timing.outer,
                  peer_joined=peer_joined, collector_joined_before_close=collector_joined_before_close,
                  watcher_joined=watcher_joined, provisional_wire_samples=live_samples,
                  guest_stopped=bool(guest and guest.report.get("owned_guest_stopped")),
                  observer=observer.snapshot(), collector=collector_receipt, peer=peer_report, wire=wire_final)
    if report["errors"]:
        report["state"] = "INCOMPLETE"
    if options.output.exists():
        host.API["write"](options.output / "pressure.json", report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--mode", choices=("withheld", "drained", "read-resume"), default="withheld")
    known, rest = parser.parse_known_args(argv)
    modules = load_modules()
    options = modules.host.API["options"](rest)
    if options.check_options:
        print(json.dumps(dict(state="OPTIONS_PASS", mode=known.mode, guest_started=False)))
        return 0
    prepared, manifest, digest, recheck = prepare(modules, options)
    if not options.execute:
        print(json.dumps(dict(state="PREFLIGHT_PASS", mode=known.mode, guest_started=False,
                              inputs_sha256=digest, root_outer_seconds=OUTER_SECONDS)))
        return 0
    report = run_fixture(modules, options, prepared, known.mode, digest, "r06-" + uuid.uuid4().hex, recheck)
    modules.host.API["write"](options.output / "pressure-inputs.json", manifest)
    print(json.dumps(dict(state=report["state"], mode=known.mode, guest_stopped=report["guest_stopped"],
                          pressure_objective=report["pressure_objective"], control_state=report["control_state"])))
    return 0 if report["state"] == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(json.dumps(dict(state="INCOMPLETE", category=category(error))))
        raise SystemExit(1)
