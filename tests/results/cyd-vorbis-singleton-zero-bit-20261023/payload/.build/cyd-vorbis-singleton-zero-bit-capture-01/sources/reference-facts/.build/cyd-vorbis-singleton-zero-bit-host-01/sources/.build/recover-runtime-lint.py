"""Preserve interrupted logs and resume only units without confirmed completion."""
import concurrent.futures,datetime,hashlib,importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lint',ROOT/'tools/run_native_lint.py')
lint=importlib.util.module_from_spec(spec);spec.loader.exec_module(lint)
old=ROOT/'.build/lint-c3-runtime-transfer-full'
out=ROOT/'.build/lint-c3-runtime-transfer-resumed-02';out.mkdir(exist_ok=False)
build=ROOT/'idf/esp32c3-oled-native/build-lint-web-transfer'
inventory=json.loads((ROOT/'.build/runtime-lint-recovery-inventory.json').read_text())
tool=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-clang/esp-21.1.3_20260408/esp-clang/bin/clang-tidy.exe')
header=re.escape(ROOT.as_posix()).replace('/',r'[/\\]')+r'[/\\]'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head=='3f1da5f4843e744634a9e21167d6d31aeed9befd'
frozen=json.loads((ROOT/'.build/native-wifi-legacy-io-02/report.json').read_text())['source_sha256']
def digest(data):return hashlib.sha256(data).hexdigest()
def snap(dest,relative,data):
 p=dest/'sources'/relative;p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data
 else:p.write_bytes(data)
def stem(relative):
 p=ROOT/relative
 return 'httpd_overlay__'+p.name if p.parent==build/'native-httpd-rfc6455' else relative.replace('/','__')
pending=[];results=[]
for item in inventory['units']:
 relative=item['file'];p=ROOT/relative;data=p.read_bytes();assert digest(data)==item['source_sha256']
 snap(out,relative,data)
 generated=p.parent==build/'native-httpd-rfc6455'
 if generated:proof='Generated HTTPD overlay snapshot; original file mtime predates persisted log'
 else:
  committed=subprocess.check_output(['git','show',head+':'+relative],cwd=ROOT)
  if committed==data:proof='Exact source bytes in recorded campaign HEAD'
  elif committed==data.replace(b'\r\n',b'\n'):proof='Recorded campaign HEAD blob with standard checkout CRLF conversion; exact analyzed checkout bytes frozen in this report'
  else:
   assert relative.endswith('/web_upload.c') and frozen[relative]==digest(data),relative
   snap(out,'frozen-pre-analysis/'+relative,(ROOT/'.build/native-wifi-legacy-io-02/sources'/relative).read_bytes())
   assert (out/'sources/frozen-pre-analysis'/relative).read_bytes()==data
   proof='Uncommitted upload candidate byte-identical to complete pre-analysis -02 frozen source/report'
 confirmed=item['recorded'] and item['has_log'] and item['recorded']['returncode']==0 and not item['recorded']['errors']
 row=dict(file=relative,source_sha256=digest(data),source_proof=proof,source_mtime_utc=datetime.datetime.fromtimestamp(item['source_mtime'],datetime.timezone.utc).isoformat())
 if confirmed:
  assert item['source_mtime']<=item['log_mtime'],relative
  log=(old/(stem(relative)+'.log')).read_text(encoding='utf-8')
  diag=[dict(file=m[0],line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]) for m in lint.DIAGNOSTIC.findall(log)]
  assert len([d for d in diag if d['severity']=='warning'])==item['recorded']['warnings'],relative
  assert not any(d['severity']=='error' for d in diag)
  row.update(returncode=0,complete=True,diagnostics=diag,origin='Recovered persisted successful exit and original log',log_path=(old/(stem(relative)+'.log')).relative_to(ROOT).as_posix(),log_sha256=digest((old/(stem(relative)+'.log')).read_bytes()))
  results.append(row)
 else:pending.append(row)
def check(row):
 relative=row['file'];command=[str(tool),str(ROOT/relative),'-p',str(build),'--config-file='+str(ROOT/'.clang-tidy'),'--header-filter='+header,'--export-fixes='+str(out/(stem(relative)+'.yaml'))]
 r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
 path=out/(stem(relative)+'.log');path.write_text(r.stdout+r.stderr,encoding='utf-8')
 diag=[dict(file=m[0],line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]) for m in lint.DIAGNOSTIC.findall(r.stdout+r.stderr)]
 assert digest((ROOT/relative).read_bytes())==row['source_sha256']
 row.update(returncode=r.returncode,complete=r.returncode==0 and not any(d['severity']=='error' for d in diag),diagnostics=diag,origin='Fresh resume: missing original log/exit',command=command,log_path=path.relative_to(ROOT).as_posix(),log_sha256=digest(path.read_bytes()))
 print(relative+': exit='+str(r.returncode)+', warnings='+str(sum(d['severity']=='warning' for d in diag)),flush=True)
 return row
print('Recovering '+str(len(results))+' confirmed units; rerunning only '+str(len(pending))+' unconfirmed units',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results.extend(pool.map(check,pending))
report=dict(tool=subprocess.check_output([str(tool),'--version'],text=True).strip(),build_dir=build.relative_to(ROOT).as_posix(),include_httpd_overlay=True,config_sha256=digest((ROOT/'.clang-tidy').read_bytes()),source_commit=head,dirty=True,units=len(results),complete=all(r['complete'] for r in results),results=sorted(results,key=lambda r:r['file']),recovery=dict(original_directory=old.relative_to(ROOT).as_posix(),persisted_exit_log='.build/runtime-analysis-c3.out.log',reused_units=len(results)-len(pending),resumed_units=len(pending),scope='Original interrupted run has no final source-hash report. Attribution reconstructed from unchanged HEAD bytes, matching pre-analysis frozen upload candidate, and source mtimes preceding original completed logs. This is not a pre-analysis snapshot of the complete original run. Missing units analyzed now; old evidence never overwritten.'))
report['warnings']=sum(d['severity']=='warning' for r in results for d in r['diagnostics']);report['errors']=sum(d['severity']=='error' for r in results for d in r['diagnostics'])
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Recovered complete='+str(report['complete'])+': '+str(report['units'])+' units, '+str(report['warnings'])+' warnings, '+str(report['errors'])+' errors',flush=True)
