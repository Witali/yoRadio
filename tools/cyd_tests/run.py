"""CYD playback acceptance. Never install firmware, reboot or open a serial port."""
import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cyd_tests.common import Failure, Report, cyd_fixtures, digest, load_artifact, require
from tools.cyd_tests.health import HealthBoard, check_health, failure_snapshot, playback_window
from tools.esp32c3_tests.common import (check_natural_eof, check_playback, check_recovery_heap,
                                       check_transitions, exception_details)
from tools.esp32c3_tests.run import Suite
from tools.audio_test_server.server import Server
from tools.audio_test_server.fixtures import SEQUENCES

SUITES = ('http', 'https', 'eof', 'transitions', 'stop', 'switch', 'load', 'soak', 'websocket')
FINITE_CODECS = ('aac', 'mp3', 'flac', 'ogg', 'vorbis', 'opus')


def delivery_evidence(events, name, spec, *, tls=False):
    require(len(events) == 1 and events[0].get('fixture') == name and
            events[0].get('mode') == 'file' and events[0].get('complete') is True and
            type(events[0].get('sent')) is int and events[0]['sent'] == len(spec['data']) and
            events[0].get('pacing_ratio') == 1.0, 'Incomplete or mismatched controlled fixture delivery')
    result = dict(sent=events[0]['sent'], complete=True, fixture_sha256=spec['sha256'])
    if tls:
        require(events[0].get('tls_version') in ('TLSv1.2', 'TLSv1.3') and
                type(events[0].get('tls_cipher')) is str and 0 < len(events[0]['tls_cipher']) <= 80,
                'Missing negotiated HTTPS fixture evidence')
        result.update(tls_version=events[0]['tls_version'], tls_cipher=events[0]['tls_cipher'])
    return result


class CydSuite(Suite):
    """Common HTTP fixture/observation loops with native CYD health gates."""
    def __init__(self, board, origin, specs, output, *, clock=None, require_cpu=False):
        super().__init__(board, origin, specs, None, output, clock=clock)
        self.require_cpu = require_cpu

    def positive(self, name, *, hint='auto', origin=None, terminal=True):
        start = len(self.board.health_samples)
        self.start(name, hint=hint, origin=origin)
        first = len(self.board.health_samples)
        states = self.observe(max(7, self.specs[name]['seconds']-3), name)
        result = check_playback(states, self.specs[name])
        result['output'] = playback_window(states, self.board.health_samples[first:])
        if terminal:
            tail = self.observe(10, name+':eof')
            result['eof'] = check_natural_eof(tail)
            require(all(not s['pcm_sample_rate'] and not s['pcm_channels'] for s in tail[-3:]),
                    'CYD EOF retained stale PCM metadata')
        check_health(self.board.health_samples[start:])
        return result

    def transitions(self, name):
        expected = self.specs[name].get('sequence')
        require(expected and all(n in self.specs for n in expected), 'Missing fixture transition sequence')
        self.start(name, hint=self.specs[name]['codec'])
        first = len(self.board.health_samples)
        states = self.observe(self.specs[name]['seconds']-1, name)
        check_transitions(states, [self.specs[n] for n in expected])
        output = playback_window(states, self.board.health_samples[first:])
        return dict(sequence=expected, output=output)

    def stopped(self, name='stopped'):
        first = len(self.board.health_samples)
        self.board.stop()
        states = self.observe(4, name, interval=1)
        require(len(states) >= 3 and all(not s['audio'] and not s['connecting'] for s in states[-3:]),
                'CYD Stop was not confirmed')
        rows = self.board.health_samples[first:]
        check_health(rows)
        return dict(samples=rows[-3:])

    def switching(self, names, cycles):
        require(cycles >= 3, 'At least three switch cycles are required')
        previous, completed = None, 0
        for cycle in range(cycles):
            for name in names:
                self.start(name, hint=self.specs[name]['codec'])
                first = len(self.board.health_samples)
                states = self.observe(7, 'switch:'+str(cycle)+':'+name)
                check_playback(states, self.specs[name])
                playback_window(states, self.board.health_samples[first:])
                generations = {s['generation'] for s in states if s['audio']}
                require(len(generations) == 1 and previous not in generations, 'Stale CYD switch generation')
                previous = next(iter(generations))
                completed += 1
        return dict(cycles=cycles, changes=completed)

    def sustained(self, seconds, name, *, load=False, origin=None):
        spec = self.specs[name]
        mode = 'stream' if spec['codec'] == 'aac' else 'file'
        require(mode == 'stream' or spec['seconds'] >= seconds+3,
                'Finite sustained fixture must outlast the observation by three seconds')
        self.start(name, mode, spec['codec'], origin)
        first = len(self.board.health_samples)
        states = self.observe(seconds, ('load:' if load else 'soak:')+name, interval=.1 if load else 1)
        warmup = 15 if self.require_cpu else 5
        check_playback(states, spec, minimum=max(5, int((seconds-warmup)*.6)), warmup=warmup)
        require(states[-1]['seconds'] >= seconds-2 and
                all(b['seconds']-a['seconds'] < 3 for a, b in zip(states, states[1:])),
                'Incomplete CYD sustained observation')
        require(max(s['request_ms'] for s in states) < 2000, 'CYD status/health response exceeded two seconds')
        output = playback_window(states, self.board.health_samples[first:], warmup=warmup,
                                 minimum=max(5, int((seconds-warmup)*.6)), require_cpu=self.require_cpu)
        rows = self.board.health_samples[first:]
        selected = [h for s, h in zip(states, rows) if s['seconds'] >= warmup]
        check_recovery_heap(selected[:3], selected[-3:])
        return dict(seconds=seconds, status_samples=len(states), output=output,
                    maximum_status_health_ms=max(s['request_ms'] for s in states))


