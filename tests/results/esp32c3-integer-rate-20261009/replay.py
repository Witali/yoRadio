"""Verify frozen host evidence and reproduce the analytical filter calculation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
assert not args.output.resolve().is_relative_to(ROOT)
index=json.loads((ROOT/'index.json').read_text())['files']
for name,expected in index.items():
    path=(ROOT/name).resolve();assert path.is_relative_to(ROOT)
    assert path.stat().st_size==expected['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected['sha256']
for name in ('host-v2','default-regression'):
    report=json.loads((ROOT/name/'report.json').read_text())
    for source,digest in report['sources'].items():
        assert hashlib.sha256((ROOT/'sources'/source).read_bytes()).hexdigest()==digest,source
    if name=='host-v2':
        assert report['memory_sanitizers_passed'] and not report['production_qualified']
        assert len(report['cases'])==35
    else:
        assert report['pcm_identical'] and report['profile_pcm_identical'] and report['staged_profile_pcm_identical']
subprocess.run([sys.executable,str(ROOT/'sources/tools/codec_benchmark/compare_integer_rate_filters.py'),
                '--output',str(args.output)],check=True)
assert json.loads(args.output.read_text())==json.loads((ROOT/'filter-study.json').read_text())
print('PASS:',len(index),'byte-exact files and analytical replay; rejected quality verdict retained')
