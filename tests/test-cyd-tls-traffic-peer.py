"""Qualify only the synthetic loopback peer using actual verified TLS1.2 clients."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import ssl
import sys

ROOT = Path(__file__).resolve().parents[1]
PEER = ROOT/'tests/target/cyd_tls_traffic_qemu/loopback_server.py'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--material', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    material, out = args.material.resolve(), args.output.resolve()
    need(material.is_relative_to(ROOT/'.build') and out.is_relative_to(ROOT/'.build') and not out.exists(), 'existing ignored material and fresh ignored capture')
    out.mkdir(parents=True)
    report = dict(passed=False, host_peer_only=True, native_mcu_executed=False, physical_hardware=False,
                  certificate_store_modified=False, insecure_verification=False, external_connections=False,
                  sources={}, material_identities={}, cases={})
    for path in (Path(__file__).resolve(), PEER):
        body = path.read_bytes()
        relative = path.relative_to(ROOT)
        target = out/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        report['sources'][relative.as_posix()] = sha(body)
    for name in ('manifest.json', 'ca.pem', 'server.pem', 'server-key.pem'):
        body = (material/name).read_bytes()
        report['material_identities'][name] = dict(bytes=len(body), sha256=sha(body), local_only=True)

    def save():
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    save()
    spec = importlib.util.spec_from_file_location('synthetic_loopback_tls_peer', PEER)
    peer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(peer)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = context.maximum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256')
    context.load_verify_locations(cafile=material/'ca.pem')
    report['client_verification'] = dict(check_hostname=context.check_hostname, verify_mode=context.verify_mode.name,
                                         openssl=ssl.OPENSSL_VERSION)

    def receive(label, port, supplied=context, hostname='cyd-tls.invalid'):
        body, headers, reads = bytearray(), bytearray(), []
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=10) as tcp:
                with supplied.wrap_socket(tcp, server_hostname=hostname, suppress_ragged_eofs=False) as tls:
                    need(tls.version() == 'TLSv1.2' and tls.cipher()[0] == 'ECDHE-RSA-AES128-GCM-SHA256', 'actual negotiated protocol/cipher')
                    need(tls.getpeercert(), 'actual verified peer certificate')
                    tls.sendall(('GET /case/'+label+' HTTP/1.1\r\nHost: cyd-tls.invalid\r\nConnection: close\r\n\r\n').encode())
                    while not headers.endswith(b'\r\n\r\n'):
                        value = tls.recv(1)
                        need(value and len(headers) < 1024, 'complete bounded response header')
                        headers.extend(value)
                    need(headers.startswith(b'HTTP/1.1 200 OK\r\n') and b'Content-Length: 65536\r\n' in headers, 'exact synthetic response')
                    while len(body) < len(peer.PAYLOAD):
                        value = tls.recv(16384)
                        need(value, 'complete response before EOF')
                        reads.append(len(value)); body.extend(value)
                    need(bytes(body) == peer.PAYLOAD, 'complete exact synthetic plaintext')
                    tls.unwrap()
            return dict(completed=True, body_bytes=len(body), sha256=sha(body), read_sizes=reads, certificate_verified=True)
        except (ssl.SSLError, OSError, ValueError) as error:
            return dict(completed=False, body_bytes=len(body), sha256=sha(body), read_sizes=reads,
                        failure_type=type(error).__name__, error_code=getattr(error, 'winerror', getattr(error, 'errno', None)))

    try:
        with peer.LoopbackTLS(material, out/'server.jsonl') as server:
            for label in ('first', 'reopen'):
                result = receive(label, server.ports[0])
                report['cases'][label] = result; save()
                need(result['completed'], 'verified host full response: '+label)
            unknown = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            unknown.minimum_version = unknown.maximum_version = ssl.TLSVersion.TLSv1_2
            for label, port, supplied, hostname in (
                    ('unknown_ca', server.ports[0], unknown, 'cyd-tls.invalid'),
                    ('wrong_name', server.ports[0], context, 'wrong.invalid'),
                    ('handshake_close', server.ports[1], context, 'cyd-tls.invalid'),
                    ('truncated_record', server.ports[2], context, 'cyd-tls.invalid')):
                result = receive(label, port, supplied, hostname)
                report['cases'][label] = result; save()
                need(not result['completed'] and result['body_bytes'] == 0, 'named actual TLS failure: '+label)
                if label in ('unknown_ca', 'wrong_name'):
                    need(result['failure_type'] == 'SSLCertVerificationError', 'real certificate validation refusal: '+label)
            with ThreadPoolExecutor(max_workers=2) as executor:
                jobs = {label: executor.submit(receive, label, server.ports[0]) for label in ('parallel_a', 'parallel_b')}
                for label, job in jobs.items():
                    result = job.result(timeout=30)
                    need(result['completed'], 'actual simultaneous verified host response: '+label)
                    report['cases'][label] = result; save()
            result = receive('after_failures', server.ports[0])
            need(result['completed'], 'actual reopen after all failures and parallel traffic')
            report['cases']['after_failures'] = result; save()
        events = [json.loads(line) for line in (out/'server.jsonl').read_text().splitlines()]
        complete = [row for row in events if row['event'] == 'response_complete']
        need(len(complete) == 5 and all(row['bytes'] == 65536 and row['sha256'] == peer.PAYLOAD_SHA256 for row in complete), 'five whole real peer responses')
        for row in complete:
            writes = [entry for entry in events if entry['event'] == 'plaintext_write' and entry['connection'] == row['connection']]
            records = [entry for entry in events if entry['event'] == 'server_record' and entry['connection'] == row['connection'] and entry['content_type'] == 23 and entry['record_bytes'] == 16408]
            need(len(writes) == len(records) == 4 and all(entry['bytes'] == 16384 for entry in writes), 'four genuine full TLS1.2 AES-GCM plaintext records per response')
        rounds = [row for row in events if row['event'] == 'parallel_round']
        need(len(rounds) == 8 and [row['round'] for row in rounds] == [0, 0, 1, 1, 2, 2, 3, 3] and
             len({row['connection'] for row in rounds}) == 2, 'two simultaneous live TLS contexts with synchronized traffic rounds')
        need(sum(row['event'] == 'record_truncated' for row in events) == 1 and
             sum(row['event'] == 'handshake_closed' for row in events) == 1 and events[-1]['event'] == 'server_stopped', 'actual named failure controls and clean server shutdown')
        need(all(sha((ROOT/name).read_bytes()) == digest for name, digest in report['sources'].items()), 'peer sources unchanged')
        report.update(passed=True, full_responses=5, full_plaintext_records=20, full_plaintext_record_bytes=16384,
                      ciphertext_record_bytes=16408, simultaneous_live_clients=2,
                      parallel_traffic_rounds=4, all_source_bindings_current=True)
        print(json.dumps({key: value for key, value in report.items() if key not in ('sources', 'material_identities', 'cases')}))
        return 0
    except BaseException as error:
        report['error_type'] = type(error).__name__
        print(json.dumps(dict(passed=False, error_type=type(error).__name__)))
        raise
    finally:
        save()


if __name__ == '__main__':
    raise SystemExit(main())
