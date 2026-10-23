import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
build=ROOT/'idf/esp32c3-oled-native/build-lint-web-transfer'
out=ROOT/'.build/lint-c3-runtime-transfer-full'
entries=json.loads((build/'compile_commands.json').read_text())
files=set()
for entry in entries:
 p=Path(entry['file']); p=(p if p.is_absolute() else Path(entry['directory'])/p).resolve()
 if p.suffix.lower() not in ('.c','.cc','.cpp','.cxx') or not p.is_relative_to(ROOT):continue
 relative=p.relative_to(ROOT)
 overlay=p.parent==build/'native-httpd-rfc6455' and p.name in ('httpd_ws.c','httpd_parse.c')
 if not overlay and any(x.startswith(('build','.')) for x in relative.parts[:-1]):continue
 files.add(p)
recorded={m[0]:dict(returncode=int(m[1]),warnings=int(m[2]),errors=int(m[3])) for m in re.findall(r'^(.*?): exit=(-?\d+), warnings=(\d+), errors=(\d+)$',(ROOT/'.build/runtime-analysis-c3.out.log').read_text(),re.M)}
details=[]
for p in sorted(files):
 rel=p.relative_to(ROOT).as_posix();stem='httpd_overlay__'+p.name if p.parent==build/'native-httpd-rfc6455' else rel.replace('/','__');log=out/(stem+'.log')
 details.append(dict(file=rel,recorded=recorded.get(rel),has_log=log.is_file(),has_yaml=(out/(stem+'.yaml')).is_file(),source_mtime=p.stat().st_mtime,log_mtime=log.stat().st_mtime if log.is_file() else None,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
report=dict(expected=len(files),recorded=len(recorded),units=details,unexpected=sorted(set(recorded)-{p.relative_to(ROOT).as_posix() for p in files}))
(ROOT/'.build/runtime-lint-recovery-inventory.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='units'},indent=2))
print('UNCONFIRMED',json.dumps([x for x in details if not x['recorded'] or not x['has_log'] or x['recorded']['returncode']!=0],indent=2))
print('MODIFIED AFTER LOG',json.dumps([x for x in details if x['log_mtime'] and x['source_mtime']>x['log_mtime']],indent=2))
