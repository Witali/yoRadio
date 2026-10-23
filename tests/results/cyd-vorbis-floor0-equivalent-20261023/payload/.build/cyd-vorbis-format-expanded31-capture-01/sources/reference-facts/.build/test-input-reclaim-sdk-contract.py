"""Exercise metadata false-positive guards without running an SDK build."""
from copy import deepcopy
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

root = Path.cwd()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
out = parser.parse_args().output.resolve()
assert out.is_relative_to(root / '.build')
out.mkdir(parents=True, exist_ok=False)
path = root / '.build/input_reclaim_sdk_contract.py'
inputs = [path, Path(__file__).resolve(), root / '.build/input-reclaim-production-profiles.json']
frozen = {}
for original in inputs:
    raw = original.read_bytes()
    (out / original.name).write_bytes(raw)
    frozen[str(original)] = hashlib.sha256(raw).hexdigest()
spec = importlib.util.spec_from_file_location('contract', path)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
rows = json.loads((root / '.build/input-reclaim-production-profiles.json').read_text())
contract.profiles(root, rows)
results = {}

def rejects(name, run, expected):
    try:
        run()
    except AssertionError as error:
        assert str(error) == expected, (name, str(error), expected)
        results[name] = {'detected': True, 'predicate': str(error)}
    else:
        raise RuntimeError('False-positive guard failed: ' + name)

rejects('empty-matrix', lambda: contract.profiles(root, []), 'exact_seven_profiles')
rejects('missing-backend', lambda: contract.profiles(root, rows[:-1]), 'exact_seven_profiles')
bad = deepcopy(rows); bad[-1] = deepcopy(bad[0])
rejects('duplicate-profile', lambda: contract.profiles(root, bad), 'exact_profile_set')
bad = deepcopy(rows); bad[0]['enabled'] = False
rejects('wrong-feature-selection', lambda: contract.profiles(root, bad), 'profile_selection')
bad = deepcopy(rows); bad[1]['build_directory'] = bad[0]['build_directory']; bad[1]['sdkconfig'] = bad[0]['sdkconfig']
rejects('shared-build-config', lambda: contract.profiles(root, bad), 'unique_build_directory')
bad = deepcopy(rows); bad[0]['baseline'] = str(root / 'firmware/development/esp32-cyd2usb-native-output-telemetry-legacy')
rejects('wrong-baseline-backend', lambda: contract.profiles(root, bad), 'baseline_selection')

git = lambda *args: subprocess.check_output(['git', '-c', 'core.longpaths=true', *args], cwd=root)
for row in rows:
    contract.baseline(root, row, git)
bad = deepcopy(rows[0]); bad['baseline_sdkconfig_sha256'] = 'different-baseline'
rejects('changed-baseline-identity', lambda: contract.baseline(root, bad, git), 'baseline_sdkconfig_hash')
def altered_blob(*args):
    return b'{}' if args[-1].endswith('/sdkconfig.json') else git(*args)
rejects('working-baseline-differs-from-git', lambda: contract.baseline(root, rows[0], altered_blob), 'committed_baseline_sdkconfig.json')

snapshot = dict(commit='frozen-head', source_dirty=False, dirty=False, untracked=[],
                excluded_paths=['firmware/development/', 'tests/results/'], content_sha256='frozen-content')
marker = dict(source_commit='frozen-head', source_content_sha256='frozen-content', source_snapshot=deepcopy(snapshot))
contract.source(snapshot, marker)
bad = deepcopy(snapshot); bad['content_sha256'] = 'edited-same-head'
rejects('same-head-edited-content', lambda: contract.source(bad, marker), 'current_source_content')
bad = deepcopy(snapshot); bad['untracked'] = ['new-source.c']
rejects('untracked-source', lambda: contract.source(bad, marker), 'current_source_clean')

row = rows[0]
refs = {'fixed-host-README': 'frozen-host-sha', 'fixed-http-README': 'frozen-http-sha'}
refs = {str(Path(name).resolve()): value for name, value in refs.items()}
receipt = dict(source_commit='frozen-head', source_dirty=False, source_untracked=[], source_content_sha256='frozen-content',
               source_excluded_paths=snapshot['excluded_paths'], variant=row['variant'], backend=row['backend'],
               build_directory=row['build_directory'], sdkconfig_seed={'source_sha256': row['prepared_sdkconfig_sha256']},
               evidence=[{'path': name, 'sha256': value} for name, value in refs.items()])
contract.receipt(receipt, row, marker, refs)
bad = deepcopy(receipt); bad['evidence'] = []
rejects('empty-evidence', lambda: contract.receipt(bad, row, marker, refs), 'intended_evidence_count')
bad = deepcopy(receipt); bad['evidence'][0]['sha256'] = 'edited-evidence'
rejects('altered-evidence', lambda: contract.receipt(bad, row, marker, refs), 'intended_evidence_set')
bad = deepcopy(receipt); bad['sdkconfig_seed']['source_sha256'] = 'different-seed'
rejects('different-prepared-seed', lambda: contract.receipt(bad, row, marker, refs), 'actual_prepared_seed')
bad = deepcopy(receipt); bad['source_content_sha256'] = 'different-source'
rejects('different-receipt-source', lambda: contract.receipt(bad, row, marker, refs), 'receipt_source_content')

assert all(contract.sha(original) == digest for original, digest in frozen.items())
(out / 'report.json').write_text(json.dumps({'passed': True, 'metadata_only': True, 'cases': results,
                                         'module_sha256': contract.sha(path), 'frozen_inputs': frozen,
                                         'inputs_unchanged_after': True, 'sdk_or_device_runs': 0}, indent=2) + '\n')
print('PASS seven-profile metadata contract and ' + str(len(results)) + ' exact false-positive controls')
