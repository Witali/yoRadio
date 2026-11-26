import hashlib,json,shutil,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]
SOURCE='f7dee344fb30ce109f2d30a01f0325d353e3b2eb'
def pin(p):
 b=Path(p).read_bytes(); return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def load(p): return json.loads(Path(p).read_bytes())
def git(*a): return subprocess.check_output(['git','-c','core.longpaths=true',*a],cwd=ROOT)
assert git('rev-parse','HEAD').decode().strip()==SOURCE and not git('diff','--name-only','HEAD') and not git('diff','--cached','--name-only')
assert not (BASE/'candidate-inputs.json').exists() and shutil.disk_usage(ROOT).free>2*1024**3
baseline=load(BASE/'sdk-baseline/baseline-index.json')
for item in baseline['protected']: assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256'])
sources={}
for name in ('pbuf_failure.c','pbuf_failure_record.h','pcm.c','attach.cmake','prepare.py','prepare-rx-source.py'):
 p=ROOT/'tests/target/cyd_full_app_openeth_qemu'/name; sources[p.relative_to(ROOT).as_posix()]=pin(p)
for profile in baseline['profiles']:
 backend=profile['backend']; d=BASE/'sdk'/backend; d.mkdir(parents=True)
 old=BASE/'sdk-baseline'/backend; assert pin(old/'objects.zip')=={k:profile['object_zip'][k]for k in ('bytes','sha256')}
 shutil.copyfile(old/'sdkconfig',d/'sdkconfig')
 compiled=load(ROOT/'.build/cnortc24'/backend/'baseline.json')['project_units']
 for unit in compiled:
  p=ROOT/unit['file']; value=pin(p)
  if unit['file']!='tests/target/cyd_full_app_openeth_qemu/pcm.c': assert value==dict(bytes=unit['bytes'],sha256=unit['sha256'])
  sources[unit['file']]=value
result=dict(source_commit=SOURCE,baseline_index=pin(BASE/'sdk-baseline/baseline-index.json'),sources=sources,
 sdk_repositories=baseline['sdk_repositories'],protected=baseline['protected'],qemu=baseline['qemu'],
 candidate_flag='CYD_OPENETH_PBUF_FAILURE_PROBE=ON',kconfig_delta=[],compiled=False)
(BASE/'candidate-inputs.json').write_text(json.dumps(result,indent=2)+'\n')
print('Candidate source/inputs frozen; profiles prepared, no compilation yet.')
