"""Copy one reviewed evidence stage without overwriting another archive."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / '.build/cyd-vorbis-wide-width-archive-stage-01'
DEST = ROOT / 'tests/results/cyd-vorbis-wide-width-20261023'


def inventory(root):
    result = {}
    for path in root.rglob('*'):
        assert not path.is_symlink()
        if path.is_file():
            raw = path.read_bytes()
            result[path.relative_to(root).as_posix()] = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    return result


def main():
    assert SOURCE.is_relative_to(ROOT / '.build') and DEST.is_relative_to(ROOT / 'tests/results')
    assert SOURCE.is_dir() and not DEST.exists()
    receipt_path = ROOT / '.build/cyd-vorbis-wide-width-archive-stage-verify-01-command.json'
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt['status'] == 'TERMINAL' and receipt['returncode'] == 0
    assert receipt['owned_pid'] > 0 and not receipt.get('timed_out') and not receipt.get('interrupted')
    assert receipt['argv'][-2:] == ['--repository', '.']
    for path, row in receipt['logs'].items():
        raw = Path(path).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
    before = inventory(SOURCE)
    shutil.copytree(SOURCE, DEST)
    assert inventory(DEST) == before == inventory(SOURCE)
    result = dict(schema='wide-width-archive-exact-promotion-v1', files=len(before),
        stored_bytes=sum(row['bytes'] for row in before.values()), source=str(SOURCE), destination=str(DEST),
        manifest_sha256=before['manifest.json']['sha256'], exact_copy=True,
        canonical_offline_verifier_executed=False)
    out = ROOT / '.build/cyd-vorbis-wide-width-promotion-01.json'
    with out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
