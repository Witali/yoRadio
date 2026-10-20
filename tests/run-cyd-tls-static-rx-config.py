"""Actual canonical-path helper, configure-only project(NONE). No SDK build.

Freeze all 19 guarded SDK files and canonical source overlay, then configure source
copies in their actual intended paths. Verify exact source/options/dependencies
and byte-equal canonical SDK overlay; off/early must not access any SDK input.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/"tests/native/cyd_tls_static_rx"
MAIN=Path('idf/esp32-cyd2usb-native/main')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--sdk',type=Path,required=True)
    p.add_argument('--cmake',type=Path,required=True);p.add_argument('--ninja',type=Path,required=True)
    p.add_argument("--preflight-only",action="store_true");a=p.parse_args()
    out=a.output.resolve();sdk=a.sdk.resolve();overlay=ROOT
    assert out.is_relative_to(ROOT/".build") and not out.exists()
    spec=importlib.util.spec_from_file_location("config_contract",HERE/"source_contract.py");contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    if a.preflight_only:
        assert a.cmake.is_file() and a.ninja.is_file(),"Installed CMake/Ninja required"
        print(json.dumps(contract.preflight(ROOT,sdk)));return
    out.mkdir(parents=True)
    report=dict(passed=False,scope=__doc__,compiler=False,sdk_build=False,qemu=False,inputs={},cases={})
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    def freeze(path,rel):
        dest=out/'inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());report['inputs'][str(path)]={'sha256':sha(path),'snapshot':dest.relative_to(out).as_posix()};return dest
    try:
        freeze(Path(__file__),Path('runner')/Path(__file__).name)
        production=[ROOT/MAIN/n for n in ('native_tls_rx_reserve.c','native_tls_rx_reserve.h','compat/tls_static_rx/enable.cmake','compat/tls_static_rx/sdk-source-guards.json','Kconfig.projbuild')]+[ROOT/'tools/patch_cyd_tls_static_rx.py',HERE/'source_contract.py']
        for f in production:freeze(f,Path('repository')/f.relative_to(ROOT))
        spec=importlib.util.spec_from_file_location('frozen_config_contract',out/'inputs/repository/tests/native/cyd_tls_static_rx/source_contract.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
        report['module_contract']=contract.validate_module(out/'inputs/repository'/MAIN/'native_tls_rx_reserve.c')
        guards=json.loads((overlay/MAIN/'compat/tls_static_rx/sdk-source-guards.json').read_text())
        for relative in guards:freeze(sdk/relative,Path('sdk')/relative)
        report['tools']={str(f.resolve()):sha(f.resolve()) for f in [a.cmake,a.ninja,Path(sys.executable)]}
        cases={
            'canonical':{},'off':{'off':True},'forced-zero':{'off':True,'zero':True},'early':{'early':True},
            'target':{'IDF_TARGET':'esp32c3'},'target-symbol-zero':{'CONFIG_IDF_TARGET_ESP32':'0'},
            'major':{'IDF_VERSION_MAJOR':'7'},'minor':{'IDF_VERSION_MINOR':'1'},'patch':{'IDF_VERSION_PATCH':'3'},'malformed-major':{'IDF_VERSION_MAJOR':'6x'},
            'external':{'CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC':'0'},'custom':{'CONFIG_MBEDTLS_CUSTOM_MEM_ALLOC':'1'},
            'dynamic':{'CONFIG_MBEDTLS_DYNAMIC_BUFFER':'1'},'variable':{'CONFIG_MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH':'1'},
            'tls-zero':{'CONFIG_ESP_TLS_USING_MBEDTLS':'0'},'bundle-zero':{'CONFIG_MBEDTLS_CERTIFICATE_BUNDLE':'0'},
            'short-content':{'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN':'4096'},'serialize':{'CONFIG_MBEDTLS_SSL_CONTEXT_SERIALIZATION':'1'},
            'gmt':{'CONFIG_MBEDTLS_SSL_PROTO_GMTSSL1_1':'1'},'missing-target':{'missing_target':True},
            'source-absent':{'source_absent':True},'source-duplicate':{'source_duplicate':True},
            'missing-module':{'missing':'module'},'missing-header':{'missing':'header'},'missing-patcher':{'missing':'patcher'},'missing-guards':{'missing':'guards'},
        }
        cases.update({'guard-'+str(i):{'guard':relative} for i,relative in enumerate(guards)})
        frozen=out/'inputs'
        for name,variant in cases.items():
            d=out/name;repo=d/'repository';project=d/'project';project.mkdir(parents=True);shutil.copytree(frozen/'repository',repo)
            helper=repo/MAIN/'compat/tls_static_rx/enable.cmake';module=repo/MAIN/'native_tls_rx_reserve.c';header=repo/MAIN/'native_tls_rx_reserve.h';patcher=repo/'tools/patch_cyd_tls_static_rx.py';manifest=repo/MAIN/'compat/tls_static_rx/sdk-source-guards.json'
            inactive=bool(variant.get('off') or variant.get('early'))
            sdk_copy=d/'sdk'
            if not inactive:shutil.copytree(frozen/'sdk',sdk_copy)
            source=sdk_copy/'components/mbedtls/mbedtls/library/ssl_tls.c';sibling=project/'keep.c';sibling.write_text('/* retained sibling */\n')
            if variant.get('guard'):
                f=sdk_copy/variant['guard'];f.write_bytes(f.read_bytes()+b'\n/* mutation guard */\n')
            if variant.get('missing'):{'module':module,'header':header,'patcher':patcher,'guards':manifest}[variant['missing']].unlink()
            settings={'CONFIG_YORADIO_TLS_STATIC_RX_RESERVE':'0' if variant.get('zero') else ('OFF' if variant.get('off') else 'ON'),
                      'CMAKE_BUILD_EARLY_EXPANSION':'ON' if variant.get('early') else 'OFF','IDF_VERSION_MAJOR':'6','IDF_VERSION_MINOR':'0','IDF_VERSION_PATCH':'2',
                      'IDF_TARGET':'esp32','CONFIG_IDF_TARGET_ESP32':'1','CONFIG_ESP_TLS_USING_MBEDTLS':'1','CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC':'1','CONFIG_MBEDTLS_CERTIFICATE_BUNDLE':'1','CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN':'16384','COMPONENT_LIB':'main','PYTHON':Path(sys.executable).as_posix()}
            settings.update({k:v for k,v in variant.items() if k.isupper()})
            if inactive:
                settings.update(IDF_TARGET='invalid',IDF_VERSION_MAJOR='bad',CONFIG_ESP_TLS_USING_MBEDTLS='0',PYTHON='nonexistent-python',COMPONENT_LIB='unregistered')
                for f in [module,header,patcher,manifest]:f.unlink()
            lines=['cmake_minimum_required(VERSION 3.20)','project(CanonicalReserveGate NONE)','add_library(main INTERFACE)','target_link_options(main INTERFACE keep-main)']
            sources=[] if variant.get('source_absent') else [source.as_posix()]
            sources+=[sibling.as_posix()]
            if variant.get('source_duplicate'):sources+=[source.as_posix()]
            if not variant.get('missing_target'):
                lines+=['add_library(mbedtls INTERFACE)','target_link_options(mbedtls INTERFACE keep-sdk)','set_property(TARGET mbedtls PROPERTY SOURCES "'+';'.join(sources)+'")']
                if inactive:lines+=['set_source_files_properties("'+source.as_posix()+'" PROPERTIES GENERATED TRUE)']
            lines+=['set('+k+' "'+v+'")' for k,v in settings.items()]
            lines+=['function(idf_component_get_property destination component property)',('message(FATAL_ERROR "inactive_access_forbidden")' if inactive else 'set(${destination} "'+(sdk_copy/'components/mbedtls').as_posix()+'" PARENT_SCOPE)'),'endfunction()',
                    'include("'+helper.as_posix()+'")','native_enable_tls_static_rx_reserve()',
                    'get_target_property(main_sources main SOURCES)','get_target_property(main_options main INTERFACE_LINK_OPTIONS)',
                    'get_target_property(sdk_sources mbedtls SOURCES)','get_target_property(sdk_options mbedtls INTERFACE_LINK_OPTIONS)',
                    'get_property(dependencies DIRECTORY PROPERTY CMAKE_CONFIGURE_DEPENDS)',
                    'file(WRITE "${CMAKE_BINARY_DIR}/capture.txt" "${main_sources}\\n${main_options}\\n${sdk_sources}\\n${sdk_options}\\n${CMAKE_C_COMPILER}|${CMAKE_CXX_COMPILER}\\n${dependencies}\\n")']
            (project/'CMakeLists.txt').write_text('\n'.join(lines)+'\n')
            before={f.relative_to(d).as_posix():sha(f) for f in d.rglob('*') if f.is_file()}
            cmd=[str(a.cmake.resolve()),'-G','Ninja','-DCMAKE_MAKE_PROGRAM='+a.ninja.resolve().as_posix(),'-S',str(project),'-B',str(d/'build')]
            result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60);log=result.stdout.decode(errors='replace');(d/'configure.log').write_bytes(result.stdout)
            positive=name=='canonical' or inactive
            details={'exit_status':result.returncode,'argv':cmd,'log_sha256':hashlib.sha256(result.stdout).hexdigest()}
            if positive:
                assert result.returncode==0,(name,log)
                capture=(d/'build/capture.txt').read_text().splitlines();generated=d/'build/native-tls-static-rx/ssl_tls.c'
                expected=['main_sources-NOTFOUND' if inactive else (helper.parent/'../../native_tls_rx_reserve.c').as_posix(),'keep-main',';'.join(sources if inactive else [generated.as_posix(),sibling.as_posix()]),'keep-sdk','|']
                assert capture[:5]==expected,(name,capture,expected)
                dependencies=capture[5].split(';') if len(capture)>5 and capture[5] else []
                if inactive:assert not generated.exists() and not dependencies
                else:
                    spec=importlib.util.spec_from_file_location('case_patcher',patcher);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
                    assert generated.read_bytes()==mod.patch(source.read_bytes())
                    expected_dependencies=[source.as_posix(),patcher.as_posix(),manifest.as_posix()]+[(sdk_copy/rel).as_posix() for rel in sorted(guards)]
                    assert dependencies==expected_dependencies,(dependencies,expected_dependencies)
                    details['overlay_sha256']=sha(generated)
                details['exact_capture']=capture
            else:
                if name.startswith('guard-'):expected='CYD static RX overlay rejected SDK'
                elif name.startswith('source-'):expected='Expected exactly one audited static RX source'
                elif name=='missing-header':expected='Missing canonical static RX reserve header'
                elif name.startswith('missing-') and name!='missing-target':expected='Missing canonical static RX reserve inputs'
                elif name=='missing-target':expected='CYD static RX reserve requires registered canonical targets'
                elif name in ['target','target-symbol-zero','major','minor','patch','malformed-major']:expected='CYD static RX reserve requires exact ESP32 IDF6.0.2'
                else:expected='CYD static RX reserve rejects unsupported allocator/buffer/config lifetime'
                assert result.returncode!=0 and expected in log,(name,expected,log)
                details['exact_rejection']=expected
            assert all(sha(d/rel)==identity for rel,identity in before.items())
            details['passed']=True;report['cases'][name]=details;save()
        assert all(sha(Path(path))==entry['sha256'] and sha(out/entry['snapshot'])==entry['sha256'] for path,entry in report['inputs'].items())
        assert all(sha(Path(path))==identity for path,identity in report['tools'].items())
        report['configure_case_count']=len(cases);report['passed']=True;print(str(len(cases))+' canonical path configure cases PASS',flush=True)
    except BaseException as e:report['error']=repr(e);raise
    finally:save()
if __name__=='__main__':main()
