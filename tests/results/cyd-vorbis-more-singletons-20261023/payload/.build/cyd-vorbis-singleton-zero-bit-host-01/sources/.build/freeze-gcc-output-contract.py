import hashlib,json,re,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'.build/gcc-output-contract-final';out.mkdir(exist_ok=False)
header='idf/components/native_storage/include/web_multipart.h'
old=root/'tests/results/native-web-transfer-20261018/multipart/sources'/header
new=root/header
for folder,path in [('baseline',old),('current',new)]:
    target=out/folder/'web_multipart.h';target.parent.mkdir();shutil.copyfile(path,target)
for label,stem in [('baseline','web-production-c3'),('current','c3-web-multipart-gcc-objects')]:
    for suffix in ['out.log','err.log']:
        shutil.copyfile(root/'.build'/f'{stem}.{suffix}',out/f'{label}-{suffix}')
errors=[line for line in (out/'baseline-out.log').read_text(errors='replace').splitlines() if 'error:' in line]
assert len(errors)==3 and all('uninitialized' in line for line in errors)
current=(out/'current-out.log').read_text(errors='replace')
assert 'error:' not in current and '__idf_esp_http_server' in current
compiler=root/'.idf-absent'
description=json.loads((root/'idf/esp32c3-oled-native/build-c3-transfer/project_description.json').read_text())
report={'passed':True,'scope':'GCC15 ESP32-C3 component build before/after multipart output-contract refactor; original full application build failed, no app image qualification in this report.',
        'baseline_commit':'742d081f','baseline_build_passed':False,'baseline_compiler_errors':errors,
        'baseline_header_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
        'source_sha256':{header:hashlib.sha256(new.read_bytes()).hexdigest()},
        'current_gcc_component_build_passed':True,'compiler':description['c_compiler'],
        'compiler_sha256':hashlib.sha256(Path(description['c_compiler']).read_bytes()).hexdigest(),
        'current_command':'idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory build-c3-transfer -Sdkconfig build-c3-transfer/sdkconfig -IdfArguments @(-D,IDF_TOOLCHAIN=gcc,__idf_main,__idf_native_web_transport,__idf_esp_http_server)',
        'interpretation':'Original successful helper paths assigned both outputs; GCC did not correlate separate found flag with the range. Initialize both outputs and use the output pointer as found predicate; diagnostics remain enabled.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('Frozen original GCC errors and passing production component build')
