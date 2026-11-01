"""Authenticate frozen TLS observations as data; execute no archived program."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parents[2]
OUTCOMES = dict(peer01=False, peer02=True, freeze01=False, native01=False,
                native02=True, syntax01=False, syntax02=True)
FALSE_SCOPES = ('physical_hardware', 'production_sources_changed', 'production_default_activation',
                'rf_or_full_radio_qualified', 'tft_load_qualified', 'physical_headroom_qualified',
                'target_throughput_qualified', 'full_tls_conformance', 'insecure_verification',
                'user_network_restrict', 'archived_code_executed', 'omitted_payloads_read_by_verifier',
                'certificate_store_modified')
PAYLOAD_SHA = hashlib.sha256(bytes((n*73+(n >> 8)*19+11) & 255 for n in range(65536))).hexdigest()
EMPTY_SHA = hashlib.sha256(b'').hexdigest()
NORMAL = {'first', 'reopen', 'after_failures', 'parallel_a', 'parallel_b', 'pressure', 'after_pressure'}
WARNINGS = ('add mac address to filter not supported', 'failed to add mac filter',
            'Failed to add multicast filter for IPv4', 'RX frame dropped (0x14)')
MAIN = 'tests/target/cyd_tls_traffic_qemu/main/main.c'
CONTROLLER = 'tests/run-cyd-tls-traffic-qemu.py'
SOURCE_PINS = {
    MAIN: '155375d0909dcd3aec8591166957a0552929cae10c9f3b38072dee0d1f49f779',
    CONTROLLER: '1c49ff98f1e057b7c179eff8729035b4dc6cc9d627930f27d93cdc9e6944a0c0',
    'tests/target/cyd_tls_traffic_qemu/loopback_server.py': 'ae85255cb930ab5f3844bb636ae335de95ddfa1c660e88db968da2f56fd1db05',
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def normalize(path):
    return path.replace('\\', '/').lower()


def policy(manifest):
    need(manifest['schema'] == 1 and manifest['checkpoint_completed'] is True, 'completed bounded checkpoint')
    need(all(manifest[name] is False for name in FALSE_SCOPES), 'precise scope, no unpublished payload/code execution')
    need(set(manifest['campaigns']) == set(OUTCOMES), 'all seven original attempts')
    need(all(manifest['campaigns'][name]['expected_pass'] is passed for name, passed in OUTCOMES.items()),
         'all original nonpasses stay nonpass')


def server_check(events, native):
    need(events and events[0]['event'] == 'listening' and events[-1]['event'] == 'server_stopped', 'whole independent server transcript')
    first = events[0]
    need(first['host'] == '127.0.0.1' and first['ports'] == [18443, 18444, 18445] and first['payload_bytes'] == 65536 and
         first['payload_sha256'] == PAYLOAD_SHA and first['tls'] == 'TLSv1.2' and
         first['cipher'] == 'ECDHE-RSA-AES128-GCM-SHA256', 'actual local verified TLS1.2/full-record peer profile')
    need(all(a['monotonic_ns'] <= b['monotonic_ns'] for a, b in zip(events, events[1:])), 'original server event order')
    accepted = {row['connection']: row for row in events if row['event'] == 'accepted'}
    closed = [row['connection'] for row in events if row['event'] == 'connection_closed']
    need(len(accepted) == len(closed) == len(set(closed)) == (10 if native else 9) and
         set(closed) == set(accepted) and events[-1]['connections'] == len(accepted), 'every actual peer closes exactly once')
    need(Counter(row['mode'] for row in accepted.values()) == dict(normal=8 if native else 7, handshake_close=1, truncated_record=1), 'named actual endpoint modes')
    handshake = {row['connection']: row for row in events if row['event'] == 'handshake'}
    need(all(row['version'] == 'TLSv1.2' and row['cipher'] == first['cipher'] for row in handshake.values()), 'actual negotiated server protocol/cipher')
    complete = [row for row in events if row['event'] == 'response_complete']
    expected = NORMAL if native else {'first', 'reopen', 'after_failures', 'parallel_a', 'parallel_b'}
    need(len(complete) == len(expected) and {row['case'] for row in complete} == expected, 'all expected full responses, no invented failed response')
    full_records = 0
    for connection in accepted:
        records = [row for row in events if row['event'] == 'server_record' and row['connection'] == connection]
        need([row['ordinal'] for row in records] == list(range(1, len(records)+1)) and
             all(row['header_bytes'] == 5 and row['record_bytes'] > 0 for row in records), 'actual complete TLS wire-record census')
        full_records += sum(row['content_type'] == 23 and row['record_bytes'] == 16408 for row in records)
    for row in complete:
        connection = row['connection']
        need(connection in handshake and accepted[connection]['mode'] == 'normal' and row['bytes'] == 65536 and
             row['sha256'] == PAYLOAD_SHA, 'independent full response and verified handshake')
        writes = [event for event in events if event['event'] == 'plaintext_write' and event['connection'] == connection]
        records = [event for event in events if event['event'] == 'server_record' and event['connection'] == connection and event['content_type'] == 23 and event['record_bytes'] == 16408]
        need(len(writes) == len(records) == 4 and all(event['bytes'] == 16384 and event['case'] == row['case'] for event in writes),
             'four real full plaintext writes and AES-GCM records for every response')
    need(full_records == (28 if native else 20), 'exact full-record census, no metadata-only substitution')
    rounds = [row for row in events if row['event'] == 'parallel_round']
    ready = [row for row in events if row['event'] == 'parallel_ready']
    need(len(ready) == 2 and {row['case'] for row in ready} == {'parallel_a', 'parallel_b'} and
         [row['round'] for row in rounds] == [0, 0, 1, 1, 2, 2, 3, 3] and
         len({row['connection'] for row in rounds}) == 2, 'two live TLS peers with actual synchronized traffic')
    need(max(row['monotonic_ns'] for row in ready) <= min(row['monotonic_ns'] for row in rounds), 'both peer requests exist before parallel traffic starts')
    for round_number in range(4):
        need({row['case'] for row in rounds if row['round'] == round_number} == {'parallel_a', 'parallel_b'}, 'both peers participate in every round')
    stopped = [row for row in events if row['event'] == 'handshake_closed']
    truncated = [row for row in events if row['event'] == 'record_truncated']
    need(len(stopped) == len(truncated) == 1 and stopped[0]['received_bytes'] >= 5 and
         accepted[stopped[0]['connection']]['mode'] == 'handshake_close', 'real client hello before explicit handshake closure')
    need(truncated[0]['advertised_record_bytes'] == 16408 and truncated[0]['sent_wire_bytes'] == 8209 and
         accepted[truncated[0]['connection']]['mode'] == 'truncated_record' and truncated[0]['connection'] in handshake,
         'actual half-sent application record after a successful TLS handshake')
    bad = [row for row in events if row['event'] == 'peer_error']
    need(len(bad) == (1 if native else 2) and all(row['error_type'] == 'SSLError' and 'ALERT' in row['reason'] for row in bad),
         'independent certificate-rejection peer alerts, no generic server failure accepted')
    return dict(complete_responses=len(complete), full_records=full_records, live_clients=2)


def guest_check(log, static_rx):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|TLS_TRAFFIC_FAILURE', log, re.I), 'no panic/refusal interpreted as success')
    need(log.count('TLS_EARLY_MPI calls=1 core=0') == 1 and log.count('TLS_NETWORK openeth=1 synthetic_host=10.0.2.2 tls_ports=18443,18444,18445') == 1,
         'actual early MPI helper and explicit synthetic network')
    need(all(log.count(warning) == 1 for warning in WARNINGS), 'all original multicast-filter/drop diagnostics retained, no warning suppression')
    active, attached, opens, data = {}, set(), {}, {}
    allocations = frees = attaches = static_loans = pressure_events = parallel_events = 0
    handshake_error = None
    for line in log.splitlines():
        match = re.search(r'mbedtls_ssl_handshake returned -0x([0-9a-f]+)', line)
        if match:
            need(handshake_error is None, 'one named handshake error before its open result')
            handshake_error = int(match[1], 16)
        if line.startswith('TLS_ATTACH '):
            match = re.fullmatch(r'TLS_ATTACH cfg=(0x[0-9a-f]+) result=(-?\d+)', line)
            need(match is not None and int(match[2]) == 0, 'actual original bundle attach succeeds')
            attached.add(int(match[1], 16)); attaches += 1
        elif line.startswith('TLS_RX_ALLOC '):
            match = re.fullmatch(r'TLS_RX_ALLOC core=([01]) cfg=(0x[0-9a-f]+) ptr=(0x[0-9a-f]+) count=(\d+) bytes=(\d+)', line)
            need(match is not None, 'whole actual RX allocation record')
            core, cfg, pointer, count, size = int(match[1]), int(match[2], 16), int(match[3], 16), int(match[4]), int(match[5])
            need(cfg in attached and pointer not in active and count == 1 and size == static_rx['bytes'] == 16717,
                 'full SDK RX capacity, registered eligible configuration, exclusive pointer loan')
            active[pointer] = dict(core=core, cfg=cfg, case=None)
            allocations += 1; static_loans += pointer == static_rx['address']
        elif line.startswith('TLS_OPEN '):
            match = re.fullmatch(r'TLS_OPEN case=(\w+) core=([01]) status=(-?\d+) ptr=(0x[0-9a-f]+)', line)
            need(match is not None, 'whole actual public TLS open record')
            label, core, status, pointer = match[1], int(match[2]), int(match[3]), int(match[4], 16)
            need(label not in opens and pointer in active and active[pointer]['core'] == core, 'open retains its actual live RX owner')
            if label in ('wrong_name', 'handshake_close'):
                need(status == -1 and handshake_error == (0x2700 if label == 'wrong_name' else 0x7280), 'exact original X509/peer-EOF failure, no unrelated refusal')
            else:
                need(label in NORMAL | {'truncated_record'} and status == 1 and handshake_error is None, 'genuine positive verified TLS connection')
            handshake_error = None
            opens[label] = dict(core=core, status=status, pointer=pointer)
            active[pointer]['case'] = label
        elif line.startswith('TLS_PARALLEL '):
            match = re.fullmatch(r'TLS_PARALLEL ptr0=(0x[0-9a-f]+) ptr1=(0x[0-9a-f]+) live=2', line)
            need(match is not None, 'complete actual parallel-owner record')
            pointers = (int(match[1], 16), int(match[2], 16))
            need(pointers[0] != pointers[1] and static_rx['address'] in pointers and all(pointer in active for pointer in pointers) and
                 {active[pointer]['case'] for pointer in pointers} == {'parallel_a', 'parallel_b'} and
                 {active[pointer]['core'] for pointer in pointers} == {0, 1}, 'both-core simultaneous static/heap owners, no premature release')
            parallel_events += 1
        elif line.startswith('TLS_PRESSURE '):
            match = re.fullmatch(r'TLS_PRESSURE real_null=(\d+) recoveries=(\d+) blocks=(\d+) released=(\d+) budget=(\d+) owner_preserved=(\d+) rx=(0x[0-9a-f]+)', line)
            need(match is not None, 'whole real pressure record')
            nulls, recoveries, blocks, released, budget, owners = map(int, match.groups()[:6])
            pointer = int(match[7], 16)
            need((nulls, recoveries, blocks, released, budget, owners) == (1, 1, 131, 1, 4, 1) and
                 0 < released <= budget and pointer == static_rx['address'] and pointer in active and active[pointer]['case'] == 'pressure',
                 'original genuine allocator NULL/recovery, bounded reclaim and all live owners retained')
            pressure_events += 1
        elif line.startswith('TLS_DATA '):
            match = re.fullmatch(r'TLS_DATA case=(\w+) bytes=(\d+) reads=(\d+) full=(\d+) terminal=(-?\d+) sha256=([0-9a-f]{64})', line)
            need(match is not None, 'whole exact plaintext observation')
            label = match[1]
            need(label in opens and opens[label]['status'] == 1 and label not in data and opens[label]['pointer'] in active,
                 'data belongs to its still-live verified TLS context')
            numbers = tuple(map(int, match.groups()[1:5]))
            if label == 'truncated_record':
                need(numbers == (0, 0, 0, 0) and match[6] == EMPTY_SHA, 'incomplete response with read0/body0, not an invented TLS alert')
            else:
                need(label in NORMAL and numbers == (65536, 4, 4, 16384) and match[6] == PAYLOAD_SHA, 'complete original body/hash/full-record geometry')
            data[label] = (numbers, match[6])
        elif line.startswith('TLS_RX_FREE '):
            match = re.fullmatch(r'TLS_RX_FREE ptr=(0x[0-9a-f]+) kind=normal bytes=(\d+)', line)
            need(match is not None, 'actual original normal cleanup path')
            pointer = int(match[1], 16)
            need(pointer in active and int(match[2]) == 16717, 'exact live RX release, no double/foreign free')
            label = active[pointer]['case']
            need(label in opens and (opens[label]['status'] == -1 or label in data), 'no RX release before its terminal data/failure')
            del active[pointer]; frees += 1
    need(handshake_error is None and not active and (allocations, frees, attaches, static_loans, pressure_events, parallel_events) == (10, 10, 10, 9, 1, 1),
         'complete actual helper/owner census')
    need(set(opens) == NORMAL | {'wrong_name', 'handshake_close', 'truncated_record'} and set(data) == NORMAL | {'truncated_record'}, 'complete named native case census')
    need(log.count('Certificate validated') == 8 and log.count('TLS_TRAFFIC_PASS allocations=10 frees=10 attaches=10 full_responses=7 parallel_live=2 pressure_recovered=1') == 1,
         'actual bundle verification and complete terminal marker')
    return dict(allocations=allocations, frees=frees, attaches=attaches, static_loans=static_loans,
                heap_fallback_loans=1, full_responses=7, full_records=28, truncated_read_zero=True,
                real_pressure_nulls=1, recovered_idle_slots=1, preserved_warning_records=4)


def native_report_check(report, source_manifest, child, bundle):
    need(report['passed'] is True and report['state'] == 'complete' and report['native_mcu_executed'] is True and
         report['qemu_invoked'] is True and report['all_source_bindings_current'] is True, 'authentic complete native execution and source bindings')
    need(all(report[name] is False for name in ('physical_hardware', 'production_sources_changed', 'rf_or_full_radio_qualified',
         'physical_headroom_qualified', 'certificate_store_modified', 'insecure_verification', 'external_endpoints', 'user_network_restrict')),
         'original bounded native scope')
    need(report['sources'] == source_manifest['sources'] == bundle['sources'] and
         report['generated_project_inputs'] == source_manifest['generated_project_inputs'] == bundle['generated_project_inputs'],
         'exact frozen source and certificate/clock/config input manifests')
    need(child['pid'] == 23308 and child['exit_status'] == 0, 'actual SDK child terminal zero')
    commands = report['commands']
    need(all(row['pid'] > 0 and row['state'] == 'complete' and row['exit_status'] == 0 and not row.get('timed_out') for row in commands),
         'every actual SDK/observer/QEMU child terminal zero')
    need(next(row for row in commands if row['name'] == 'sdk-driver')['pid'] == 29744 and
         next(row for row in commands if row['name'] == 'qemu')['pid'] == 1976, 'original driver and actual emulator process bindings')
    need(report['full_responses'] == 7 and report['full_plaintext_records'] == 28 and report['parallel_live_clients'] == 2 and
         report['genuine_parallel_traffic_rounds'] == 4 and report['real_pressure_recovery'] is True, 'unchanged original selected-case outcome')
    cfg = report['compiled_profile']
    need(all(cfg[name] for name in ('MBEDTLS_HARDWARE_MPI', 'MBEDTLS_HARDWARE_AES', 'MBEDTLS_HARDWARE_SHA', 'ETH_USE_OPENETH',
         'YORADIO_TLS_INPUT_RECLAIM', 'YORADIO_TLS_STATIC_RX_RESERVE', 'YORADIO_TLS_EARLY_MPI_LOCK',
         'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE', 'MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_NONE', 'MBEDTLS_SSL_PROTO_TLS1_2')) and
         cfg['MBEDTLS_SSL_IN_CONTENT_LEN'] == 16384 and cfg['MBEDTLS_SSL_OUT_CONTENT_LEN'] == 4096 and
         not cfg['FREERTOS_UNICORE'] and not cfg['MBEDTLS_SSL_PROTO_TLS1_3'], 'actual unchanged classic dual-core hardware-crypto/full-record profile')
    need(report['static_rx'] == bundle['static_rx'] == dict(address=0x3ffbbd98, bytes=16717, kind='b'), 'original actual ELF static BSS RX metadata')


def verify(require_current=False, self_test=False):
    manifest = json.loads((FOLDER/'manifest.json').read_bytes()); policy(manifest)
    archive = FOLDER/manifest['archive']['path']
    need(archive.parent == FOLDER and archive.name == 'captures.zip' and archive.stat().st_size == manifest['archive']['bytes'] and
         sha(archive.read_bytes()) == manifest['archive']['sha256'], 'whole exact archive')
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        need(len(names) == len(set(names)) == manifest['physical_blobs'], 'complete unique physical archive census')
        blobs = {name: z.read(name) for name in names}
    for name, body in blobs.items():
        need(name == 'blobs/'+sha(body) and not body.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')) and
             re.search(rb'-----BEGIN CERTIFICATE-----\s+[A-Za-z0-9+/=\r\n]+-----END CERTIFICATE-----', body) is None,
             'only exact unflagged noncredential, nonbinary published bytes')
    files, identities = {}, {}
    for row in manifest['original_files']+manifest['projections']:
        name, body = row['path'], blobs[row['blob']]
        p = PurePosixPath(name)
        need(not p.is_absolute() and '..' not in p.parts and name not in identities and len(body) == row['bytes'] and sha(body) == row['sha256'], 'unique exact safe logical bytes')
        files[name], identities[name] = body, row
    need(len(manifest['original_files']) == manifest['public_original_files'] and len(manifest['projections']) == manifest['public_projection_files'] == 7 and
         set(blobs) == {row['blob'] for row in manifest['original_files']+manifest['projections']}, 'complete logical/physical public inventory')
    for row in manifest['omitted_payloads']:
        need(row['path'] not in identities and row['original_retained_locally'] is True and row['byte_payload_published'] is False and
             row['reasons'] and 'blobs/'+row['sha256'] not in blobs, 'whole local omission, no alternate publication or semantic override')
        identities[row['path']] = row
    need(len(identities) == manifest['original_file_census']+7, 'complete original and new-projection census')

    def identity(name, digest, size=None):
        need(name in identities and identities[name]['sha256'] == digest and
             (size is None or identities[name]['bytes'] == size), 'exact original source/log/omission identity: '+name)

    reports = {}
    for label, campaign in manifest['campaigns'].items():
        projection = json.loads(files['projections/'+label+'.json'])
        need(projection['projection_kind'] == 'literal_selected_original_report_fields' and projection['original_report_read_by_public_verifier'] is False and
             projection['original_report_sha256'] == campaign['original_report_sha256'] and projection['original_report_bytes'] == campaign['original_report_bytes'],
             'explicit new projection bound to unchanged original, never presented as original bytes')
        identity(label+'/report.json', projection['original_report_sha256'], projection['original_report_bytes'])
        report = reports[label] = projection['value']
        need(report['passed'] is OUTCOMES[label], 'unchanged original campaign outcome: '+label)
        if label+'/report.json' in files:
            original = json.loads(files[label+'/report.json'])
            need(original == report, 'whole public original and literal projection agree')
        if label.startswith('peer'):
            need(report['host_peer_only'] and report['native_mcu_executed'] is False and not report['physical_hardware'] and
                 not report['certificate_store_modified'] and not report['insecure_verification'] and not report['external_connections'], 'original host-only scope')
            for name, digest in report['sources'].items():
                identity(label+'/sources/'+name, digest)
            need(report['client_verification']['check_hostname'] and report['client_verification']['verify_mode'] == 'CERT_REQUIRED', 'actual host certificate/name verification configuration')
        elif label in ('freeze01', 'native01', 'native02'):
            for name, row in report['sources'].items():
                identity(label+'/'+row['snapshot'], row['sha256'], row['bytes'])
            for name, row in report['generated_project_inputs'].items():
                identity(label+'/'+name, row['sha256'], row['bytes'])
            for command in report['commands']:
                for stream in ('stdout', 'stderr'):
                    row = command[stream]
                    identity(label+'/'+row['path'], row['sha256'], row['bytes'])
        else:
            identity(label+'/main.c', report['source_sha256'])
            need(report['syntax_only'] and not report['sdk_build_invoked'] and not report['native_mcu_executed'] and
                 report['state'] == 'complete' and report['pid'] > 0 and report['exit_status'] == (0 if label == 'syntax02' else 1), 'real bounded syntax-only outcomes')
            for stream in ('stdout', 'stderr'):
                row = report[stream]
                identity(label+'/'+stream+'.log', row['sha256'], row['bytes'])
    peer01_events = [json.loads(line) for line in files['peer01/server.jsonl'].decode().splitlines()]
    need(reports['peer01']['cases'] == {} and reports['peer01']['error_type'] == 'ValueError' and
         [row['event'] for row in peer01_events] == ['listening', 'server_stopped'] and peer01_events[-1]['connections'] == 0,
         'preserved initial host environment nonpass before any accepted connection; precise OS cause unrecorded')
    host = reports['peer02']
    need(host['all_source_bindings_current'] and host['full_responses'] == 5 and host['full_plaintext_records'] == 20, 'complete actual host peer qualification')
    for label, row in host['cases'].items():
        if label in ('unknown_ca', 'wrong_name', 'handshake_close', 'truncated_record'):
            need(row['completed'] is False and row['body_bytes'] == 0, 'actual named host refusal')
            if label in ('unknown_ca', 'wrong_name'):
                need(row['failure_type'] == 'SSLCertVerificationError', 'genuine host certificate refusal')
        else:
            need(row['completed'] and row['certificate_verified'] and row['body_bytes'] == 65536 and row['sha256'] == PAYLOAD_SHA and row['read_sizes'] == [16384]*4, 'full actual host TLS response')
    host_result = server_check([json.loads(line) for line in files['peer02/server.jsonl'].decode().splitlines()], False)
    need(reports['freeze01']['state'] == 'frozen_unbuilt_unrun' and reports['freeze01']['preparation_passed'] and not reports['freeze01']['native_mcu_executed'], 'freeze-only is never execution acceptance')
    failed = reports['native01']
    failed_child = json.loads(files['native01/sdk-child.json'].decode('utf-8-sig'))
    need(failed['state'] == 'nonpass' and not failed['native_mcu_executed'] and not failed.get('qemu_invoked', False) and
         len(failed['commands']) == 1 and failed['commands'][0]['name'] == 'sdk-driver' and failed['commands'][0]['state'] == 'complete' and
         failed['commands'][0]['exit_status'] == 1 and failed_child['exit_status'] == 2 and
         b'No space left on device' in files['native01/sdk-build.stdout.log'] and 'native01/qemu.stdout.log' not in identities and
         'native01/execution-bundle.json' not in identities, 'actual disk-exhaustion failure before any MCU/QEMU run')
    syntax_error = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', files['syntax01/stderr.log'].decode())
    need('missing terminating " character' in syntax_error and files['syntax02/stderr.log'] == b'' and
         files['syntax01/main.c'] == files['syntax02/main.c'], 'original quote-parser failure, unchanged C and corrected syntax pass')
    native = reports['native02']
    source_manifest = json.loads(files['native02/source-manifest.json'])
    child = json.loads(files['native02/sdk-child.json'].decode('utf-8-sig'))
    bundle = json.loads(files['native02/execution-bundle.json'])
    native_report_check(native, source_manifest, child, bundle)
    need(json.loads(files['native02/build/config/sdkconfig.json']) == native['compiled_profile'], 'untouched actual generated configuration')
    for name, digest in SOURCE_PINS.items():
        row = native['sources'][name]
        need(row['sha256'] == digest, 'reviewed frozen diagnostic/parser instrumentation: '+name)
        identity('native02/'+row['snapshot'], digest, row['bytes'])
    c = files['native02/'+native['sources'][MAIN]['snapshot']].decode()
    need('.crt_bundle_attach=native_tls_rx_reserve_crt_bundle_attach' in c and '.common_name=name' in c and
         'skip_common_name' not in c and 'settimeofday(&now,NULL)' in c and 'psa_hash_update' in c and
         '__real_heap_caps_calloc(count,size,caps)' in c and 'injected' not in c and 'after.ready==before.ready' in c and
         'after.reading==before.reading' in c and 'after.writing==before.writing' in c and '((uint8_t *)writing)[i]==0x73' in c,
         'actual real allocator forwarding, certificate verification, PSA hashing and retained-input assertions')
    material = json.loads(files['material01/manifest.json'].decode('utf-8-sig'))
    need(material['ephemeral_test_only'] and not material['certificate_store_modified'] and not material['ca_private_key_written'], 'recorded disposable material generation scope')
    epoch = material['guest_epoch_seconds']
    need(datetime.fromisoformat(material['not_before_utc']).timestamp() <= epoch <= datetime.fromisoformat(material['not_after_utc']).timestamp(), 'historically valid guest clock, independent of current date')
    need(files['native02/project/main/test_clock.h'].decode().strip() == '#define TLS_TEST_EPOCH '+str(epoch), 'actual compiled valid guest clock input')
    for name, row in material['files'].items():
        identity('material01/'+name, row['sha256'], row['bytes'])
        need('material01/'+name not in files and all(row['sha256'] != sha(body) for body in blobs.values()), 'whole generated keys/certificates never published under an alias')
        for label in ('peer01', 'peer02', 'freeze01', 'native01', 'native02'):
            observed = reports[label]['material_identities'][name]
            need(observed['sha256'] == row['sha256'] and observed['bytes'] == row['bytes'] and observed['local_only'], 'all attempts bind exact same local material')
    closure = json.loads(files['native02/actual-compiler-closure.json'])
    need(closure['captured_before_execution'] and len(closure['dependencies']) == native['actual_compiler_dependencies'] == bundle['actual_compiler_dependencies'] == 1718 and
         set(closure['dependencies']) == set(manifest['compiler_dependency_snapshots']), 'complete captured actual compiler dependency census')
    for original, digest in closure['dependencies'].items():
        identity(manifest['compiler_dependency_snapshots'][original], digest)
    units = closure['translation_units']
    need(units == json.loads(files['native02/build/compile_commands.json']), 'exact actual compile records')
    for name in ('main.c', 'native_tls_rx_reserve.c', 'native_input_reclaim.c', 'native_tls_early_mpi.c', 'adaptive_input.c'):
        need(sum(normalize(row['file']).endswith('/'+name) for row in units) == 1, 'exact actual helper/main translation unit: '+name)
    need(sum(normalize(row['file']).endswith('/native-tls-static-rx/ssl_tls.c') for row in units) == 1 and
         not any('/.idf/v6.0.2/components/mbedtls/mbedtls/library/ssl_tls.c' in normalize(row['file']) for row in units), 'guarded build-local TLS source selected, installed SDK source not replaced')
    for name, callee in (('mbedtls_ssl_setup', '__wrap_yoradio_tls_static_rx_calloc'), ('mbedtls_ssl_free', '__wrap_yoradio_tls_static_rx_zeroize_free'),
                         ('app_main', '__wrap_native_tls_early_mpi_prepare')):
        need(callee.encode() in files['native02/asm-'+name+'.stdout.log'], 'actual disassembled helper dispatch: '+name)
    symbols = files['native02/symbols.stdout.log'].decode().replace('\r\n', '\n')
    match = re.search(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+b\s+s_rx$', symbols, re.M)
    need(match and int(match[1], 16) == native['static_rx']['address'] and int(match[2], 16) == native['static_rx']['bytes'], 'real ELF symbol static RX metadata, without reading omitted ELF')
    for name, row in native['local_binary_identities'].items():
        logical = 'native02/'+name.replace('\\', '/')
        identity(logical, row['sha256'], row['bytes'])
        need(logical not in files and row['local_only'], 'whole diagnostic image/binary remains local')
    for name, row in native['tools'].items():
        prefix = 'tools/'+name+'/'
        selected = [key for key in identities if key.startswith(prefix)]
        need(len(selected) == 1, 'complete exact tool identity: '+name)
        identity(selected[0], row['sha256'], row['bytes'])
        need(selected[0] not in files, 'compiled tool/ROM payload stays local')
    guest_log = files['native02/qemu.stdout.log'].decode()
    guest_result = guest_check(guest_log, native['static_rx'])
    native_events = [json.loads(line) for line in files['native02/server.jsonl'].decode().splitlines()]
    server_result = server_check(native_events, True)
    if require_current:
        for name, digest in manifest['canonical_diagnostic_sources'].items():
            need(sha((ROOT/name).read_bytes()) == digest, 'explicit optional current diagnostic source binding: '+name)
    controls = []
    if self_test:
        def reject(label, action):
            try:
                action()
            except (ValueError, KeyError):
                controls.append(label)
            else:
                raise ValueError('contradictory evidence accepted: '+label)
        for name in FALSE_SCOPES:
            changed = dict(manifest, **{name: True})
            reject('unsupported-'+name, lambda changed=changed: policy(changed))
        for label in ('peer01', 'native01', 'syntax01', 'freeze01'):
            changed = deepcopy(manifest); changed['campaigns'][label]['expected_pass'] = True
            reject('promoted-'+label, lambda changed=changed: policy(changed))
        for field in ('all_source_bindings_current', 'passed'):
            changed = deepcopy(native); changed[field] = False
            reject('native-'+field, lambda changed=changed: native_report_check(changed, source_manifest, child, bundle))
        changed = deepcopy(native); changed['sources'][MAIN]['sha256'] = '0'*64
        reject('source-binding-mismatch', lambda: native_report_check(changed, source_manifest, child, bundle))
        changed = deepcopy(native); changed['commands'][0]['exit_status'] = 1
        reject('driver-failure', lambda: native_report_check(changed, source_manifest, child, bundle))
        changed_child = dict(child, exit_status=2)
        reject('actual-sdk-child-failure', lambda: native_report_check(native, source_manifest, changed_child, bundle))
        for label, before, after in (
                ('generic-certificate-refusal', '-0x2700', '-0x7100'),
                ('bad-body-size', 'case=first bytes=65536', 'case=first bytes=65535'),
                ('wrong-body-hash', 'case=first bytes=65536 reads=4 full=4 terminal=16384 sha256='+PAYLOAD_SHA,
                 'case=first bytes=65536 reads=4 full=4 terminal=16384 sha256='+'0'*64),
                ('wrong-full-record-count', 'case=first bytes=65536 reads=4 full=4', 'case=first bytes=65536 reads=4 full=3'),
                ('fake-allocator-pressure', 'TLS_PRESSURE real_null=1', 'TLS_PRESSURE real_null=0'),
                ('lost-input-owner', 'budget=4 owner_preserved=1', 'budget=4 owner_preserved=0'),
                ('unbounded-reclaim', 'released=1 budget=4', 'released=5 budget=4'),
                ('invented-truncation-alert', 'case=truncated_record bytes=0 reads=0 full=0 terminal=0', 'case=truncated_record bytes=0 reads=0 full=0 terminal=-1')):
            need(before in guest_log, 'contradiction control applies to actual transcript: '+label)
            changed_log = guest_log.replace(before, after, 1)
            reject(label, lambda changed_log=changed_log: guest_check(changed_log, native['static_rx']))
        for warning in WARNINGS:
            changed_log = guest_log.replace(warning, 'suppressed diagnostic', 1)
            reject('warning-suppressed-'+warning, lambda changed_log=changed_log: guest_check(changed_log, native['static_rx']))
        marker = 'TLS_PARALLEL ptr0='
        at = guest_log.index(marker)
        premature = guest_log[:at]+'TLS_RX_FREE ptr=0x3ffbbd98 kind=normal bytes=16717\n'+guest_log[at:]
        reject('premature-rx-release', lambda: guest_check(premature, native['static_rx']))
        for label, event, key, value in (
                ('server-record-size', 'server_record', 'record_bytes', 16407),
                ('server-plaintext-size', 'plaintext_write', 'bytes', 16383),
                ('server-response-hash', 'response_complete', 'sha256', '0'*64),
                ('serialized-parallel-rounds', 'parallel_round', 'round', 2),
                ('no-real-client-hello', 'handshake_closed', 'received_bytes', 0)):
            changed_events = deepcopy(native_events)
            row = next(row for row in changed_events if row['event'] == event and
                       (event != 'server_record' or row['record_bytes'] == 16408))
            row[key] = value
            reject(label, lambda changed_events=changed_events: server_check(changed_events, True))
    print(json.dumps(dict(passed=True, original_attempts=7, public_original_reports_read=sum(label+'/report.json' in files for label in OUTCOMES),
                          omitted_original_reports_read=False, compiler_dependencies=1718, helper_dispatches_observed=3,
                          host=host_result, native=guest_result, independent_server=server_result,
                          contradiction_controls_rejected=len(controls), archived_code_executed=False,
                          omitted_payloads_read=False, current_diagnostic_sources_checked=require_current)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-current', action='store_true')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    verify(args.require_current, args.self_test)
