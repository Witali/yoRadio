"""Supplemental focused lint evidence. Does not alter the full lint runner."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[1]
LINT=ROOT/'tools/run_native_lint.py'
spec=importlib.util.spec_from_file_location('native_lint',LINT)
lint=importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)
CONFIG=ROOT/'.clang-tidy'
HEADER_FILTER=re.escape(ROOT.as_posix()).replace('/',r'[/\\]')+r'[/\\]'
CASES=[
    ('c3','idf/esp32c3-oled-native/main/websocket_service.c','idf/esp32c3-oled-native/build-lint-web-transfer',
     'C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-clang/esp-21.1.3_20260408/esp-clang/bin/clang-tidy.exe'),
    ('cyd','idf/esp32-cyd2usb-native/main/websocket_service.c','idf/esp32-cyd2usb-native/build-lint-health',
     'C:/Work/yoRadio/.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe')]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def key(d):return (d['file'].replace('\\','/').lower(),d['column'],d['severity'],d['message'],d['check'])
def added(left,right):
    available=Counter(key(d) for d in right);result=[]
    for d in left:
        k=key(d)
        if available[k]:available[k]-=1
        else:result.append(d)
    return result

def check(case):
    variant,relative,build_relative,tool=case
    path=ROOT/relative;build=ROOT/build_relative;database=build/'compile_commands.json'
    out=ROOT/('.build/ws-lint-http-fallback-'+variant);out.mkdir(exist_ok=False)
    stem=relative.replace('/','__');yaml=out/(stem+'.yaml')
    source_data=path.read_bytes();config_data=CONFIG.read_bytes();database_data=database.read_bytes()
    assert b'HTTPD_400_BAD_REQUEST' in source_data and b'WebSocket upgrade required' in source_data
    entries=json.loads(database_data)
    matches=[e for e in entries if Path(e['file']).resolve()==path]
    assert len(matches)==1,(relative,len(matches))
    for source,destination in [(path,'websocket_service.c'),(CONFIG,'.clang-tidy'),(LINT,'run_native_lint.py'),(Path(__file__),'qualify.py')]:
        shutil.copyfile(source,out/destination)
    (out/'compilation-entry.json').write_text(json.dumps(matches[0],indent=2)+'\n',encoding='utf-8')
    baseline_path=ROOT/('.build/lint-'+variant+'-web-transfer-full/report.json')
    baseline=json.loads(baseline_path.read_text(encoding='utf-8'))
    baseline_result=next(r for r in baseline['results'] if r['file']==relative)
    command=[tool,str(path),'-p',str(build),'--config-file='+str(CONFIG),
             '--header-filter='+HEADER_FILTER,'--export-fixes='+str(yaml)]
    version=subprocess.check_output([tool,'--version'],text=True)
    started=datetime.now(timezone.utc).isoformat()
    try:
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        code=result.returncode;log=result.stdout+result.stderr
    except subprocess.TimeoutExpired as error:
        code=-1;log='Analysis timed out after 180 seconds\n'
        for data in (error.stdout,error.stderr):
            if data:log+=data.decode(errors='replace') if isinstance(data,bytes) else data
    (out/(stem+'.log')).write_text(log,encoding='utf-8')
    diagnostics=[dict(file=m[0],line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]) for m in lint.DIAGNOSTIC.findall(log)]
    current_errors=sum(d['severity']=='error' for d in diagnostics)
    current_warnings=sum(d['severity']=='warning' for d in diagnostics)
    unchanged=path.read_bytes()==source_data and CONFIG.read_bytes()==config_data and database.read_bytes()==database_data
    yaml_written=yaml.is_file()
    if not yaml_written:
        # Preserve absence as evidence, rather than inventing clang-tidy output.
        (out/'export-fixes-status.txt').write_text('clang-tidy produced no export-fixes file.\n',encoding='utf-8')
    report=dict(scope='Supplemental focused clang-tidy after early HTTP 400 fallback fix; historical full reports preserved.',
        tool=version.strip(),tool_path=tool,command=command,command_line=subprocess.list2cmdline(command),cwd=str(ROOT),
        started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),build_dir=build_relative,header_filter=HEADER_FILTER,
        config_sha256=hashlib.sha256(config_data).hexdigest(),compile_commands_sha256=hashlib.sha256(database_data).hexdigest(),
        runner_sha256=sha(LINT),helper_sha256=sha(Path(__file__)),source_sha256=hashlib.sha256(source_data).hexdigest(),
        source_and_configuration_unchanged_during_analysis=unchanged,export_fixes_written=yaml_written,
        units=1,complete=code==0 and current_errors==0 and unchanged,returncode=code,warnings=current_warnings,errors=current_errors,
        diagnostics=diagnostics,warning_checks=dict(Counter(d['check'] for d in diagnostics if d['severity']=='warning')),
        raw_warning_summary=[line for line in log.splitlines() if re.search(r'(warnings? generated|Suppressed .*warnings?)',line)],
        baseline_report=str(baseline_path.relative_to(ROOT)),baseline_report_sha256=sha(baseline_path),
        baseline_source_sha256=baseline_result['source_sha256'],baseline_warnings=sum(d['severity']=='warning' for d in baseline_result['diagnostics']),
        baseline_errors=sum(d['severity']=='error' for d in baseline_result['diagnostics']),
        new_diagnostics=added(diagnostics,baseline_result['diagnostics']),resolved_diagnostics=added(baseline_result['diagnostics'],diagnostics),
        comparison='Diagnostic identity uses file/column/severity/message/check; line shifts alone do not count as new warnings.')
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(variant=variant,complete=report['complete'],warnings=current_warnings,errors=current_errors,
                         new=len(report['new_diagnostics']),resolved=len(report['resolved_diagnostics']),export_fixes_written=yaml_written)),flush=True)
    return report['complete']

with ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(check,CASES))
if not all(results):raise SystemExit(1)
