"""Exercise actual TLS input-reclaim CMake guards without compiling a firmware."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
MAIN=Path('idf/esp32-cyd2usb-native/main')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def installed(relative):
    return next((parent/relative for parent in (ROOT,*ROOT.parents) if (parent/relative).is_file()),None)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cmake',type=Path,default=shutil.which('cmake') or installed('.idf/tools-v6.0.2/tools/cmake/4.0.3/bin/cmake.exe'))
    parser.add_argument('--ninja',type=Path,default=shutil.which('ninja') or installed('.idf/tools-v6.0.2/tools/ninja/1.12.1/ninja.exe'))
    args=parser.parse_args()
    if not args.cmake or not args.ninja:parser.error('Installed CMake and Ninja are required')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    inputs=[Path(__file__).resolve().relative_to(ROOT),*[MAIN/name for name in
        ('CMakeLists.txt','Kconfig.projbuild','native_input_reclaim.c','native_input_reclaim.h','compat/input_reclaim/enable.cmake')]]
    report={'passed':False,'scope':__doc__,'source_sha256':{},'cases':{},'physical_hardware':False,'compiled_firmware':False}
    for relative in inputs:
        target=out/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((ROOT/relative).read_bytes())
        report['source_sha256'][relative.as_posix()]=sha(target)
    report['tools']={str(path.resolve()):sha(path.resolve()) for path in (args.cmake,args.ninja)}
    helper=out/'sources'/MAIN/'compat/input_reclaim/enable.cmake'
    module=out/'sources'/MAIN/'native_input_reclaim.c'
    keys=['CONFIG_YORADIO_TLS_INPUT_RECLAIM','CMAKE_BUILD_EARLY_EXPANSION',
          'CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER','CONFIG_ESP_TLS_USING_MBEDTLS',
          'CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC','CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC',
          'CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS']
    scenarios={'enabled':{},'disabled':{keys[0]:False},'early':{keys[1]:True},
        'no-adaptive':{keys[2]:False},'other-tls':{keys[3]:False},
        'external-allocator':{keys[4]:False},'custom-allocator':{keys[5]:True},
        'abort-on-failure':{keys[6]:True}}
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for name,overrides in scenarios.items():
        directory=out/name;project=directory/'project';project.mkdir(parents=True)
        flags=dict(zip(keys,(True,False,True,True,True,False,False)));flags.update(overrides)
        settings='\n'.join('set('+key+' '+('ON' if value else 'OFF')+')' for key,value in flags.items())
        cmake='''cmake_minimum_required(VERSION 3.20)
project(CydInputReclaim NONE)
add_library(reclaim_target INTERFACE)
target_link_options(reclaim_target INTERFACE "-Wl,--undefined=keep_original")
set(COMPONENT_LIB @TARGET@)
@SETTINGS@
include("@HELPER@")
native_enable_tls_input_reclaim()
get_target_property(captured_sources reclaim_target SOURCES)
get_target_property(captured_options reclaim_target INTERFACE_LINK_OPTIONS)
file(WRITE "${CMAKE_BINARY_DIR}/captured.txt" "${captured_sources}\\n${captured_options}\\n")
'''.replace('@TARGET@','absent_target' if name in ('disabled','early') else 'reclaim_target').replace('@SETTINGS@',settings).replace('@HELPER@',helper.as_posix())
        (project/'CMakeLists.txt').write_text(cmake)
        command=[str(args.cmake.resolve()),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+args.ninja.resolve().as_posix(),
                 '-S',project.as_posix(),'-B',(directory/'build').as_posix()]
        (directory/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
        (directory/'configure.log').write_bytes(result.stdout)
        rejected=name not in ('enabled','disabled','early')
        report['cases'][name]={'exit_status':result.returncode,'expected_rejection':rejected,
            'configure_log_sha256':hashlib.sha256(result.stdout).hexdigest()};save()
        if rejected:
            assert result.returncode!=0 and b'TLS input reclaim requires adaptive input' in result.stdout,(name,result.stdout)
        else:
            assert result.returncode==0,(name,result.stdout.decode(errors='replace'))
            sources,options=(directory/'build/captured.txt').read_text().splitlines()
            expected=['-Wl,--undefined=keep_original']
            if name=='enabled':
                assert Path(sources).resolve()==module.resolve(),sources
                expected+=['-Wl,--wrap=esp_mbedtls_mem_calloc','-Wl,--undefined=__wrap_esp_mbedtls_mem_calloc']
            else:assert sources=='captured_sources-NOTFOUND'
            assert options.split(';')==expected,options
        report['cases'][name]['passed']=True;save();print('PASS '+name,flush=True)
    report['inputs_unchanged_after']={name:sha(ROOT/name)==digest for name,digest in report['source_sha256'].items()}
    report['tools_unchanged_after']={name:sha(Path(name))==digest for name,digest in report['tools'].items()}
    assert all(report['inputs_unchanged_after'].values()) and all(report['tools_unchanged_after'].values())
    report['passed']=True;save()

if __name__=='__main__':
    main()
