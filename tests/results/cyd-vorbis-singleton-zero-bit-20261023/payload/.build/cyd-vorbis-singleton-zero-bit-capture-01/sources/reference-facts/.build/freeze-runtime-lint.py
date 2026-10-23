"""Freeze exact reported units and current project headers without changing old logs."""
import datetime,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
for board,relative in [('c3','.build/lint-c3-runtime-transfer-complete-01')]:
 directory=ROOT/relative;report=json.loads((directory/'report.json').read_text())
 assert report['complete'] and report['errors']==0
 sources={};dependencies={}
 def write(relative,data):
  path=directory/'sources'/relative;path.parent.mkdir(parents=True,exist_ok=True)
  if path.exists():assert path.read_bytes()==data,relative
  else:path.write_bytes(data)
 for unit in report['results']:
  name=unit['file'];data=(ROOT/name).read_bytes();assert sha(data)==unit['source_sha256'],name
  write(name,data);sources[name]=sha(data)
 project='esp32-cyd2usb-native' if board=='cyd' else 'esp32c3-oled-native'
 # Only code/header/build configuration: never runtime CSV or private storage.
 names=subprocess.check_output(['git','ls-files','idf/components',f'idf/{project}/main','yoRadio/src/audioI2S','yoRadio/src/core'],cwd=ROOT,text=True).splitlines()
 names=[name for name in names if Path(name).suffix.lower() in ('.h','.hpp','.inc') or Path(name).name in ('CMakeLists.txt','Kconfig.projbuild')]
 names+=['.clang-tidy','tools/run_native_lint.py',f'idf/{project}/CMakeLists.txt',f'idf/{project}/sdkconfig.defaults',report['build_dir']+'/compile_commands.json',report['build_dir']+'/sdkconfig',report['build_dir']+'/config/sdkconfig.h']
 for name in sorted(set(names)):
  path=ROOT/name
  if not path.is_file():continue
  data=path.read_bytes();write(name,data);dependencies[name]=dict(sha256=sha(data),mtime_utc=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat())
 assert sha((ROOT/'.clang-tidy').read_bytes())==report['config_sha256']
 manifest=dict(units=sources,dependencies=dependencies,scope='Every reported project translation-unit snapshot exactly matches its report SHA-256; project headers/build inputs also captured after analysis for reproducibility. Header snapshots are current post-analysis bytes, not a claimed pre-analysis capture. SDK/vendor dependency tree is identified by compile database/tool version and target pin, not fully copied here.',source_commit=report['source_commit'])
 target=directory/'source-manifest.json'
 if target.exists():assert json.loads(target.read_text())==manifest
 else:target.write_text(json.dumps(manifest,indent=2)+'\n')
 print(board,len(sources),'exact source hashes,',len(dependencies),'header/build snapshots')
