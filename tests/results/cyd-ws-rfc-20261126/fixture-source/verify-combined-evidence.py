"""Read-only cross-check of retained live results; starts no guest or process."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
RUNS = ROOT / ".build/cpbuf24"
SOURCE = "95672e8f673ec977b6f61b78eeba6958d0d992ac"
CHECKOUT = "162bdb72407e3aaae5c69c8ecc135a6bf129ad40"


def read(path):
    return json.loads(path.read_bytes())


def pin(path):
    body = path.read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / filename)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def main():
    out = BASE / "combined-evidence-verification-01.json"
    assert not out.exists()
    root_review = read(BASE / "run-pressure-v5-root-review.json")
    for name, expected in root_review["files"].items():
        assert pin(BASE / name) == expected, name
    integration = module("combined_pressure_root", "run-pressure-v5.py")
    modules = integration.load_modules()
    peer, gdb = modules.peer, modules.gdb
    assert pin(gdb.DEFAULT_GDB) == dict(bytes=gdb.GDB_BYTES, sha256=gdb.GDB_SHA)
    assert pin(gdb.DEFAULT_CONFIG) == dict(bytes=gdb.CONFIG_BYTES, sha256=gdb.CONFIG_SHA)
    qualified = read(ROOT / ".build/cws-close26/target/sdk/continuous/qualification.json")
    assert qualified["passed"] and qualified["source_commit"] == SOURCE
    assert qualified["elf"]["sha256"] == gdb.ELF_SHA
    binding_keys = ("source_commit", "sdk_commit", "app_sha256", "qemu_sha256",
                    "sdkconfig_sha256", "fixture_sha256", "rom_manifest_sha256", "backend")
    final_flags = ("owned_guest_stopped", "all_input_pins_still_match",
                   "host_and_launcher_pins_still_match", "checkout_commit_still_matches",
                   "flash_unchanged", "fatal_markers_absent", "capture_write_errors_absent",
                   "capture_stopped")
    result = dict(source_commit=SOURCE, checkout_commit=CHECKOUT, backend="continuous",
                  physical_tested=False, baseline=[], pressure_runs=[], all_passed=False,
                  original_outcomes_unchanged=True, raw_material_outside_repositories=True,
                  scope="84 original cases per transport plus separately qualified R06 with two controls; original raw matrices remain INCOMPLETE")
    for transport in ("ws", "wss"):
        baseline_dir = RUNS / ("rfc-" + transport + "-close-01")
        baseline = read(baseline_dir / "client/report.json")
        launch = read(baseline_dir / "launch.json")
        assert baseline["state"] == "INCOMPLETE" and baseline["complete_matrix"] is False
        assert len(baseline["cases"]) == 85 and len({c["id"] for c in baseline["cases"]}) == 85
        passed = [c for c in baseline["cases"] if c["state"] == "PASS"]
        missing = [c for c in baseline["cases"] if c["state"] != "PASS"]
        assert len(passed) == 84 and len(missing) == 1 and missing[0]["id"] == "R06"
        assert missing[0]["state"] == "INCOMPLETE" and missing[0]["raw_outcome"] == "NOT_EXERCISED"
        assert baseline["final_resource"] == "PASS"
        assert launch["source_commit"] == SOURCE and launch["checkout_commit"] == CHECKOUT
        assert all(launch[k] is True for k in ("owned_processes_stopped", "all_input_pins_still_match",
                                              "released_helper_pins_still_match", "checkout_commit_still_matches", "flash_unchanged"))
        assert baseline["binding"]["source_commit"] == SOURCE
        assert baseline["binding"]["app_sha256"] == qualified["image"]["sha256"]
        assert baseline["binding"]["sdkconfig_sha256"] == qualified["config"]["sha256"]
        result["baseline"].append(dict(transport=transport, original_passed=84,
            original_incomplete=["R06"], report=pin(baseline_dir / "client/report.json"),
            launch=pin(baseline_dir / "launch.json"),
            outcomes=[{k: c[k] for k in ("id", "title", "raw_outcome", "rfc", "project", "resource", "state")} for c in baseline["cases"]]))
        for mode in ("drained", "withheld", "read-resume"):
            directory = RUNS / ("rfc-r06-final-" + mode + "-" + transport + "-01")
            report = read(directory / "pressure.json")
            host = read(directory / "host.json")
            inputs = read(directory / "pressure-inputs.json")
            assert report["state"] == "PASS" and report["mode"] == mode and not report["errors"]
            assert all(host.get(k) is True for k in final_flags)
            assert all(report.get(k) is True for k in ("peer_joined", "collector_joined_before_close", "watcher_joined", "guest_stopped"))
            assert all(host["binding"][k] == baseline["binding"][k] for k in binding_keys)
            assert host["qualified_image"] == qualified["image"] and host["qualified_elf"] == qualified["elf"]
            assert host["qualified_config"] == qualified["config"]
            assert inputs["source_commit"] == SOURCE and inputs["checkout_commit"] == CHECKOUT
            assert hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == report["inputs_sha256"]
            for path, expected in inputs["inputs"].items():
                if not path.startswith("external-input-"):
                    assert pin(ROOT / path) == expected, path
            collector = report["collector"]
            assert collector["closed"] and not collector["attached"] and collector["category"] is None
            cleanup = collector["io_cleanup"]
            assert not cleanup["issues"] and all(cleanup[k] is True for k in ("process_stopped", "reader_joined", "stdin_closed", "stdout_closed", "pipe_EOF"))
            assert report["post_close_health"]["allocation_failures"] == 0
            assert report["health_after_peer_and_debugger_close"] is True
            if transport == "wss":
                assert len(report["peer"]["tls"]) == 2
                for tls in report["peer"]["tls"]:
                    assert tls["version"] == "TLSv1.2" and tls["cipher"] == peer.TLS_CIPHER
                    assert tls["verify_mode"] == "CERT_REQUIRED" and tls["hostname_checked"] is True
                    assert tls["host_date_verification_enabled"] is True
                    assert tls["certificate_sha256"] == host["binding"]["certificate_sha256"]
            private = Path(tempfile.gettempdir()) / host["private_run_basename"]
            assert private.parent == Path(tempfile.gettempdir()) and private.is_dir()
            capture = modules.pcap.CaptureGuard(private / "wire.pcap")
            capture.expect_flows(report["roles"])
            actual_wire = capture.sample(final=True, capture_write_errors_absent=True, capture_stopped=True)
            assert actual_wire == report["wire"]
            observer = peer.Observer()
            guard = report["observer"]["wire_guard"]
            observer.arm_wire_guard(guard["run_id"], SOURCE, gdb.ELF_SHA, guard["evidence_sha256"], inputs_sha256=guard["inputs_sha256"])
            slow = next(x for x in report["roles"] if x["role"] == "slow")
            bound = peer.Binding(**report["observer"]["binding"])
            observer.bind(bound, guest_tuple=slow["guest_tuple"])
            events_path = private / "gdb-observer/events.jsonl"
            raw_path = private / "gdb-observer/raw-mi.log"
            assert events_path.stat().st_size <= 4 * 1024 * 1024 and raw_path.stat().st_size <= 4 * 1024 * 1024
            events = [json.loads(line) for line in events_path.read_text().splitlines()]
            raw = raw_path.read_bytes()
            emitted = [x for x in events if x.get("origin") == "root-gdb-send-frame"]
            machine = gdb.FrameMachine(slow["guest_fd"], slow["pcb"], slow["guest_tuple"])
            replayed = []
            for event in events:
                if event.get("kind") == "sample":
                    replayed.extend(machine.consume(event["site"], event))
            assert len(replayed) == len(emitted)
            for generated, event in zip(replayed, emitted):
                assert all(event[k] == v for k, v in generated.items())
                length = event["evidence_prefix_bytes"]
                assert type(length) is int and 0 < length <= len(raw)
                assert hashlib.sha256(raw[:length]).hexdigest() == event["evidence_sha256"]
                assert event["inputs_sha256"] == report["inputs_sha256"]
                observer.submit(event)
            assert len(emitted) == (2 if mode == "withheld" else 1 if mode == "read-resume" else 0)
            if mode == "withheld":
                assert machine.state == "PROJECT_TIMEOUT_WITNESSED"
            observer.connections_closed.set()
            observer.submit(integration.wire_event(bound, actual_wire, True, guest_tuple=slow["guest_tuple"]))
            rechecked = peer.finish_report(dict(report["peer"]), observer)
            assert rechecked["state"] == "PASS"
            assert observer.snapshot()["pressure"] == report["observer"]["pressure"]
            assert observer.snapshot()["timeout"] == report["observer"]["timeout"]
            row = dict(transport=transport, mode=mode, state="PASS", report=pin(directory / "pressure.json"),
                host=pin(directory / "host.json"), inputs=pin(directory / "pressure-inputs.json"),
                elapsed_seconds=report["elapsed_seconds"], commands=report["peer"]["commands_completed"],
                unique_server_tcp_payload=actual_wire["unique_tcp_payload_bytes"],
                pressure=observer.snapshot()["pressure"], timeout=observer.snapshot()["timeout"],
                peer_termination=report["peer"]["slow_termination_kind"],
                guest_terminal=observer.snapshot()["wire"]["selected_slow_terminal"],
                minimum_heap=report["post_close_health"]["minimum_heap"], final_allocation_failures=0,
                source_sample_replay_and_raw_MI_prefix_hashes=True, final_pcap_redecoded=True,
                actual_events=pin(events_path), raw_MI=pin(raw_path), raw_pcap=pin(private / "wire.pcap"))
            result["pressure_runs"].append(row)
    assert len(result["pressure_runs"]) == 6
    result.update(all_passed=True, combined_defined_case_coverage_per_transport=85,
                  original_raw_matrix_reclassified=False, whole_service_stop_join_exercised=False)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(state="VERIFIED_PASS", transports=2, companion_runs=6,
                          covered_defined_cases_per_transport=85, original_outcomes_unchanged=True)))


if __name__ == "__main__":
    main()
