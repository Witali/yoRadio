from pathlib import Path
import json,hashlib,shutil,gzip
root=Path.cwd();run=root/'.build/early-owner-public-600-01'
dest=root/'tests/results/esp32c3-stream-probe-20261013/early-owner-public-01'
controller=json.loads((run/'controller.json').read_text())
report=json.loads((run/'physical/report.json').read_text())
restore=controller['restoration']
assert restore['image']['app_elf_sha256']==controller['original']['app_elf_sha256']
assert not restore['status']['audio']
assert all(restore[k] is True for k in ('wifi_unchanged','playlist_unchanged','settings_unchanged'))
assert controller['installed']['app_elf_sha256']==controller['candidate']['app_elf_sha256']
assert report['image']==controller['candidate']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for rel,digest in report['test_sources_sha256'].items():
 assert sha(root/rel)==digest,rel
dest.mkdir(parents=True,exist_ok=False)
(dest/'.gitattributes').write_text('* -text\n')
for p in run.rglob('*'):
 if p.is_file():
  target=dest/p.relative_to(run);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
shutil.copyfile(root/'.build/run-early-owner-public.py',dest/'controller.py')
shutil.copyfile(__file__,dest/'archive.py')
for rel in ('tools/esp32c3_tests/sustained_output.py','tools/esp32c3_tests/common.py',
            'tools/esp32c3_tests/production_health.py','tools/esp32c3_tests/public_streams.py',
            'tools/esp32c3_tests/aac_reference.py','tools/esp32c3_tests/ota.py',
            'tools/esp32c3_tests/trace_transport.py','tools/esp32c3_tests/run.py',
            'tests/test-sustained-output.py'):
 target=dest/'sources'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,target)
logs=root/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-startup-confirm/log'
latest=max(logs.glob('idf_py_stdout_output_*'),key=lambda p:p.stat().st_mtime)
(dest/'build.log.gz').write_bytes(gzip.compress(latest.read_bytes(),mtime=0))
def save(name,value):(dest/name).write_text(json.dumps(value,indent=2)+'\n')
save('summary.json',dict(passed=controller['test_exit_code']==0,
 cases=[dict(name=r['name'],result=r['result']) for r in report['cases']],
 reference=report['reference']['spec'],seconds=report['seconds'],
 output_window=report.get('output_window'),health=report.get('steady_health'),
 restoration_verified=True,production_qualified=False,
 scope='One ten-minute public HE-AAC stream and sampled WebUI/output/heap health. Concurrent host decode uses a separate connection; not synchronized packet comparison. No analog continuity or all-format qualification.'))
save('sha256.json',{p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='sha256.json'})
print('Archived',dest)
