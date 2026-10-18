"""Run the production OTA sink against pinned image-parser/checksum/SHA code.

Selected SDK functions are extracted verbatim. Only flash/HAL/OTA ownership
and SHA driver adaptation are host seams. Unsigned ESP32/C3 application mode;
no secure-boot, anti-rollback, encryption, device ABI or physical flash claim.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
common=module('ota_common',ROOT/'tests/run-native-ota.py')
tls=module('pinned_crypto',ROOT/'tests/run-native-web-tls.py')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--sdk-root',required=True,type=Path)
    parser.add_argument('--crypto-cache',required=True,type=Path)
    parser.add_argument('--chip',required=True,choices=['esp32','esp32c3'])
    args=parser.parse_args()
    if sys.platform=='win32':
        raise SystemExit(subprocess.call(['wsl.exe','--exec','python3',common.host(__file__),'--output',common.host(args.output),
            '--sdk-root',common.host(args.sdk_root),'--crypto-cache',common.host(args.crypto_cache),'--chip',args.chip]))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    sdk=args.sdk_root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);cache=args.crypto_cache.resolve()
    files=[Path(__file__),ROOT/'tests/run-native-ota.py',ROOT/'tests/run-native-web-tls.py',
        ROOT/'tests/native/native_ota/host.h',ROOT/'tests/native/native_ota/image_host.c',ROOT/'tests/native/native_ota/image_test.c',
        ROOT/'idf/components/native_ota/native_ota_sink.c',ROOT/'idf/components/native_ota/include/native_ota_sink.h']
    sdk_files=[sdk/'components/bootloader_support/include/esp_app_format.h',sdk/'components/esp_app_format/include/esp_app_desc.h',
        sdk/'components/bootloader_support/include/esp_image_format.h',sdk/'components/bootloader_support/src/esp_image_format.c',
        sdk/('components/soc/'+args.chip+'/include/soc/soc.h')]
    hashes={}
    for path in files+sdk_files:
        relative=path.relative_to(ROOT) if path in files else Path('sdk')/path.relative_to(sdk)
        raw=path.read_bytes();hashes[relative.as_posix()]=hashlib.sha256(raw).hexdigest();target=out/'sources'/relative
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    frozen=out/'sources';test=frozen/'tests/native/native_ota';production=frozen/'idf/components/native_ota/native_ota_sink.c'
    for name in ['host.h','image_test.c']:(out/name).write_bytes((test/name).read_bytes())
    (out/'native_ota_sink.h').write_bytes((frozen/'idf/components/native_ota/include/native_ota_sink.h').read_bytes())
    (out/'sdk-app-format.h').write_text(common.strip_includes((frozen/'sdk/components/bootloader_support/include/esp_app_format.h').read_text()))
    (out/'sdk-app-desc.h').write_text(common.strip_includes((frozen/'sdk/components/esp_app_format/include/esp_app_desc.h').read_text()))
    header=(frozen/'sdk/components/bootloader_support/include/esp_image_format.h').read_text()
    (out/'sdk-image-types.inc').write_text(common.typedef(header,'esp_image_metadata_t')+common.typedef(header,'esp_image_load_mode_t'))
    for name in ['esp_err.h','esp_ota_ops.h','esp_app_format.h','esp_app_desc.h','esp_image_format.h']:(out/name).write_text('#include "host.h"\n')
    source=(frozen/'sdk/components/bootloader_support/src/esp_image_format.c').read_text()
    names=['is_bootloader','should_map','should_load','verify_image_header','verify_segment_header','process_image_header',
        'process_segment_data','process_segment','process_segments','process_checksum','process_appended_hash_and_sig',
        'verify_simple_hash','image_load','esp_image_verify','esp_image_get_metadata']
    functions=[tls.function(source,name) for name in names]
    macros=source[source.index('#define FAIL_LOAD'):source.index('static esp_err_t process_image_header',source.index('#define FAIL_LOAD'))]
    (out/'sdk-image-prototypes.inc').write_text(common.typedef(source,'process_segment_data_t')+''.join(f[:f.index('{')].rstrip()+';\n' for f in functions))
    (out/'sdk-image-functions.inc').write_text(macros+''.join(functions))
    addresses=(frozen/('sdk/components/soc/'+args.chip+'/include/soc/soc.h')).read_text()
    (out/'soc-addresses.inc').write_text('\n'.join(next(line for line in addresses.splitlines() if re.match(r'#define\s+'+name+r'\s',line)) for name in ['SOC_DROM_LOW','SOC_DROM_HIGH','SOC_IROM_LOW','SOC_IROM_HIGH'])+'\n')
    # Reuse the existing manual software crypto builder, which hashes every
    # source/header/flag before accepting its cached sanitizer archive.
    command=['python3',str(frozen/'tests/run-native-web-tls.py'),'--build-only','--output',str(out/'crypto-build'),
        '--sdk-root',str(sdk),'--crypto-cache',str(cache),'--jobs','6']
    common.execute(command,out/'crypto-build.log')
    mbed=sdk/'components/mbedtls/mbedtls';crypto=mbed/'tf-psa-crypto'
    flags=['-std=c11','-D_GNU_SOURCE','-O1','-g','-fno-omit-frame-pointer','-fsanitize=address,undefined','-fno-pie','-no-pie',
        '-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter',
        '-DHOST_CHIP='+('0' if args.chip=='esp32' else '5'),'-DCONFIG_IDF_TARGET_ESP32='+('1' if args.chip=='esp32' else '0'),
        '-I'+str(out),'-I'+str(cache/'host-config'),'-I'+str(sdk/'components/mbedtls/port/include'),'-I'+str(mbed/'include'),
        '-I'+str(crypto/'include'),'-I'+str(crypto/'utilities'),'-I'+str(crypto/'core'),'-I'+str(crypto/'drivers/builtin/include')]
    library=cache/'libpinned-mbedtls.a'
    def build_run(name,sink=production):
        binary=out/name;command=['gcc',*flags,str(test/'image_host.c'),str(sink),str(library),'-pthread','-o',str(binary)]
        common.execute(command,out/(name+'-build.log'))
        return common.execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','90',str(binary),str(out/'fixture.bin')],out/(name+'.log'),negative=name!='images')
    log=build_run('images');print(log.decode(),end='')
    fixture=(out/'fixture.bin').read_bytes();assert hashlib.sha256(fixture[:-32]).digest()==fixture[-32:]
    raw=(out/'sdk-image-functions.inc').read_text();negative={}
    mutations={'checksum':('if (!skip_check_checksum && calc_checksum != read_checksum)','if (false)'),
               'sha256':('if (memcmp(data->image_digest, image_hash, HASH_LEN) != 0)','if (false)')}
    for name,(old,new) in mutations.items():
        assert raw.count(old)==1,name
        (out/'sdk-image-functions.inc').write_text(raw.replace(old,new));build_run(name);negative[name]='DETECTED'
    (out/'sdk-image-functions.inc').write_text(raw)
    mutant=out/'no-exact-length.c';text=production.read_text();assert text.count('metadata.image_len != sink->received')==1
    mutant.write_text(text.replace('metadata.image_len != sink->received','false'));build_run('exact-length',mutant);negative['exact-length']='DETECTED'
    report=dict(passed=True,sdk=sdk.name,chip=args.chip,source_sha256=hashes,sanitizers=['ASan','UBSan'],sdk_functions=names,
        groups=int(re.search(rb'(\d+) groups',log)[1]),negative_controls=negative,independent_fixture_sha256='Python hashlib agrees with appended PSA SHA256',
        crypto_archive_sha256=hashlib.sha256(library.read_bytes()).hexdigest(),crypto_build_command=command,
        crypto_identity=json.loads((cache/'identity.json').read_text()),
        scope='Actual production sink plus verbatim selected pinned application-mode image verifier/metadata/segment/checksum/hash functions, actual pinned PSA SHA256. Host partition/OTA ownership/memory flash/read/map/clock-reset/chip-eFuse/log seams; SDK SOC mapped-address constants. Unsigned profiles only: no hardware flash erase/cache/ABI/RAM, secure boot/signature, encryption, anti-rollback or revision qualification.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
