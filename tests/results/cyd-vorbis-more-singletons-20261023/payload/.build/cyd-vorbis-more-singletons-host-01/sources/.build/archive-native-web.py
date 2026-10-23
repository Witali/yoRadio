"""Copy selected immutable host evidence, excluding executables and secrets."""
from pathlib import Path
import hashlib
import json
import shutil

root=Path(__file__).resolve().parents[1]
destination=root/'tests/results/native-web-transfer-20261018'
groups={
    'message': 'ws-message-prefix-final',
    'radio': 'radio-pair-parent',
    'index-c3': 'playlist-pair-c3-final',
    'index-cyd': 'playlist-pair-cyd-final',
    'multipart': 'shared-multipart-integrated-final',
    'multipart-existing': 'c3-web-memory-transfer-integrated',
    'uploads': 'native-uploads-namespace-lock-final',
    'wifi-c3': 'c3-wifi-persistence-final',
    'wifi-cyd': 'cyd-wifi-storage-integrated-final',
    'web-regressions': 'web-warning-namespace-wifi-final',
    'static-startup-cyd': 'cyd-web-upload-start-final',
    'startup-c3': 'c3-web-start-transfer-first',
    'httpd-cyd': 'rfc6455-http-length-cyd-fixed',
    'httpd-c3': 'rfc6455-http-length-c3-fixed',
    'transport-faults': 'native-web-transport-final',
    'tls-bundle': 'native-web-bundle-final',
    'ws-cyd': 'cyd-ws-native-transport-first',
    'ws-cyd-final': 'cyd-ws-http-fallback-final',
    'ws-c3-final': 'c3-ws-http-fallback-final',
    'tcp-integrated': 'ws-integration-qualified-final',
    'wss-integrated': 'wss-integration-qualified-final',
    'tls-cyd': 'native-tls-602-qualified-final',
    'tls-c3': 'native-tls-611-qualified-final',
    'tls-bundle-profile': 'native-web-bundle-profile-freeze',
    'ws-lint-cyd': 'ws-lint-http-fallback-cyd',
    'ws-lint-c3': 'ws-lint-http-fallback-c3',
    'sdk-components': 'sdk-web-components-final',
    'multipart-gcc-output': 'multipart-gcc-outputs-final',
    'uploads-gcc-output': 'native-uploads-gcc-outputs-final',
    'gcc-output-contract': 'gcc-output-contract-final',
    'multipart-lint-c3': 'multipart-gcc-lint-c3',
    'multipart-lint-cyd': 'multipart-gcc-lint-cyd',
    'lint-cyd': 'lint-cyd-web-transfer-full',
    'lint-c3': 'lint-c3-web-transfer-full',
}
allowed={'.json','.log','.c','.h','.cpp','.inc','.py','.js','.cjs','.ps1','.cmake','.txt','.yaml','.md','.gz'}

def copy_exact(source,target):
    data=source.read_bytes()
    if target.exists():
        assert target.read_bytes()==data, f'Immutable evidence differs: {target}'
    else:
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)

manifest={}
for name,folder in groups.items():
    source=root/'.build'/folder
    reports=list(source.glob('*report.json')) or list(source.glob('results.json'))
    assert reports, source
    for file in source.rglob('*'):
        if not file.is_file() or (file.suffix.lower() not in allowed and file.name!='.clang-tidy'): continue
        if '__pycache__' in file.parts or 'fs' in file.relative_to(source).parts: continue
        assert file.suffix.lower() not in {'.pem','.key','.crt','.bin','.csv'}
        copy_exact(file,destination/name/file.relative_to(source))
    # Older harnesses recorded hashes without source snapshots. Reconstruct
    # only from identical current bytes; a mismatch requires another run.
    for report in reports:
        record=json.loads(report.read_text(encoding='utf-8'))
        hashes=record.get('source_sha256',{})
        if isinstance(hashes,dict):
            for relative,expected in hashes.items():
                if not isinstance(expected,str): continue
                snapshot=destination/name/'sources'/relative
                source_snapshot=source/'sources'/relative
                candidate=(snapshot if snapshot.is_file() else
                           source_snapshot if source_snapshot.is_file() else root/relative)
                assert candidate.is_file(), (name,relative)
                actual=hashlib.sha256(candidate.read_bytes()).hexdigest()
                assert actual==expected, (name,relative,expected,actual)
                copy_exact(candidate,snapshot)
    manifest[name]={'origin':'.build/'+folder,
                    'reports':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in reports}}
for file in destination.rglob('*'):
    if file.is_file() and file.name!='archive-manifest.json':
        manifest.setdefault('files',{})[file.relative_to(destination).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
(destination/'archive-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('Archived',len(manifest['files']),'exact evidence files in',destination.relative_to(root))
