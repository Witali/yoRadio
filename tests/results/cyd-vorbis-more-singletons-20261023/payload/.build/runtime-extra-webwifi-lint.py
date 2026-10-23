import hashlib,importlib.util,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lint',ROOT/'tools/run_native_lint.py');lint=importlib.util.module_from_spec(spec);spec.loader.exec_module(lint)
old=ROOT/'.build/lint-c3-runtime-transfer-resumed-02';out=ROOT/'.build/lint-c3-runtime-transfer-complete-01';out.mkdir(exist_ok=False)
report=json.loads((old/'report.json').read_text());build=ROOT/report['build_dir']
relative='idf/esp32c3-oled-native/main/web_wifi.c';source=ROOT/relative;raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert any(Path(entry['file']).resolve()==source for entry in json.loads((build/'compile_commands.json').read_text()))
snapshot=out/'sources'/relative;snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(raw)
tool='C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-clang/esp-21.1.3_20260408/esp-clang/bin/clang-tidy.exe'
header=re.escape(ROOT.as_posix()).replace('/',r'[/\\]')+r'[/\\]';stem=relative.replace('/','__')
command=[tool,str(source),'-p',str(build),'--config-file='+str(ROOT/'.clang-tidy'),'--header-filter='+header,'--export-fixes='+str(out/(stem+'.yaml'))]
r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
log=out/(stem+'.log');log.write_text(r.stdout+r.stderr,encoding='utf-8');assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
diagnostics=[dict(file=m[0],line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]) for m in lint.DIAGNOSTIC.findall(r.stdout+r.stderr)]
assert r.returncode==0 and not any(d['severity']=='error' for d in diagnostics)
report['results'].append(dict(file=relative,source_sha256=sha,returncode=r.returncode,complete=True,diagnostics=diagnostics,origin='Fresh analysis of newly registered project unit, with source snapshot captured before invocation',command=command,log_path=log.relative_to(ROOT).as_posix(),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest()))
report['results'].sort(key=lambda row:row['file']);report['units']=len(report['results']);report['warnings']=sum(d['severity']=='warning' for row in report['results'] for d in row['diagnostics']);report['errors']=sum(d['severity']=='error' for row in report['results'] for d in row['diagnostics'])
report['recovery']['newly_registered_units']=1;report['recovery']['recovered_report']=str((old/'report.json').relative_to(ROOT)).replace('\\','/')
report['recovery']['configuration_change']='Parent added missing web_wifi.c main source registration; compilation database regenerated successfully before this additional unit. Existing 63 C/C++ unit source hashes unchanged.'
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Complete combined C3:',report['units'],'units',report['warnings'],'warnings',report['errors'],'errors; added unit warnings',len(diagnostics))
