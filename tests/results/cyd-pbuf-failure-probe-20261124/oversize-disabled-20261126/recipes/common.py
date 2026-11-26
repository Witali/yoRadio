import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
PROFILE = BASE / 'legacy'
DEP = Path('C:/Work/yoRadio/.idf')

def load(path):
    return json.loads(Path(path).read_bytes())

def pin(path):
    body = Path(path).read_bytes()
    return dict(bytes=len(body), sha256=hashlib.sha256(body).hexdigest())

def write_new(path, value):
    path = Path(path)
    assert not path.exists(), 'Refuse to overwrite an earlier result'
    path.write_text(json.dumps(value, indent=2) + '\n')

def guard(check_seed=False):
    p = load(BASE / 'preflight.json')
    def git(*args):
        return subprocess.check_output(['git', '-c', 'core.longpaths=true', *args], cwd=ROOT)
    assert git('rev-parse', 'HEAD').decode().strip() == p['source_commit']
    assert not git('diff', '--name-only', 'HEAD') and not git('diff', '--cached', '--name-only')
    for name, expected in p['sources'].items():
        assert pin(ROOT / name) == expected, 'Frozen source changed: ' + name
    for name, expected in p['primary_sdk_sources'].items():
        assert pin(name) == expected, 'Pinned SDK input changed'
    for name, expected in p['helpers'].items():
        assert pin(ROOT / name) == expected, 'Frozen build helper changed'
    for name, expected in p.get('experiment_inputs', {}).items():
        assert pin(BASE / name) == expected, 'Prepared experiment input changed'
    for item in p['protected']:
        assert pin(ROOT / item['path']) == {k: item[k] for k in ('bytes', 'sha256')}, 'Protected input changed'
    original = ROOT / '.build/cpbuf24/sdk/legacy/fixture'
    expected_files = {item['file'] for item in p.get('baseline_fixture_inputs', [])}
    assert {x.relative_to(original).as_posix() for x in original.rglob('*') if x.is_file()} == expected_files
    for item in p['baseline_fixture_inputs']:
        path = original / item['file']
        assert not path.is_symlink() and path.resolve().is_relative_to(original.resolve())
        assert pin(path) == {k: item[k] for k in ('bytes', 'sha256')}, 'Frozen fixture input changed'
    for folder, revision in p['sdk_repositories'].items():
        repo = DEP / folder
        assert git('-C', str(repo), 'rev-parse', 'HEAD').decode().strip() == revision
        assert not git('-C', str(repo), 'status', '--porcelain', '--untracked-files=no')
    if check_seed:
        assert pin(PROFILE / 'sdkconfig') == p['seed_candidate']
    assert shutil.disk_usage(ROOT).free >= p['minimum_build_free_bytes'], 'Existing2 GiB disk guard failed'
    return p

def config_proof(build):
    before = load(PROFILE / 'baseline/sdkconfig.json')
    after = load(build / 'config/sdkconfig.json')
    delta = {k: dict(before=before.get(k), after=after.get(k))
             for k in before.keys() | after.keys()
             if k not in before or k not in after or type(before[k]) is not type(after[k]) or before[k] != after[k]}
    assert delta == load(BASE / 'preflight.json')['expected_effective_config_delta'], 'Effective configuration delta widened'
    assert after['LWIP_TCP_OVERSIZE_QUARTER_MSS'] is False
    old = (PROFILE / 'baseline/sdkconfig.h').read_bytes()
    new = (build / 'config/sdkconfig.h').read_bytes()
    old_lf, new_lf = old.replace(b'\r\n', b'\n'), new.replace(b'\r\n', b'\n')
    old_define = b'#define CONFIG_LWIP_TCP_OVERSIZE_MSS 1\n'
    new_define = b'#define CONFIG_LWIP_TCP_OVERSIZE_DISABLE 1\n'
    assert old_lf.count(old_define) == new_lf.count(new_define) == 1
    assert old_lf.replace(old_define, new_define) == new_lf, 'Generated header delta widened'
    return dict(effective_delta=delta, before=pin(PROFILE / 'baseline/sdkconfig.json'),
                after=pin(build / 'config/sdkconfig.json'), header_before=pin(PROFILE / 'baseline/sdkconfig.h'),
                header_after=pin(build / 'config/sdkconfig.h'),
                header_comparison='Exactly one selected choice define, after explicit CRLF-to-LF comparison; raw hashes retained.')