def acceptance(args, *, board_factory=HealthBoard, server_factory=Server,
               fixture_loader=cyd_fixtures, clock=None):
    """Dependency seams are explicit; offline tests supply no real transports."""
    out = args.output.resolve()
    require(not out.exists(), 'Choose a fresh acceptance output')
    out.mkdir(parents=True)
    report = Report(out/'report.json', {})
    report.data.update(scope='CYD sampled playback/status/health and recovery; no analog/IRQ/OTA qualification',
                       passed=False, backend=args.backend, requested_suites=args.suite,
                       deployment=False, reboot=False, serial_capture=False, physical_acceptance_complete=False,
                       watchdog_counter_available=False, driver_counter_units='backend buffer bytes; includes idle/prime',
                       cpu_required=args.require_cpu)
    for directory in (ROOT/'tools/cyd_tests',):
        report.data['test_sources_sha256'].update({p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                                                  for p in directory.glob('*.py')})
    parser_source = ROOT/'tools/export_cyd_production.py'
    report.data['test_sources_sha256'][parser_source.relative_to(ROOT).as_posix()] = digest(parser_source.read_bytes())
    board = suite = None
    admitted = False
    primary_interruption = None

    def save():
        if board is not None:
            (out/'health.json').write_text(json.dumps(board.health_samples, indent=2)+'\n', encoding='utf-8')
        report.save()

    def error_fields(error):
        result = dict(type=type(error).__name__, exception_chain=exception_details(error))
        if isinstance(error, Failure):
            result['reason'] = str(error)
        if not isinstance(error, Exception):
            result['interrupted'] = True
        return result

    def remember_interruption(error, location):
        nonlocal primary_interruption
        if not isinstance(error, Exception):
            if primary_interruption is None:
                primary_interruption = error
            report.data.setdefault('controller_error', dict(location=location, **error_fields(error)))

    def snapshot(name):
        if board is not None and admitted:
            try:
                report.data.setdefault('failure_snapshots', {})[name] = failure_snapshot(board)
            except BaseException as error:
                # Diagnostics cannot erase the already durable primary failure.
                report.data.setdefault('snapshot_errors', {})[name] = error_fields(error)
                remember_interruption(error, name+':snapshot')
            save()

    def case(name, action, *, cleanup=False):
        started = time.perf_counter()
        record = dict(name=name, result='RUNNING')
        report.data['cases'].append(record)
        save()
        try:
            record['evidence'] = action()
            record['result'] = 'PASS'
        except BaseException as error:
            record.update(result='FAIL', **error_fields(error))
            remember_interruption(error, name)
            record['seconds'] = round(time.perf_counter()-started, 3)
            save()  # Persist failure/interrupt and partial samples BEFORE diagnostics or Stop.
            snapshot(name)
            if primary_interruption is not None and not cleanup:
                raise primary_interruption
        finally:
            record['seconds'] = round(time.perf_counter()-started, 3)
            save()
            print(name+': '+record['result'], flush=True)
        return record['result'] == 'PASS'

    try:
        artifact = load_artifact(args.firmware, args.backend)
        require(args.suite and len(set(args.suite)) == len(args.suite) and all(s in SUITES for s in args.suite),
                'Select distinct supported CYD suites')
        require('switch' not in args.suite or args.cycles >= 3, 'At least three switch cycles are required')
        require(args.load_seconds >= 40 and args.soak_seconds >= 60, 'Keep minimum load/soak windows')
        require(not args.require_cpu or artifact.diagnostics and any(s in args.suite for s in ('load', 'soak')),
                'CPU acceptance requires diagnostic firmware and a sustained suite')
        report.data['artifact'] = artifact.evidence
        specs = fixture_loader(args.fixture_manifest)
        names = args.case or [n for n, s in specs.items() if s['codec'] in FINITE_CODECS and n not in SEQUENCES]
        require(names and len(set(names)) == len(names) and all(n in specs and 'rate' in specs[n] and
                specs[n]['codec'] in FINITE_CODECS for n in names), 'Select known finite public-codec fixtures')
        require(not any(s in args.suite for s in ('load', 'soak')) or len(names) == 1,
                'Select one sustained fixture explicitly')
        require(not any(s in args.suite for s in ('https',)) or
                args.https_origin and args.tls_cert and args.tls_key, 'HTTPS requires the controlled TLS fixture server')
        if 'https' in args.suite:
            parsed = urlsplit(args.https_origin)
            require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and
                    not parsed.password and parsed.path in ('', '/') and not parsed.query and
                    not parsed.fragment and (parsed.port or 443) == args.tls_port,
                    'HTTPS origin must name the controlled TLS server port')
            require(args.tls_cert.is_file() and args.tls_key.is_file(), 'Controlled TLS certificate/key missing')
        report.data.update(fixture_hashes={n: specs[n]['sha256'] for n in names},
                           pacing_ratio=1.0, public_profile_tags_claimed=False)
        board = board_factory(args.board, artifact)
        report.data['board'] = board.authorize()
        initial = board.status()
        require(not initial['audio'] and not initial['connecting'], 'Do not interrupt unrelated active playback')
        before = board.settings()  # Never serialized, hashed or sent back.
        admitted = True
        suite = CydSuite(board, f'http://{args.host}:{args.port}', specs, out, clock=clock,
                         require_cpu=args.require_cpu)
        initial_idle = suite.stopped('initial-idle')['samples']
        report.data['initial_status'] = initial
        with ExitStack() as stack:
            server = stack.enter_context(server_factory(args.host, args.port, specs, pacing_ratio=1.0, delivery_stats=True))
            tls = None
            if 'https' in args.suite:
                require(args.https_origin.startswith('https://'), 'HTTPS fixture origin required')
                tls = stack.enter_context(server_factory(args.host, args.tls_port, specs, args.tls_cert,
                                                        args.tls_key, pacing_ratio=1.0, delivery_stats=True))
                report.data['leaf_certificate_sha256'] = digest(args.tls_cert.read_bytes())
            try:
                for protocol in ('http', 'https'):
                    if protocol in args.suite:
                        for name in names:
                            for hint in ('auto', specs[name]['codec']):
                                def file_case(n=name, p=protocol, h=hint):
                                    selected_server = tls if p == 'https' else server
                                    first = len(selected_server.events)
                                    result = suite.positive(n, hint=h, origin=args.https_origin if p == 'https' else None)
                                    result['delivery'] = delivery_evidence(selected_server.events[first:], n, specs[n], tls=p == 'https')
                                    return result
                                case(protocol+':'+name+':'+hint, file_case)
                if 'eof' in args.suite:
                    for name in names:
                        for hint in ('auto', specs[name]['codec']):
                            case('eof:'+name+':'+hint, lambda n=name, h=hint: suite.positive(n, hint=h))
                if 'transitions' in args.suite:
                    for name in SEQUENCES:
                        case('transition:'+name, lambda n=name: suite.transitions(n))
                if 'stop' in args.suite:
                    def stop_play():
                        suite.positive(names[0], terminal=False)
                        return suite.stopped('explicit-stop')
                    case('stop-after-playback', stop_play)
                if 'switch' in args.suite:
                    case('switch', lambda: suite.switching(names, args.cycles))
                for kind, seconds in (('load', args.load_seconds), ('soak', args.soak_seconds)):
                    if kind in args.suite:
                        case(kind+':'+names[0], lambda k=kind, n=names[0], duration=seconds:
                             suite.sustained(duration, n, load=k == 'load'))
                if 'websocket' in args.suite:
                    def websocket():
                        suite.start(names[0], hint=specs[names[0]]['codec'])
                        first = len(board.health_samples)
                        states = suite.observe(7, 'websocket-warmup')
                        check_playback(states, specs[names[0]])
                        playback_window(states, board.health_samples[first:])
                        with board.websocket() as ws:
                            ws.send('getindex')
                            for _ in range(12):
                                message = json.loads(ws.recv(timeout=5))
                                values = {p['id']: p['value'] for p in message.get('payload', [])}
                                if 'fmt' in values:
                                    require(values['fmt'] == board.status()['format'] and values.get('playerwrap') == 'playing',
                                            'CYD WebSocket snapshot is stale')
                                    return dict(snapshot_matches=True)
                            raise Failure('Missing CYD WebSocket snapshot')
                    case('websocket', websocket)
                # Stop while the controlled source still exists, so normal
                # server teardown cannot manufacture an input failure.
                if case('final-idle', lambda: suite.stopped('final-idle')):
                    case('settled-recovery', lambda: check_recovery_heap(initial_idle, board.health_samples[-3:]))
                case('settings-unchanged', lambda: require(board.settings() == before, 'CYD settings changed during playback acceptance'))
                case('identity-unchanged', board.check_identity)
            finally:
                report.data['server_events'] = server.events
                if tls is not None:
                    report.data['tls_events'] = tls.events
    except BaseException as error:
        remember_interruption(error, 'controller')
        report.data.setdefault('controller_error', error_fields(error))
        save()  # A cancellation during preflight/between cases is durable too.
        snapshot('controller')
    finally:
        if admitted and board is not None:
            case('cleanup-stop', lambda: suite.stopped('cleanup-idle') if suite else board.stop(), cleanup=True)
        report.data['passed'] = (primary_interruption is None and bool(report.data['cases']) and 'controller_error' not in report.data and
                                all(row['result'] == 'PASS' for row in report.data['cases']))
        save()
    if isinstance(primary_interruption, KeyboardInterrupt):
        return 130
    # SystemExit(0), GeneratorExit and interruptions in cleanup also fail closed.
    return 0 if report.data['passed'] else 1


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--board', required=True)
    p.add_argument('--host', required=True)
    p.add_argument('--backend', choices=('pdm', 'continuous', 'legacy'), required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--suite', action='append', choices=SUITES, required=True)
    p.add_argument('--case', action='append')
    p.add_argument('--fixture-manifest', type=Path)
    p.add_argument('--port', type=int, default=8770)
    p.add_argument('--https-origin')
    p.add_argument('--tls-port', type=int, default=8771)
    p.add_argument('--tls-cert', type=Path)
    p.add_argument('--tls-key', type=Path)
    p.add_argument('--cycles', type=int, default=3)
    p.add_argument('--load-seconds', type=int, default=40)
    p.add_argument('--soak-seconds', type=int, default=600)
    p.add_argument('--require-cpu', action='store_true')
    return p


def main(argv=None, **dependencies):
    args = parser().parse_args(argv)
    require(args.load_seconds >= 40 and args.soak_seconds >= 60, 'Keep minimum load/soak windows')
    return acceptance(args, **dependencies)


if __name__ == '__main__':
    raise SystemExit(main())
