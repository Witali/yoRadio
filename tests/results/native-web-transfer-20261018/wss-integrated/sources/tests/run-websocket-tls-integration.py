"""Join frozen HTTPD/application and actual ESP-TLS/crypto evidence into WSS.

No production edits or package installation. Real verified OpenSSL clients,
PSA SHA-1/Base64, ESP-TLS server code, transport and HTTPD/application receive
paths. Credentials exist only in a Linux temporary directory.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/native/ws_integration'
SDK_ROOT=ROOT/'.idf' if (ROOT/'.idf').is_dir() else ROOT.parents[1]/'.idf'


def host(path):
    path=Path(path).resolve().as_posix()
    return '/mnt/'+path[0].lower()+path[2:] if sys.platform=='win32' else path


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(command,log):
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    log.write_bytes(result.stdout)
    if result.returncode:
        print(result.stdout.decode(errors='replace'),file=sys.stderr)
        raise RuntimeError('Command failed; see '+str(log))
    return result.stdout


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--integration-evidence',type=Path,required=True)
    parser.add_argument('--tls-cyd',type=Path,required=True)
    parser.add_argument('--tls-c3',type=Path,required=True)
    parser.add_argument('--crypto-cyd',type=Path,required=True)
    parser.add_argument('--crypto-c3',type=Path,required=True)
    parser.add_argument('--target',choices=['cyd','c3','both'],default='both')
    args=parser.parse_args()
    if sys.platform=='win32':
        command=['wsl.exe','--exec','python3',host(__file__)]
        for key,value in vars(args).items():command+=['--'+key.replace('_','-'),host(value) if isinstance(value,Path) else value]
        raise SystemExit(subprocess.call(command))
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    plain=args.integration_evidence.resolve();plain_report=json.loads((plain/'report.json').read_text())
    assert plain_report['passed']
    report={'sanitizers':['ASan','UBSan'],'variants':{},'physical_hardware':False,
            'integration_report_sha256':digest(plain/'report.json'),'source_sha256':{}}
    # Current new test scaffolding and its inputs are all frozen before build.
    # Production/SDK algorithm bodies come only from the prior frozen reports.
    for path in [Path(__file__),*FIXTURE.glob('*.*')]:
        key=path.relative_to(ROOT).as_posix();target=out/'sources'/key
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        report['source_sha256'][key]=digest(target)
    for name in ['platform.h','platform.c']:
        frozen=plain/'sources/tests/native/ws_integration'/name
        assert digest(frozen)==digest(out/'sources/tests/native/ws_integration'/name),'Regenerate plaintext evidence after fixture changes'
    for target,tls_evidence,cache in [('cyd',args.tls_cyd,args.crypto_cyd),('c3',args.tls_c3,args.crypto_c3)]:
        if args.target!='both' and args.target!=target:continue
        tls_evidence=tls_evidence.resolve();cache=cache.resolve();directory=out/target;directory.mkdir()
        tls_report=json.loads((tls_evidence/'report.json').read_text());assert tls_report['passed']
        assert tls_report['crypto_fingerprint']==json.loads((cache/'identity.json').read_text())['fingerprint']
        library=cache/'libpinned-mbedtls.a';assert library.is_file()
        # Snapshot input evidence, including its source manifests, not its
        # ephemeral credentials (which no evidence directory contains).
        shutil.copytree(plain/'sources',directory/'plain-sources')
        shutil.copytree(plain/target/'sdk-sources',directory/'sdk-sources')
        shutil.copytree(tls_evidence/'sources',directory/'tls-sources')
        shutil.copyfile(tls_evidence/'vendor-source-sha256.json',directory/'vendor-source-sha256.json')
        for name in ['sdk-functions.inc','transport-production.inc','esp_err.h','sdk-tls-errors.h']:
            shutil.copyfile(tls_evidence/name,directory/name)
        unified_keys=(tls_evidence/'sdk-key-config.h').is_file()
        if unified_keys:shutil.copyfile(tls_evidence/'sdk-key-config.h',directory/'sdk-key-config.h')
        for path in (plain/target).glob('*.inc'):
            if '-original' not in path.name:shutil.copyfile(path,directory/path.name)
        prefix=(directory/'tls-sources/tests/native/native_web_transport/esp_tls_host.c').read_text()
        prefix=prefix[:prefix.index('static uint8_t *read_ephemeral')]
        first=prefix.index('static struct {int socket;')
        last=prefix.index('static uint8_t *nvs_blob;')
        externs='''/* These are the actual SDK session APIs in integration.c. */
void *httpd_sess_get_transport_ctx(httpd_handle_t,int);
void httpd_sess_set_transport_ctx(httpd_handle_t,int,void *,void (*)(void *));
esp_err_t httpd_sess_set_send_override(httpd_handle_t,int,httpd_send_func_t);
esp_err_t httpd_sess_set_recv_override(httpd_handle_t,int,httpd_recv_func_t);
esp_err_t httpd_sess_set_pending_override(httpd_handle_t,int,httpd_pending_func_t);
'''
        prefix=prefix[:first]+externs+prefix[last:]
        backend=directory/'backend.c'
        backend.write_text(prefix+'\n'+(out/'sources/tests/native/ws_integration/tls_backend.c').read_text())
        unit=directory/'integration.c'
        unit.write_text(('#define TARGET_C3 1\n' if target=='c3' else '')+'''
#define INTEGRATION_TLS 1
#include "platform.h"
#include "psa/crypto.h"
#include "mbedtls/base64.h"
#include "native_httpd_headers.h"
#include "sdk-ws.inc"
#include "sdk-txrx.inc"
#include "sdk-parse.inc"
#include "sdk-sess.inc"
#include "sdk-uri.inc"
#include "application.inc"
#include "platform.c"
#include "tls_test.c"
''')
        # Match the already-qualified software crypto cache's include tree.
        sdk_name=tls_report['sdk'];sdk=SDK_ROOT/sdk_name
        assert sdk.is_dir(),sdk
        mbed=sdk/'components/mbedtls/mbedtls';crypto=mbed/'tf-psa-crypto'
        includes=[directory,out/'sources/tests/native/ws_integration',directory/'plain-sources/idf/esp32-cyd2usb-native/main/compat/httpd_rfc6455',
            directory/'plain-sources/idf/components/native_stream/include',directory/'sdk-sources/components/http_parser',
            cache/'host-config',sdk/'components/mbedtls/port/include',mbed/'include',mbed/'library',
            *[crypto/name for name in ['include','core','dispatch','utilities','extras','platform','drivers/builtin/include','drivers/builtin/src',
                'drivers/everest/include','drivers/everest/include/tf-psa-crypto/private/everest','drivers/everest/include/tf-psa-crypto/private/everest/kremlib',
                'drivers/p256-m/p256-m/include','drivers/p256-m/p256-m/include/p256-m','drivers/p256-m/p256-m_driver_interface',
                'drivers/pqcp/include','drivers/pqcp/src','drivers/pqcp/mldsa-native/mldsa']]]
        binary=directory/'wss'
        flags=['-std=c11','-D_GNU_SOURCE','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-function',
            '-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-Wno-sign-compare',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-ffunction-sections','-fdata-sections']
        if unified_keys:flags.append('-DHOST_ESP_TLS_UNIFIED_KEYS=1')
        execute(['gcc',*flags,*['-I'+str(p) for p in includes],str(unit),str(backend),
            str(directory/'sdk-sources/components/http_parser/http_parser.c'),str(library),'-Wl,--gc-sections','-no-pie','-pthread','-o',str(binary)],directory/'build.log')
        with tempfile.TemporaryDirectory(prefix='wss-integration-') as ephemeral:
            temporary=Path(ephemeral);certificate=temporary/'certificate.pem';private=temporary/'private.pem'
            result=subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-sha256','-nodes','-keyout',str(private),
                '-out',str(certificate),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost',
                '-addext','basicConstraints=critical,CA:TRUE'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            if result.returncode:raise RuntimeError('Ephemeral test credential generation failed')
            os.chmod(private,0o600)
            # SDK 6.0.2's pinned software crypto requires traditional RSA PEM;
            # use the same qualified container on both profiles.
            traditional=temporary/'traditional.pem'
            result=subprocess.run(['openssl','pkey','-in',str(private),'-traditional','-out',str(traditional)],
                                  stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            if result.returncode:raise RuntimeError('Ephemeral test container conversion failed')
            os.chmod(traditional,0o600);packed=temporary/'bundle.ntls'
            execute(['python3',str(directory/'tls-sources/idf/components/native_web_transport/tools/pack_tls_bundle.py'),
                '--certificate',str(certificate),'--key',str(traditional),'--output',str(packed)],directory/'packer.log')
            assert packed.stat().st_mode&0o777==0o600
            log=execute(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','45',
                str(binary),str(packed),str(out/'sources/tests/native/ws_integration/tls_client.py'),str(certificate)],directory/'test.log')
        print(target+': '+log.decode().strip())
        report['variants'][target]={'passed':True,'result':log.decode().strip(),'crypto_archive_sha256':digest(library),
            'tls_report_sha256':digest(tls_evidence/'report.json'),'crypto_fingerprint':tls_report['crypto_fingerprint'],
            'production_source_sha256':plain_report['source_sha256'],'tls_source_sha256':tls_report['source_sha256'],
            'generated_overlay':plain_report['variants'][target]['overlay'],
            'composed_inputs_sha256':{p.name:digest(p) for p in directory.glob('*.inc')}}
    report['passed']=True
    report['scope']='Actual generated HTTPD parser/lifecycle/URI/framing and actual application receive/control/transport/session/register code; actual native_web_transport and selected pinned ESP-TLS server/public functions linked with qualified pinned software MbedTLS archive; trusted CA and hostname-verified independent OpenSSL client over real TCP/TLS1.2. Actual PSA SHA-1/Base64 accept, no SHA sample stub. Host HTTPD/ESP-TLS field models, FreeRTOS scheduling, error-response formatting, radio command dispatch/status and NVS are explicit seams. No hardware ABI/RAM/timing, whole FreeRTOS HTTPD main loop, TLS1.3 or full RFC conformance claim.'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
