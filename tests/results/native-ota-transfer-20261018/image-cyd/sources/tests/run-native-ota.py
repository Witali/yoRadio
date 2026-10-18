"""Qualify the actual shared OTA image sink with pinned SDK image layouts.

SDK operations are fault seams. Pinned image verifier qualification is a
separate runner. No device is accessed; --output retains all generated evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
TEST=ROOT/'tests/native/native_ota'
COMPONENT=ROOT/'idf/components/native_ota'

def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value

def execute(command,log,negative=False):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
    log.write_bytes(result.stdout)
    if negative:
        assert result.returncode and b'Assertion' in result.stdout,result.stdout.decode(errors='replace')
    elif result.returncode:
        raise RuntimeError(result.stdout.decode(errors='replace'))
    return result.stdout

def strip_includes(text):return re.sub(r'^\s*#\s*include[^\n]*\n','',text,flags=re.M)
def typedef(source,name):
    match=re.search(r'typedef\s+(?:struct|enum)\s*\{[^{}]*\}\s*'+name+r'\s*;',source,re.S)
    assert match,name
    return match[0]+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--sdk-root',type=Path,required=True)
    args=parser.parse_args()
    if sys.platform=='win32':
        command=['wsl.exe','--exec','python3',host(__file__),'--output',host(args.output),'--sdk-root',host(args.sdk_root)]
        raise SystemExit(subprocess.call(command))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    sdk=args.sdk_root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),TEST/'host.h',TEST/'sink_test.c',COMPONENT/'native_ota_sink.c',COMPONENT/'include/native_ota_sink.h',COMPONENT/'CMakeLists.txt']
    sdk_files=[sdk/'components/bootloader_support/include/esp_app_format.h',sdk/'components/esp_app_format/include/esp_app_desc.h',sdk/'components/bootloader_support/include/esp_image_format.h']
    hashes={}
    for file in files+sdk_files:
        relative=file.relative_to(ROOT) if file in files else Path('sdk')/file.relative_to(sdk)
        data=file.read_bytes();hashes[relative.as_posix()]=hashlib.sha256(data).hexdigest()
        target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    frozen=out/'sources'
    (out/'sdk-app-format.h').write_text(strip_includes((frozen/'sdk/components/bootloader_support/include/esp_app_format.h').read_text()))
    (out/'sdk-app-desc.h').write_text(strip_includes((frozen/'sdk/components/esp_app_format/include/esp_app_desc.h').read_text()))
    image_header=(frozen/'sdk/components/bootloader_support/include/esp_image_format.h').read_text()
    (out/'sdk-image-types.inc').write_text(typedef(image_header,'esp_image_metadata_t')+typedef(image_header,'esp_image_load_mode_t'))
    for name in ['esp_err.h','esp_ota_ops.h','esp_app_format.h','esp_app_desc.h','esp_image_format.h']:(out/name).write_text('#include "host.h"\n')
    (out/'native_ota_sink.h').write_bytes((frozen/'idf/components/native_ota/include/native_ota_sink.h').read_bytes())
    (out/'host.h').write_bytes((frozen/'tests/native/native_ota/host.h').read_bytes())
    flags=['-std=c11','-D_GNU_SOURCE','-O1','-g','-fno-omit-frame-pointer','-fsanitize=address,undefined','-fno-pie','-no-pie',
        '-Wall','-Wextra','-Werror','-Wno-unused-function','-I'+str(out)]
    production=frozen/'idf/components/native_ota/native_ota_sink.c';test=frozen/'tests/native/native_ota/sink_test.c'
    def build_run(name,source,negative=False):
        binary=out/name
        execute(['gcc',*flags,str(test),str(source),'-o',str(binary)],out/(name+'-build.log'))
        return execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','60',str(binary)],out/(name+'.log'),negative)
    log=build_run('sink',production);print(log.decode(),end='')
    mutations={
        'chip-policy':('header.chip_id != sink->policy.expected_chip ||',''),
        'maintenance-order':('if (sink->policy.before_flash(sink->policy.context) != ESP_OK)','if (false)'),
        'ended-handle':('sink->started = false; // Public SDK contract','sink->started = true; // Public SDK contract'),
        'exact-length':('metadata.image_len != sink->received','false'),
        'size-cap':('size > sink->limit - sink->received','false')}
    negative={}
    raw=production.read_text()
    for name,(old,new) in mutations.items():
        assert raw.count(old)==1,name
        mutant=out/(name+'.c');mutant.write_text(raw.replace(old,new))
        build_run(name,mutant,True);negative[name]='DETECTED'
    report=dict(passed=True,sdk=sdk.name,compiler=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],
        source_sha256=hashes,sanitizers=['ASan','UBSan'],fault_groups=int(re.search(rb'(\d+) groups',log)[1]),negative_controls=negative,
        fault_scope='Actual production sink and verbatim pinned SDK public image layouts; OTA flash/lifecycle and image verification fault seams. No device operations or target RAM/ABI claim.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
