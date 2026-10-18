"""Qualify final audio units after the frozen complete lint checkpoint."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--board',choices=('cyd','c3'),required=True)
a=p.parse_args();board=a.board
project='esp32c3-oled-native' if board=='c3' else 'esp32-cyd2usb-native'
build=root/'idf'/project/('build-lint-web-transfer' if board=='c3' else 'build-lint-health')
tool=Path('C:/Work/yoRadio/.idf')/('tools-v6.1/tools/esp-clang/esp-21.1.3_20260408' if board=='c3' else 'tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829')/'esp-clang/bin/clang-tidy.exe'
out=root/f'.build/ota-audio-lint-{board}-publication';out.mkdir(parents=True,exist_ok=False)
source=root/'idf'/project/'main/audio_service.c'
inputs=[Path(__file__),source,*[source.parent/n for n in ('audio_service.h','native_state.h','native_audio_output.h')],root/'.clang-tidy']
hashes={}
for path in inputs:
    raw=path.read_bytes();relative=path.relative_to(root).as_posix();hashes[relative]=hashlib.sha256(raw).hexdigest()
    destination=out/'sources'/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
header_filter=re.escape(root.as_posix()).replace('/',r'[/\\]')+r'[/\\]'
command=[str(tool),str(source),'-p',str(build),'--config-file='+str(root/'.clang-tidy'),'--header-filter='+header_filter,'--export-fixes='+str(out/'diagnostics.yaml')]
result=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
(out/'analysis.log').write_bytes(result.stdout)
diagnostic=re.compile(r'^(.*?):(\d+):(\d+): (warning|error): (.*?)(?: \[([^\]]+)\])?$',re.M)
diagnostics=[dict(file=m[0],line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]) for m in diagnostic.findall(result.stdout.decode(errors='replace'))]
for relative,expected in hashes.items():assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==expected,relative
baseline=json.loads((root/f'.build/lint-{board}-ota-transfer-full/report.json').read_text())
previous=next(u for u in baseline['results'] if u['file']==source.relative_to(root).as_posix())
previous_keys={(d['message'],d['check']) for d in previous['diagnostics']}
report={'passed':result.returncode==0 and not any(d['severity']=='error' for d in diagnostics),'board':board,'source_sha256':hashes,'source_stable_during_analysis':True,'command':command,'diagnostics':diagnostics,'new_diagnostic_signatures':[d for d in diagnostics if (d['message'],d['check']) not in previous_keys],'complete_report_sha256':hashlib.sha256((root/f'.build/lint-{board}-ota-transfer-full/report.json').read_bytes()).hexdigest(),'sdkconfig_sha256':hashlib.sha256((build/'sdkconfig').read_bytes()).hexdigest(),'scope':'Final changed audio unit after complete project/overlay analysis. Compilation database and target headers from the pinned Clang SDK profile; no production GCC or physical runtime claim.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['passed'],result.stdout.decode(errors='replace')
print(json.dumps({'passed':True,'board':board,'warnings':len(diagnostics),'new':len(report['new_diagnostic_signatures'])}))
