"""Verify frozen metadata and raw seeds before the seven SDK builds."""
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
marker = json.loads((root / '.build/input-reclaim-production-source.json').read_text())
profiles = root / '.build/input-reclaim-production-profiles.json'
assert contract.sha(profiles) == marker['profiles_sha256']
rows = json.loads(profiles.read_text())
contract.profiles(root, rows)
contract.source(source_snapshot(root), marker)
for name, digest in marker['qualifier_tools_sha256'].items():
    assert contract.sha(root / name) == digest, ('qualification_tool_changed', name)
for row in rows:
    contract.baseline(root, row, git)
    assert contract.sha(row['sdkconfig']) == row['prepared_sdkconfig_sha256'], 'prepared_seed_changed'
    assert contract.evidence(root, row) == marker['expected_evidence'][row['name']], 'frozen_evidence_changed'
print('PASS pre-build clean source / exact seven profiles / immutable baselines / raw seeds / frozen evidence / tools')
