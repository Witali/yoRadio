import hashlib,json,re,subprocess,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tests/results/native-lint-20261018/shared-credential-focused-final"
OUT.mkdir(parents=True,exist_ok=False)
HEADER=re.escape(ROOT.as_posix()).replace("/",r"[/\\]")+r"[/\\]"
CASES=[("cyd","idf/esp32-cyd2usb-native/build-lint-health","C:/Work/yoRadio/.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe","idf/esp32-cyd2usb-native/main/network_service.c"),("c3","idf/esp32c3-oled-native/build-lint","C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-clang/esp-21.1.3_20260408/esp-clang/bin/clang-tidy.exe","idf/esp32c3-oled-native/main/network_service.c")]
def run(case):
 name,build,tool,source=case
 cmd=[tool,str(ROOT/source),"-p",str(ROOT/build),"--config-file="+str(ROOT/".clang-tidy"),"--header-filter="+HEADER,"--export-fixes="+str(OUT/(name+".yaml"))]
 r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding="utf-8",errors="replace",timeout=180)
 (OUT/(name+".log")).write_text(r.stdout,encoding="utf-8")
 diag=re.findall(r"^.*?:[0-9]+:[0-9]+: (warning|error): .*?$",r.stdout,re.M)
 assert r.returncode==0 and "error" not in diag,r.stdout
 return dict(target=name,file=source,source_sha256=hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),warnings=diag.count("warning"),errors=diag.count("error"),complete=True,command=cmd)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(run,CASES))
shared="idf/components/native_storage/include/credential_line.h"
r=dict(scope="Focused rerun of both network translation units after shared row extraction; full 50/24 unit runs are recorded separately.",results=results,shared_header=shared,shared_header_sha256=hashlib.sha256((ROOT/shared).read_bytes()).hexdigest(),complete=True)
(OUT/"report.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
print(json.dumps(r,indent=2))
