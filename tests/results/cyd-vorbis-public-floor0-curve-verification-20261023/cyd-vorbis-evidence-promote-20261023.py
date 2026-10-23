"""Copy a verified new evidence archive byte-exactly; never replace a destination."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    result = {}
    for path in root.rglob('*'):
        need(not path.is_symlink(), 'No symlink in evidence inventory')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = dict(bytes=path.stat().st_size, sha256=digest(path))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('stage', 'destination', 'verification', 'report'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    stage, destination, report_path = (value.resolve() for value in (args.stage, args.destination, args.report))
    allowed = {'cyd-vorbis-public-floor0-curve-20261023', 'cyd-vorbis-more-singletons-20261023'}
    need(stage.is_dir() and stage.is_relative_to(repo / '.build') and stage != repo / '.build', 'Bounded existing stage')
    need(destination.parent == repo / 'tests/results' and destination.name in allowed and not destination.exists(), 'Exact fresh canonical destination')
    need(report_path.parent == repo / '.build' and not report_path.exists(), 'Separate fresh promotion proof')
    need(digest(stage / 'manifest.json') == args.manifest_sha256, 'Reviewed stage manifest identity')
    verification = args.verification.resolve()
    receipt = json.loads(verification.read_bytes())
    need(receipt['status'] == 'TERMINAL' and type(receipt['returncode']) is int and receipt['returncode'] == 0
         and type(receipt['owned_pid']) is int and receipt['owned_pid'] > 0
         and not receipt.get('timed_out', False) and not receipt.get('interrupted', False)
         and not receipt.get('error_type'), 'Actual successful stage verification')
    for origin, fact in receipt['logs'].items():
        path = Path(origin)
        need(path.stat().st_size == fact['bytes'] and digest(path) == fact['sha256'], 'Actual verification stream identity')
    argv = receipt['argv']
    need(argv.count('--root') == argv.count('--manifest-sha256') == 1
         and (Path(receipt['cwd']) / argv[argv.index('--root') + 1]).resolve() == stage
         and argv[argv.index('--manifest-sha256') + 1] == args.manifest_sha256, 'Stage verification operands')
    before = inventory(stage)
    shutil.copytree(stage, destination)
    after = inventory(destination)
    need(before == after and inventory(stage) == before, 'Every canonical and stage file remains byte-identical')
    result = dict(result='COPIED_PENDING_CANONICAL_REPLAY', manifest_sha256=args.manifest_sha256,
        stage=str(stage), destination=str(destination), files=len(before), bytes=sum(row['bytes'] for row in before.values()),
        stage_verification_sha256=digest(verification), destination_previously_absent=True,
        exact_copy=True, canonical_replay_completed=False, files_verified=before)
    with report_path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({name: result[name] for name in ('result', 'files', 'bytes', 'manifest_sha256')}))


if __name__ == '__main__':
    main()
