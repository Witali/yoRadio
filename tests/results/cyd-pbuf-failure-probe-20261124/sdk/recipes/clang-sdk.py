import hashlib,json,os,re,runpy,shutil,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]; DEP=Path('C:/Work/yoRadio/.idf')
def load(p): return json.loads(Path(p).read_bytes())
def pin(p):
 b=Path(p).read_bytes(); return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
backend,shell=sys.argv[1:3]; d=BASE/'sdk'/backend; old=BASE/'sdk-baseline'/backend; row=load(old/'snapshot.json'); candidate=load(BASE/'candidate-inputs.json')
status=d/'clang-status.json'; assert not status.exists()
report=dict(state='RUNNING',source_commit=candidate['source_commit'],children=[])
def save():
 temp=status.with_suffix('.tmp'); temp.write_text(json.dumps(report,indent=2)+'\n'); os.replace(temp,status)
env=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',IDF_COMPONENT_MANAGER='0',SOURCE_DATE_EPOCH=str(row['source_date_epoch']))
def call(name,args,cwd=ROOT):
 with (d/(name+'.stdout.log')).open('xb')as out,(d/(name+'.stderr.log')).open('xb')as err:
  child=subprocess.Popen(list(map(str,args)),cwd=cwd,env=env,stdout=out,stderr=err)
  item=dict(phase=name,pid=child.pid,state='RUNNING'); report['children'].append(item); save(); code=child.wait()
 item.update(state='TERMINAL',exit_status=code); save(); return code
