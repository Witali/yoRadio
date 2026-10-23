"""Freeze current clean source, exact profiles, seeds, evidence and local tools."""
from pathlib import Path
import json
import subprocess
import sys
import input_reclaim_sdk_contract as contract

root = Path.cwd()
contract.longpaths()
sys.path.insert(0, str(root / 'tools'))
from export_cyd_production import source_snapshot
git = lambda *args: subprocess.check_output(['git', '-c', 'core.longpaths=true', *args], cwd=root)
target = root / '.build/input-reclaim-production-source.json'
assert not target.exists()
rows = json.loads((root / '.build/input-reclaim-production-profiles.json').read_text())
contract.profiles(root, rows)
for row in rows:
    contract.baseline(root, row, git)
    assert contract.sha(row['sdkconfig']) == row['prepared_sdkconfig_sha256'], 'prepared_seed_changed'
snapshot = source_snapshot(root)
assert not snapshot['source_dirty'] and not snapshot['untracked'], snapshot
names = ['prepare-input-reclaim-production.py', 'run-input-reclaim-production.ps1',
         'qualify-input-reclaim-sdk.py', 'input_reclaim_sdk_contract.py',
         'input-reclaim-production-preflight.py', 'freeze-input-reclaim-production.py']
tools = {'.build/' + name: contract.sha(root / '.build' / name) for name in names}
marker = dict(source_commit=snapshot['commit'], source_content_sha256=snapshot['content_sha256'],
              source_snapshot=snapshot, profiles_sha256=contract.sha(root / '.build/input-reclaim-production-profiles.json'),
              qualifier_tools_sha256=tools, expected_evidence={row['name']: contract.evidence(root, row) for row in rows})
target.write_text(json.dumps(marker, indent=2) + '\n')
print(json.dumps(dict(source_commit=marker['source_commit'], profiles=7,
                      source_content_sha256=marker['source_content_sha256'], marker_sha256=contract.sha(target)), indent=2))
