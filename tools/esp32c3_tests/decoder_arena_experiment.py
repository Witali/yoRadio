"""App-only OTA comparison of shared decoder arena; always restore original app.

Uses synthetic, board-independent fixtures. Settings and original station stay
in memory only. This measures allocation lifetimes and output health, not PCM
bit equivalence or analog continuity. Existing acceptance gates are unchanged.
"""
import argparse
import json
from pathlib import Path
import time
import subprocess

from common import Board, Failure, check_playback, exception_details, fixtures, require, sha
from ota import image_info, multipart, snapshot, upload, verify_snapshot, wait_image
from production_health import HealthBoard, check_health, read_health
from sustained_output import check_output, check_memory
from run import Suite, Capture
from audio_test_server.server import Server, pause_argument

ARENA_FIELDS = ('capacity', 'live', 'peak', 'blocks', 'free', 'largest', 'failures')

class ArenaBoard(HealthBoard):
    def __init__(self, origin, collect_after_fault=False):
        super().__init__(origin)
        self.collect_after_fault = collect_after_fault
        self.arenas = []
        self.timings = []
        self.inputs = []

    def json(self, path, data=None, timeout=5):
        response = super().json(path, data, timeout)
        if path != '/api/native/health': return response
        raw = response.get('decoder_arena')
        if raw is not None:
            require(isinstance(raw, dict) and all(type(raw.get(k)) is int and raw[k] >= 0
                    for k in ARENA_FIELDS), 'Invalid arena telemetry')
            raw = {k: raw[k] for k in ARENA_FIELDS}
            require(raw['live'] <= raw['peak'] <= raw['capacity'] and
                    raw['largest'] <= raw['free'] <= raw['capacity'], 'Inconsistent arena counters')
        self.latest_arena = raw
        timing = response.get('arena_timing')
        if timing is not None:
            require(type(timing) is dict and all(type(timing.get(k)) is list and
                    len(timing[k]) == 2 and all(type(v) is int and 0 <= v < 2**32 for v in timing[k])
                    for k in ('malloc', 'free', 'realloc', 'snapshot')), 'Invalid arena timing')
            timing = {k: timing[k] for k in ('malloc', 'free', 'realloc', 'snapshot')}
        self.latest_timing = timing
        queue = response.get('input_queue')
        if queue is not None:
            keys = ('resident', 'occupied', 'minimum', 'limit', 'packet_capacity')
            require(type(queue) is dict and all(type(queue.get(k)) is int and queue[k] >= 0
                    for k in keys), 'Invalid input queue diagnostic')
            queue = {k: queue[k] for k in keys}
            require(queue['occupied'] <= queue['resident'], 'Inconsistent input queue occupancy')
        self.latest_input = queue
        return response

    def status(self):
        if self.collect_after_fault:
            # Diagnostic collection only: retain actual fault counters. All
            # acceptance gates below still reject these faulty measurements.
            state = Board.status(self)
            started = time.perf_counter()
            health = read_health(self)
            self.health_samples.append(dict(at=time.perf_counter(),
                request_ms=(time.perf_counter()-started)*1000, **health))
            check_health([dict(h, allocation_failures=0, task_watchdog_events=0)
                          for h in (self.health_samples[0], *self.health_samples[-2:])])
        else:
            state = super().status()
        self.arenas.append(self.latest_arena)
        self.timings.append(self.latest_timing)
        self.inputs.append(self.latest_input)
        return state

class ObservedSuite(Suite):
    """Keep transient network failures as failed evidence without discarding a run."""
    def observe(self, seconds, name, interval=.4):
        start = time.perf_counter()
        batch = dict(case=name, started_at=start, samples=[], errors=[])
        try:
            while time.perf_counter() - start < seconds:
                requested = time.perf_counter()
                try:
                    state = self.board.status()
                    batch['samples'].append(dict(seconds=time.perf_counter()-start,
                        request_ms=(time.perf_counter()-requested)*1000, **state))
                except (OSError, TimeoutError) as error:
                    batch['errors'].append(dict(seconds=time.perf_counter()-start,
                        exception_chain=exception_details(error)))
                time.sleep(interval)
        finally:
            batch['ended_at'] = time.perf_counter()
            self.observations.append(batch)
            (self.output / 'status.json').write_text(json.dumps(self.observations, indent=2)+'\n')
        return batch['samples']

