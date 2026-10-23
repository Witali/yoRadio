from pathlib import Path
import hashlib,json,shutil
root=Path.cwd();source=root/'.build/cyd-flac-maintenance-regression-final';dest=root/'tests/results/cyd-flac-runtime-20261019/maintenance-regression';dest.mkdir(exist_ok=False)
report=json.loads((source/'report.json').read_text());assert report['passed']
for p in source.rglob('*'):
 if p.is_file() and p.suffix in {'.c','.cpp','.h','.py','.inc','.json','.log'}:
  target=dest/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for relative,expected in report['source_sha256'].items():
 snapshot=source/'sources'/relative;assert hashlib.sha256(snapshot.read_bytes()).hexdigest()==expected,relative
 target=dest/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():shutil.copyfile(snapshot,target)
print('PASS maintenance', {key:len(value) for key,value in report['variants'].items()},len(report['negative_controls']),'semantic controls')
