import json,re,subprocess,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]
backend=sys.argv[1]; d=BASE/'sdk'/backend; clang=BASE/'sdk/clang-shared'
load=lambda p:json.loads(Path(p).read_bytes())
assert load(d/'clang-status.json')['state']=='TERMINAL_PASS'
assert load(clang/'config/sdkconfig.json')==load(d/'compiled/clang/config/sdkconfig.json')
entry,=[x for x in load(clang/'compile_commands.json')if Path(x['file']).name=='pbuf_failure.c']
tidy='C:/Work/yoRadio/.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe'
with (d/'tidy-pbuf-system-inclusive.stdout.log').open('xb')as out,(d/'tidy-pbuf-system-inclusive.stderr.log').open('xb')as err:
 code=subprocess.run([tidy,entry['file'],'-p',str(clang),'--config-file='+str(ROOT/'.clang-tidy'),'--header-filter=.*','--system-headers'],cwd=entry['directory'],stdout=out,stderr=err).returncode
text=(d/'tidy-pbuf-system-inclusive.stdout.log').read_text(errors='replace')+(d/'tidy-pbuf-system-inclusive.stderr.log').read_text(errors='replace')
pattern=re.compile(r'^(.*?):(\d+):(\d+): (warning|error): (.*?)(?: \[([^\]]+)\])?$',re.M)
sites=[dict(file=m[0],line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5])for m in pattern.findall(text)]
report=dict(returncode=code,scope='Additional all-header report, including system headers, with unchanged repository checks; existing SDK diagnostics retained.',
 diagnostics=sites,warnings=sum(x['severity']=='warning'for x in sites),errors=sum(x['severity']=='error'for x in sites))
assert code==0 and report['errors']==0
assert all(not Path(x['file']).resolve().is_relative_to(ROOT)for x in sites),'Project warning unexpectedly appeared in full-header report'
(d/'lint-pbuf-system-inclusive.json').write_text(json.dumps(report,indent=2)+'\n')
print('SYSTEM-INCLUSIVE SDK HEADER WARNINGS',report['warnings'],'errors',report['errors'])
