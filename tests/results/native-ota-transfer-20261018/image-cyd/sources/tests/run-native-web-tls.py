"""Build pinned software MbedTLS and qualify actual native transport over TLS.

No packages are installed. SDK server/public ESP-TLS functions are extracted
verbatim; host ABI/log/error-tracker/client-only seams are explicitly recorded.
Credentials exist only in a temporary directory outside the evidence output.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
TEST=ROOT/'tests/native/native_web_transport'
MODULE=ROOT/'idf/components/native_web_transport'


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def execute(command,log):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_bytes(result.stdout)
    if result.returncode:
        print(result.stdout.decode(errors='replace'),file=sys.stderr)
        raise RuntimeError('Failed command: '+command[0]+' (see '+str(log)+')')
    return result.stdout


def function(source,name):
    match=re.search(r'^[A-Za-z_][^\n;{}]*\b'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',source,re.M)
    assert match,name
    opening=source.index('{',match.start());depth=1;position=opening+1;state='code'
    while depth:
        char=source[position];following=source[position:position+2]
        if state=='line':
            if char=='\n':state='code'
        elif state=='block':
            if following=='*/':state='code';position+=1
        elif state in ('string','char'):
            if char=='\\':position+=1
            elif char==('"' if state=='string' else "'"):state='code'
        elif following=='//':state='line';position+=1
        elif following=='/*':state='block';position+=1
        elif char=='"':state='string'
        elif char=="'":state='char'
        elif char=='{':depth+=1
        elif char=='}':depth-=1
        position+=1
    return source[match.start():position]+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--sdk-root',type=Path,required=True)
    parser.add_argument('--crypto-cache',type=Path,required=True)
    parser.add_argument('--jobs',type=int,default=6)
    parser.add_argument('--build-only',action='store_true')
    args=parser.parse_args()
    if sys.platform=='win32':
        command=['wsl.exe','--exec','python3',host(__file__),'--output',host(args.output),
            '--sdk-root',host(args.sdk_root),'--crypto-cache',host(args.crypto_cache),'--jobs',str(args.jobs)]
        if args.build_only:command.append('--build-only')
        raise SystemExit(subprocess.call(command))
    import resource
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    sdk=args.sdk_root.resolve();mbed=sdk/'components/mbedtls/mbedtls';crypto=mbed/'tf-psa-crypto'
    cache=args.crypto_cache.resolve();cache.mkdir(parents=True,exist_ok=True)
    host_config=cache/'host-config';host_config.mkdir(exist_ok=True)
    (host_config/'sdkconfig.h').write_text('/* Host software configuration: ESP hardware extensions disabled. */\n')
    includes=[host_config,sdk/'components/mbedtls/port/include',mbed/'include',mbed/'library',crypto/'include',crypto/'core',crypto/'dispatch',crypto/'utilities',crypto/'extras',
        crypto/'platform',crypto/'drivers/builtin/include',crypto/'drivers/builtin/src',
        crypto/'drivers/everest/include',crypto/'drivers/everest/include/tf-psa-crypto/private/everest',
        crypto/'drivers/everest/include/tf-psa-crypto/private/everest/kremlib',
        crypto/'drivers/p256-m/p256-m/include',crypto/'drivers/p256-m/p256-m/include/p256-m',
        crypto/'drivers/p256-m/p256-m_driver_interface',crypto/'drivers/pqcp/include',crypto/'drivers/pqcp/src',
        crypto/'drivers/pqcp/mldsa-native/mldsa']
    vendor_sources=[]
    for directory in [mbed/'library',crypto/'core',crypto/'utilities',crypto/'platform',crypto/'extras',crypto/'drivers/builtin/src',
            crypto/'drivers/everest/library',crypto/'drivers/pqcp/src']:
        vendor_sources+=sorted(directory.glob('*.c'))
    vendor_sources += [crypto/'drivers/p256-m/p256-m_driver_entrypoints.c',crypto/'drivers/p256-m/p256-m/p256-m.c']
    for file in vendor_sources:assert file.is_file(),file
    vendor_files=set(vendor_sources)
    for directory in includes:
        if directory!=host_config:vendor_files.update(directory.rglob('*.h'))
    vendor_hashes={file.relative_to(sdk).as_posix():hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(vendor_files)}
    compiler=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]
    flags=['-std=c11','-D_GNU_SOURCE','-O1','-g','-fno-omit-frame-pointer','-fsanitize=address,undefined',
        '-fno-pie','-ffunction-sections','-fdata-sections',*('-I'+str(path) for path in includes)]
    fingerprint=hashlib.sha256(json.dumps([vendor_hashes,compiler,flags],sort_keys=True).encode()).hexdigest()
    identity=cache/'identity.json';library=cache/'libpinned-mbedtls.a'
    cached=identity.is_file() and library.is_file() and json.loads(identity.read_text()).get('fingerprint')==fingerprint
    if not cached:
        objects=cache/'objects';objects.mkdir(exist_ok=True)
        def compile_one(file):
            stem=hashlib.sha256(file.relative_to(sdk).as_posix().encode()).hexdigest()[:12]
            obj=objects/(file.stem+'-'+stem+'.o');log=objects/(obj.stem+'.log')
            execute(['gcc',*flags,'-c',str(file),'-o',str(obj)],log);return obj
        compiled=[]
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            pending={pool.submit(compile_one,file):file for file in vendor_sources}
            for future in as_completed(pending):compiled.append(future.result())
        execute(['ar','rcs',str(library),*(str(file) for file in sorted(compiled))],cache/'archive.log')
        identity.write_text(json.dumps({'fingerprint':fingerprint,'compiler':compiler,'source_count':len(vendor_sources)},indent=2)+'\n')
    (out/'vendor-source-sha256.json').write_text(json.dumps(vendor_hashes,indent=2)+'\n')
    report={'passed':False,'compiler':compiler,'sdk':sdk.name,'crypto_source_count':len(vendor_sources),
        'crypto_fingerprint':fingerprint,'crypto_cache_used':cached,'sanitizers':['ASan','UBSan'],
        'openssl_client':subprocess.check_output(['python3','-c','import ssl;print(ssl.OPENSSL_VERSION)'],text=True).strip(),
        'physical_hardware':False,'private_key_container':'Qualified unencrypted RSA PKCS1 PEM; matching PKCS8 explicitly rejected'}
    if args.build_only:
        report['build_only']=True;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Built pinned MbedTLS: '+str(len(vendor_sources))+' source files');return
    files=[Path(__file__),TEST/'esp_tls_host.c',TEST/'tls_client.py',MODULE/'native_web_transport.c',MODULE/'include/native_web_transport.h',MODULE/'tools/pack_tls_bundle.py']
    sdk_files=[sdk/'components/esp-tls'/name for name in ['esp_tls.c','esp_tls_mbedtls.c','esp_tls.h','esp_tls_errors.h',
        'private_include/esp_tls_private.h','private_include/esp_tls_mbedtls.h']]
    unified_key_config=sdk/'components/esp_security/include/esp_key_config.h'
    if unified_key_config.is_file():sdk_files.append(unified_key_config)
    hashes={}
    for file in files+sdk_files:
        relative=file.relative_to(ROOT) if file in files else Path('sdk')/file.relative_to(sdk)
        data=file.read_bytes();hashes[relative.as_posix()]=hashlib.sha256(data).hexdigest()
        destination=out/'sources'/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(data)
    frozen=out/'sources';source=(frozen/'sdk/components/esp-tls/esp_tls_mbedtls.c').read_text()
    core=(frozen/'sdk/components/esp-tls/esp_tls.c').read_text()
    backend=['esp_mbedtls_cleanup','set_ca_cert','set_pki_context','set_server_config','esp_create_mbedtls_handle',
        'esp_mbedtls_get_ssl_context','esp_mbedtls_read','esp_mbedtls_write','esp_mbedtls_get_bytes_avail',
        'esp_mbedtls_server_session_init','esp_mbedtls_server_session_continue_async','esp_mbedtls_server_session_delete']
    public=['esp_tls_init','esp_tls_server_session_init','esp_tls_server_session_continue_async',
        'esp_tls_server_session_delete','esp_tls_get_bytes_avail','esp_tls_get_ssl_context',
        'esp_tls_set_conn_state','esp_tls_conn_read','esp_tls_conn_write']
    inline=(frozen/'sdk/components/esp-tls/private_include/esp_tls_mbedtls.h').read_text()
    (out/'sdk-functions.inc').write_text(function(inline,'esp_mbedtls_net_init')+''.join(function(source,name) for name in backend)+''.join(function(core,name) for name in public))
    strip=lambda text:re.sub(r'^#(?:include[^\n]*|pragma once)\n','',text,flags=re.M)
    (out/'transport-production.inc').write_text(strip((frozen/'idf/components/native_web_transport/include/native_web_transport.h').read_text())+'\n'+strip((frozen/'idf/components/native_web_transport/native_web_transport.c').read_text()))
    (out/'esp_err.h').write_text('#pragma once\ntypedef int esp_err_t;\n#define ESP_OK 0\n#define ESP_FAIL (-1)\n#define ESP_ERR_NO_MEM 0x101\n#define ESP_ERR_INVALID_ARG 0x102\n#define ESP_ERR_INVALID_STATE 0x103\n#define ESP_ERR_INVALID_SIZE 0x104\n#define ESP_ERR_NOT_SUPPORTED 0x106\n#define ESP_ERR_TIMEOUT 0x107\n')
    shutil.copyfile(frozen/'sdk/components/esp-tls/esp_tls_errors.h',out/'sdk-tls-errors.h')
    host_flags=[]
    if unified_key_config.is_file():
        shutil.copyfile(frozen/'sdk/components/esp_security/include/esp_key_config.h',out/'sdk-key-config.h')
        host_flags.append('-DHOST_ESP_TLS_UNIFIED_KEYS=1')
    binary=out/'real-tls'
    execute(['gcc',*flags,*host_flags,'-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable',
        '-I'+str(out),str(frozen/'tests/native/native_web_transport/esp_tls_host.c'),str(library),
        '-Wl,--gc-sections','-no-pie','-pthread','-o',str(binary)],out/'build.log')
    with tempfile.TemporaryDirectory(prefix='native-web-tls-') as ephemeral:
        temporary=Path(ephemeral);cert=temporary/'certificate.pem';key=temporary/'private.pem';other=temporary/'other-private.pem'
        for private,certificate in [(key,cert),(other,temporary/'other-certificate.pem')]:
            result=subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout',str(private),
                '-out',str(certificate),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost',
                '-addext','basicConstraints=critical,CA:TRUE'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            if result.returncode:raise RuntimeError('Ephemeral credential generation failed')
            os.chmod(private,0o600)
        pkcs8=key
        assert pkcs8.read_bytes().startswith(b'-----BEGIN PRIVATE KEY-----\n')
        # This pair is valid to an independent TLS implementation. Its rejection
        # is the selected embedded key profile, not a mismatched-key fixture.
        import ssl
        ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(cert,pkcs8)
        rejected=temporary/'unqualified-pkcs8.ntls'
        result=subprocess.run(['python3',str(frozen/'idf/components/native_web_transport/tools/pack_tls_bundle.py'),
            '--certificate',str(cert),'--key',str(pkcs8),'--output',str(rejected)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (out/'packer-pkcs8.log').write_bytes(result.stdout)
        assert result.returncode!=0 and not rejected.exists() and b'PKCS#1' in result.stdout and b'openssl pkey' in result.stdout
        converted=[]
        for index,private in enumerate([key,other]):
            traditional=temporary/('traditional-'+str(index)+'.pem')
            result=subprocess.run(['openssl','pkey','-in',str(private),'-traditional','-out',str(traditional)],
                stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            if result.returncode:raise RuntimeError('Ephemeral qualified-container conversion failed')
            os.chmod(traditional,0o600);converted.append(traditional)
        key,other=converted
        packed=temporary/'provisioning.ntls'
        execute(['python3',str(frozen/'idf/components/native_web_transport/tools/pack_tls_bundle.py'),
            '--certificate',str(cert),'--key',str(key),'--output',str(packed)],out/'packer.log')
        assert packed.stat().st_mode&0o777==0o600
        log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',
            'timeout','45',str(binary),str(cert),str(key),str(other),str(frozen/'tests/native/native_web_transport/tls_client.py'),str(packed),str(pkcs8)],out/'test.log')
    print(log.decode(),end='')
    metrics=re.search(rb'PASS real TLS: (\d+) cases; (.*?), trusted.*?WANT_READ=(\d+)/WANT_WRITE=(\d+)/partial=(\d+)',log)
    assert metrics,'Missing actual protocol results'
    report.update(passed=True,source_sha256=hashes,backend_functions=backend,public_functions=public,
        cases=int(metrics[1]),mbedtls_version=metrics[2].decode(),want_read=int(metrics[3]),want_write=int(metrics[4]),partial_writes=int(metrics[5]),
        provisioning={'qualified_pkcs1':'accepted; real TLS successful','matching_pkcs8':'independently OpenSSL-valid; packer rejects without output; pinned embedded pair check rejects without NVS mutation','mismatched_pkcs1':'pinned embedded pair check rejects without NVS mutation'},
        scope='Actual native_web_transport with pinned MbedTLS software crypto and verbatim selected ESP-TLS server/public functions; real loopback sockets and Python OpenSSL trusted client. Host HTTPD/NVS/type-layout/log/error-tracker/client-only configuration seams; generic software MbedTLS configuration, no ESP hardware acceleration/dynamic-buffer, target ABI/RAM/timing or NVS power-loss claim. Ephemeral certificate/private keys never archived.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