save()
try:
 assert load(d/'build-status.json')['state']=='BUILD_PASS_QUALIFICATION_PENDING'
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==candidate['source_commit']
 for name,value in candidate['sources'].items(): assert pin(ROOT/name)==value
 clang=BASE/'sdk/clang-shared'; clang.mkdir(exist_ok=True); shutil.copyfile(d/'sdkconfig',clang/'sdkconfig')
 defaults='sdkconfig.defaults'+{'pdm':'','continuous':';sdkconfig.dac.defaults','legacy':';sdkconfig.legacy-dac.defaults'}[backend]
 flags=['-D','IDF_TOOLCHAIN=clang','-D','PROJECT_VER='+row['project_version'],'-D','SDKCONFIG_DEFAULTS='+defaults,
 '-D','CMAKE_PROJECT_yoradio_cyd2usb_native_INCLUDE='+str(ROOT/'tests/target/cyd_full_app_openeth_qemu/attach.cmake')]
 for flag in ('PCM_PROBE','PCM_SHA256','RX_BACKOFF','ALLOCATION_PROBE','RTC_ACCESS_PROBE','PBUF_FAILURE_PROBE'): flags+=['-D','CYD_OPENETH_'+flag+'=ON']
 flags+=['reconfigure']
 invocation=dict(schema='cyd-final-production-invocation-v1',script=str(ROOT/'idf/esp32-cyd2usb-native/build.ps1'),parameters=dict(DependencyRoot=str(DEP),AudioBackend=backend,BuildDirectory=str(clang),Sdkconfig=str(clang/'sdkconfig'),IdfArguments=flags))
 inv=d/'clang-invocation.json'; inv.write_text(json.dumps(invocation,indent=2)+'\n')
 assert call('clang-reconfigure',[shell,'-NoLogo','-NoProfile','-File',ROOT/'.build/cyd-final-campaign-20261111-01/invoke-build.ps1','-Invocation',inv])==0
 helpers=runpy.run_path(str(ROOT/'.build/cyd-final-campaign-20261111-01/campaign.py'))
 delta=helpers['delta'](load(d/'compiled/config/sdkconfig.json'),load(clang/'config/sdkconfig.json'))
 assert delta==load(ROOT/'.build/cnortc24'/backend/'compiler-config-delta.json')
 assert load(clang/'config/sdkconfig.json')==load(ROOT/'.build/cnortc24'/backend/'compiled/clang/config/sdkconfig.json')
 assert (clang/'config/sdkconfig.h').read_bytes()==(ROOT/'.build/cnortc24'/backend/'compiled/clang/config/sdkconfig.h').read_bytes()
 (d/'compiler-config-delta.json').write_text(json.dumps(delta,indent=2)+'\n')
 frozen=d/'compiled/clang'
 for name in ('sdkconfig','config/sdkconfig.json','config/sdkconfig.h','compile_commands.json'):
  p=frozen/name; p.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(clang/name,p)
 entries=load(clang/'compile_commands.json'); marker='-DCYD_OPENETH_PBUF_FAILURE_PROBE=1'
 original=BASE/'source-before'; original.mkdir(exist_ok=True)
 pcm=original/'pcm.c'
 if not pcm.exists():
  body=subprocess.check_output(['git','show','035dea9149bbaa228303f89489f9f6efa8d671ae:tests/target/cyd_full_app_openeth_qemu/pcm.c'],cwd=ROOT)
  expected,=[x for x in row['project_units']if Path(x['file']).name=='pcm.c']
  assert dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())==dict(bytes=expected['bytes'],sha256=expected['sha256'])
  pcm.write_bytes(body)
 tidy=DEP/'tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe'
 pattern=re.compile(r'^(.*?):(\d+):(\d+): (warning|error): (.*?)(?: \[([^\]]+)\])?$',re.M)
 results=[]
 for label,name in (('pcm-before','pcm.c'),('pcm','pcm.c'),('pbuf-probe','pbuf_failure.c')):
  entry,=[x for x in entries if Path(x['file']).name==name]; output=d/('lint-'+label); output.mkdir()
  unit=Path(entry['file'])
  if label=='pcm-before':
   args=helpers['entry_tokens'](entry); args=[x for x in args if x!=marker]; args=[str(pcm)if x==entry['file']else x for x in args]
   assert str(pcm)in args
   unit=pcm; entry=dict(directory=entry['directory'],arguments=args,file=str(unit),output=entry['output'])
   (output/'compile_commands.json').write_text(json.dumps([entry],indent=2)+'\n'); database=output
  else: database=clang
  filters=re.escape(ROOT.as_posix()).replace('/',r'[/\\]')+r'[/\\]'
  code=call('tidy-'+label,[tidy,unit,'-p',database,'--config-file='+str(ROOT/'.clang-tidy'),'--header-filter='+filters,'--export-fixes='+str(output/'fixes.yaml')],entry['directory'])
  text=(d/('tidy-'+label+'.stdout.log')).read_text(errors='replace')+(d/('tidy-'+label+'.stderr.log')).read_text(errors='replace')
  diagnostics=[]
  for m in pattern.findall(text):
   file='tests/target/cyd_full_app_openeth_qemu/pcm.c'if Path(m[0]).resolve()==unit.resolve()and name=='pcm.c'else m[0]
   diagnostics.append(dict(file=file,line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]))
  result=dict(unit=label,whole_tu=True,source=pin(unit),returncode=code,diagnostics=diagnostics,warnings=sum(x['severity']=='warning'for x in diagnostics),errors=sum(x['severity']=='error'for x in diagnostics),clang_tidy=pin(tidy))
  (output/'report.json').write_text(json.dumps(result,indent=2)+'\n'); assert code==0 and result['errors']==0
  results.append(result)
 from collections import Counter
 catalog=lambda r:Counter((x['file'],x['severity'],x['message'],x['check'])for x in r['diagnostics'])
 assert catalog(results[0])==catalog(results[1]),'New PCM warnings require review'
 assert results[2]['warnings']==0,'New probe warnings require review; no suppressions applied'
 sdk=[]; old_clang=load(ROOT/'.build/cnortc24'/backend/'compiled/clang/compile_commands.json')
 for name in ('pbuf.c','tcp_out.c'):
  entry,=[x for x in entries if Path(x['file']).name==name]; previous,=[x for x in old_clang if Path(x['file']).name==name]
  now=helpers['entry_tokens'](entry); before=helpers['entry_tokens'](previous)
  before=[x.replace(str(previous['directory']),str(entry['directory'])).replace(str(previous['directory']).replace('/','\\'),str(entry['directory']).replace('/','\\'))for x in before]
  assert now==before,'SDK frontend command differs from actual prior same-config command'
  code=call('sdk-'+name,helpers['frontend_args'](entry)+['-fsyntax-only'],entry['directory']); assert code==0
  sdk.append(dict(unit=name,source=pin(Path(entry['file'])),baseline_command_equivalent=True,config_header_identical=True,exit_status=code,stderr=pin(d/('sdk-'+name+'.stderr.log'))))
 report.update(state='TERMINAL_PASS',results=[dict(unit=x['unit'],warnings=x['warnings'],errors=x['errors'])for x in results],sdk_frontends=sdk,typed_config_delta=delta)
except Exception as error:
 report.update(state='TERMINAL_NONPASS',failure=str(error)); raise
finally: save()