def evaluate(function):
    try:
        return dict(result='PASS', evidence=function())
    except Failure as error:
        return dict(result='FAIL', reason=str(error))

def check_transition_memory(rows):
    # An intentional LC -> SBR/PS change increases live codec storage. A
    # first/last trend test describes that growth, not a leak. Retain the same
    # absolute headroom/fault gates; measure reclamation separately at Stop.
    result = check_health(rows)
    require(result['minimum_heap'] >= 16384 and result['minimum_largest'] >= 8192,
            'Heap headroom below budget during format transition')
    return result

def arena_check(rows, idle, failures_before=0):
    require(rows and all(r is not None for r in rows), 'Missing arena telemetry')
    require(max(r['live'] for r in rows) > 0, 'Decoder did not use arena')
    require(all(r and r['failures'] == failures_before for r in rows + idle), 'Arena allocation failed')
    require(idle and all(r and r['live'] == 0 and r['blocks'] == 0 for r in idle[-3:]),
            'Stop retained arena allocations')
    return dict(peak=max(r['peak'] for r in rows), maximum_live=max(r['live'] for r in rows))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--port', type=int, default=8772)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--restore', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    phase = p.add_mutually_exclusive_group()
    phase.add_argument('--candidate-only', action='store_true')
    phase.add_argument('--baseline-only', action='store_true')
    p.add_argument('--resume-candidate', action='store_true', help='Resume after an independently verified USB recovery')
    p.add_argument('--recovery-port', help='Optional native C3 USB watchdog recovery after a failed OTA boot check')
    p.add_argument('--cases', nargs='+')
    p.add_argument('--repeat', type=int, default=1, help='Repeat each fixture, retaining every trial')
    p.add_argument('--collect-after-fault', action='store_true',
                   help='Keep collecting diagnostics after fault counters; acceptance still FAILS')
    p.add_argument('--delivery-pause', type=pause_argument, action='append', default=[],
                   help='Inject a host delivery pause at BYTE_OFFSET:SECONDS (diagnosis, not qualification)')
    p.add_argument('--https-url', help='Optional public HE-AAC reference stream; not stored in reports')
    p.add_argument('--https-seconds', type=int, default=60)
    a = p.parse_args()
    require(1 <= a.repeat <= 100, 'Repeat must be within 1..100')
    require(not a.https_url or a.https_seconds >= 45, 'HTTPS observation must last at least 45 seconds')
    a.output.mkdir(parents=True, exist_ok=False)
    (a.output / 'controller-used.py').write_bytes(Path(__file__).read_bytes())
    def save(name, data):
        (a.output / name).write_text(json.dumps(data, indent=2) + '\n')
    board = Board(a.board)
    restored_image = image_info(a.restore.read_bytes())
    allowed = [restored_image['app_elf_sha256']]
    if a.resume_candidate:
        allowed.append(image_info(a.candidate.read_bytes())['app_elf_sha256'])
    require(board.info()['app_elf_sha256'] in allowed,
            'Restore image does not match initial application')
    original = board.status()
    station = board.json('/api/native/status')['station']
    with board.websocket() as ws:
        ws.send('getindex')
        current = None
        deadline = time.perf_counter() + 5
        while time.perf_counter() < deadline:
            message = json.loads(ws.recv(timeout=5))
            if 'current' in message:
                current = message['current']; break
    require(type(current) is int and current > 0, 'Cannot restore station')
    settings = snapshot(board)
    specs = fixtures()
    names = a.cases or list(specs)
    require(all(n in specs for n in names), 'Unknown fixture')
    save('initial.json', dict(original=original, restore=restored_image,
         candidate=image_info(a.candidate.read_bytes()), baseline=image_info(a.baseline.read_bytes()),
         controller_sha256=sha(Path(__file__).read_bytes()),
         repeat=a.repeat, delivery_pauses=a.delivery_pause, collect_after_fault=a.collect_after_fault,
         fixtures={n:{k:v for k,v in specs[n].items() if k not in ('data', 'segments')} for n in names}))
    def install(path):
        raw = path.read_bytes()
        expected = image_info(raw)
        active = board.info()
        if active['app_elf_sha256'] == expected['app_elf_sha256']:
            return active
        require(len(raw) <= active['max_size'], 'Image exceeds OTA slot')
        board.stop()
        target = 'app1' if active['partition'] == 'app0' else 'app0'
        code, body = upload(board.origin, multipart(raw))
        require(code == 200 and body == b'OK', 'OTA failed')
        try:
            return wait_image(board, expected['app_elf_sha256'], target, timeout=60)
        except Failure:
            save('ota-boot-check-failed-' + expected['app_elf_sha256'][:12] + '.json',
                 dict(expected=expected, result='FAIL', recovery_port=a.recovery_port))
            if not a.recovery_port:
                raise
            script = Path(__file__).resolve().parents[2] / '.agents/skills/flash-reset-esp32c3-oled/scripts/reset_esp32c3_oled.ps1'
            subprocess.run(['powershell.exe', '-NoProfile', '-File', str(script),
                '-Port', a.recovery_port, '-VerifyUrl', board.origin + '/'], check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
            return wait_image(board, expected['app_elf_sha256'], target, timeout=30)
    phases = [('baseline', a.baseline), ('candidate', a.candidate)]
    if a.candidate_only: phases = phases[1:]
    if a.baseline_only: phases = phases[:1]
    results = {}
    b = None
    try:
        with Server(a.host, a.port, specs, pacing_ratio=1.0, delivery_stats=True,
                    delivery_pauses=a.delivery_pause) as server:
            for label, app in phases:
                print('INSTALL', label, flush=True)
                save(label + '-installed.json', dict(identity=install(app),
                     persistence=verify_snapshot(board, settings)))
                b = ArenaBoard(a.board, a.collect_after_fault)
                suite = ObservedSuite(b, f'http://{a.host}:{a.port}', specs, Capture(None), a.output / label)
                b.stop(); suite.observe(4, 'idle')
                for name, trial in ((n, t) for n in names for t in range(1, a.repeat + 1)):
                    case = name if a.repeat == 1 else f'{name}:trial-{trial}'
                    print(label, case, flush=True)
                    begin = len(b.health_samples)
                    failures_before = b.arenas[-1]['failures'] if b.arenas[-1] else 0
                    suite.start(name)
                    states = suite.observe(max(7, specs[name]['seconds'] - 3), case)
                    end = len(b.health_samples)
                    if name in ('changing', 'implicit-sbr'):
                        from common import check_transitions
                        from audio_test_server.fixtures import SEQUENCES
                        format_check = lambda: check_transitions(states, [specs[n] for n in SEQUENCES[name]])
                        memory_check = check_transition_memory
                    else:
                        format_check = lambda: check_playback(states, specs[name])
                        memory_check = check_memory
                    steady = [h for s,h in zip(states,b.health_samples[begin:end]) if s['seconds'] >= 3]
                    tail = suite.observe(8, case + ':eof')
                    b.stop(); idle_start = len(b.arenas)
                    suite.observe(4, case + ':stop')
                    key = label + ':' + case
                    results[key] = dict(format=evaluate(format_check), output=evaluate(lambda:check_output(steady)),
                        memory=evaluate(lambda:memory_check(steady)),
                        eof=dict(result='PASS' if any(not s['audio'] for s in tail) else 'FAIL'))
                    errors = [e for batch in suite.observations[-3:] for e in batch['errors']]
                    results[key]['transport'] = dict(result='FAIL' if errors else 'PASS', errors=errors)
                    if label == 'candidate':
                        results[key]['arena'] = evaluate(lambda:arena_check(b.arenas[begin:end], b.arenas[idle_start:], failures_before))
                    save('results.json', results)
                    save(label + '-health.json', b.health_samples)
                    save(label + '-arena.json', b.arenas)
                    save(label + '-timing.json', b.timings)
                    save(label + '-input.json', b.inputs)
                    save('server.json', server.events)
                    print(key, {k:v['result'] for k,v in results[key].items()}, flush=True)
                save(label + '-health-check.json', evaluate(lambda:check_health(b.health_samples)))
                if a.https_url:
                    print(label, 'HTTPS HE-AAC', flush=True)
                    from public_streams import probe
                    reference = probe(a.https_url, 'ffprobe')
                    save(label + '-https-reference.json', reference)
                    b.stop(); time.sleep(1)
                    begin = len(b.health_samples)
                    failures_before = b.arenas[-1]['failures'] if b.arenas[-1] else 0
                    b.play(a.https_url)
                    states = suite.observe(a.https_seconds, 'https-he-aac')
                    end = len(b.health_samples)
                    steady = [h for s,h in zip(states,b.health_samples[begin:end]) if s['seconds'] >= 15]
                    b.stop(); idle_start = len(b.arenas); suite.observe(5, 'https-stop')
                    key = label + ':https-he-aac'
                    results[key] = dict(output=evaluate(lambda:check_output(steady)),
                        memory=evaluate(lambda:check_memory(steady)),
                        format=evaluate(lambda:check_playback(states, reference['spec'], minimum=20, warmup=15)))
                    errors = [e for batch in suite.observations[-2:] for e in batch['errors']]
                    results[key]['transport'] = dict(result='FAIL' if errors else 'PASS', errors=errors)
                    if label == 'candidate':
                        results[key]['arena'] = evaluate(lambda:arena_check(b.arenas[begin:end], b.arenas[idle_start:], failures_before))
                    save('results.json', results)
                    save(label + '-health.json', b.health_samples)
                    save(label + '-arena.json', b.arenas)
                    print(key, {k:v['result'] for k,v in results[key].items()}, flush=True)
            save('summary.json', dict(result='PASS' if all(v['result']=='PASS'
                 for row in results.values() for v in row.values()) else 'FAIL', cases=len(results)))
    except Exception as error:
        if b is not None:
            # HealthBoard retains the offending row before raising. Preserve
            # it even when the first idle observation after OTA fails.
            save(label + '-health.json', b.health_samples)
            save(label + '-arena.json', b.arenas)
            save(label + '-timing.json', b.timings)
            save(label + '-input.json', b.inputs)
        save('controller-failure.json', dict(exception_chain=exception_details(error)))
        raise
    finally:
        print('RESTORE original app/settings/station', flush=True)
        try:
            identity = install(a.restore)
            board.stop()
            if original['audio']:
                with board.websocket() as ws:
                    ws.send('play=' + str(current))
                    time.sleep(1)
            b = HealthBoard(a.board)
            states = []
            for _ in range(5):
                time.sleep(4); states.append(b.status())
            same_station = board.json('/api/native/status')['station'] == station if original['audio'] else True
            require(same_station and all(s['audio'] == original['audio'] for s in states[-3:]), 'Playback restore failed')
            save('restoration.json', dict(identity=identity, persistence=verify_snapshot(board, settings),
                 same_station=same_station, states=states, health=check_health(b.health_samples)))
            print('RESTORED', flush=True)
        except Exception as error:
            save('restoration-failure.json', dict(exception_chain=exception_details(error)))
            raise

if __name__ == '__main__':
    main()
