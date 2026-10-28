"""Pure local inspection helpers; never execute or extract archived content."""
import hashlib, importlib.util, io, json, zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def need(test, message):
    if not test:
        raise ValueError(message)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load_local(relative, digest, name):
    path = ROOT/relative
    need(sha(path.read_bytes()) == digest, 'pinned local reader')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def archive_members(relative, archive_digest, manifest_digest):
    folder = ROOT/relative
    body = (folder/'captures.zip').read_bytes(); manifest_body = (folder/'manifest.json').read_bytes()
    need(sha(body)==archive_digest and sha(manifest_body)==manifest_digest, 'pinned archive/manifest')
    manifest = json.loads(manifest_body)
    need(manifest['archive_sha256']==archive_digest and manifest['archive_bytes']==len(body), 'archive identity')
    expected = {row['path']:row for row in manifest['files']}
    need(len(expected)==len(manifest['files']), 'unique manifest members')
    result = {}
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        need(len(archive.infolist())==len(expected), 'exact archive inventory')
        for entry in archive.infolist():
            name = entry.filename; path = PurePosixPath(name)
            need(not path.is_absolute() and '..' not in path.parts and name in expected and name not in result,
                 'contained unique member')
            data = archive.read(entry); row = expected[name]
            need(len(data)==row['bytes'] and sha(data)==row['sha256'], 'every archived byte')
            result[name] = data
    return result


def clean_host(members, group='host04'):
    report = json.loads(members[group+'/report.json'])
    need(report['completed'] and report['passed'], 'host completed successfully')
    for row in report['commands']:
        receipt = row['supervisor']
        need(row['transport_exit']==0 and not row.get('forced_transport_stop') and
            receipt['nonce']==row['nonce'] and receipt['request_sha256']==row['request_sha256'] and
            receipt['state']=='terminal' and receipt['final'] and receipt['new_session'] and
            receipt['child_pid']==receipt['owned_pgid'] and receipt['child_reaped'] and
            receipt['group_gone'] and receipt['child_returncode']==0, 'owned command fully terminal')
    need(not members[group+'/execute.stderr.log'], 'no sanitizer diagnostic')
    capture = members[group+'/capture.bin']
    need(sha(capture)==report['capture_sha256'], 'captured output identity')
    return report, capture
