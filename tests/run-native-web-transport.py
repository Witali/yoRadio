"""Compile actual shared native web transport against deterministic SDK seams.

This fault suite verifies ownership, credential parsing, retries and deadlines,
plus bounded TCP close/drain and HTTPD callback ownership.
Crypto and ESP-TLS here are seams; real TLS handshake tests are separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'idf/components/native_web_transport'
TEST=ROOT/'tests/native/native_web_transport'
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_output_dma_host import host,run

def without_includes(path):
    return re.sub(r'^#(?:include[^\n]*|pragma once)\n','',path.read_text(),flags=re.M)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),COMPONENT/'native_web_transport.c',COMPONENT/'include/native_web_transport.h',TEST/'stubs.h',TEST/'faults.c']
    for path in files:
        destination=out/'sources'/path.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(path.read_bytes())
    frozen=out/'sources';component=frozen/COMPONENT.relative_to(ROOT);test=frozen/TEST.relative_to(ROOT)
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256((frozen/p.relative_to(ROOT)).read_bytes()).hexdigest() for p in files}
    report={'passed':False,'baseline_groups':69,'negative_controls':{},'sanitizers':['ASan','UBSan'],
            'source_sha256':hashes,'scope':'Actual production transport code with deterministic NVS, crypto, TLS, HTTPD, allocation, socket and clock seams. Bounded raw TCP drain/half-close/callback ownership; no real crypto/TLS handshake, peer FIN delivery, NVS power-loss, board timing/RAM proof.'}
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    source=without_includes(component/'native_web_transport.c')
    variants={'production':source,
        'mutant-plaintext-bypass':source.replace('if (!atomic_load(&s_secure)) return lwip_send(', 'if (true) return lwip_send('),
        'mutant-lost-tls-owner':source.replace('if (context->tls) esp_tls_server_session_delete(context->tls);','if (false) esp_tls_server_session_delete(context->tls);'),
        'mutant-unchecked-key-pair':source.replace('if (!result) result = mbedtls_pk_check_pair(&chain.pk, &private_key);','/* incorrect: pair unchecked */'),
        'mutant-renewed-write-budget':source.replace('while (written < size) {','while (written < size) { started = (uint64_t)esp_timer_get_time();'),
        'mutant-blocking-prepare-close':source.replace('context->shutdown_requested = true;\n    }\n}',
            'context->shutdown_requested = true;\n    }\n    (void)shutdown(socket, SHUT_RDWR);\n}')}
    negative={}
    for name,contents in variants.items():
        if name!='production':assert contents!=source
        unit=out/(name+'.c');binary=out/name
        unit.write_text('#include "stubs.h"\n'+without_includes(component/'include/native_web_transport.h')+'\n'+contents+'\n#include "faults.c"\n')
        try:
            (out/(name+'-build.log')).write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(test),host(unit),'-o',host(binary)]))
            code=0
            try:log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
            except subprocess.CalledProcessError as error:code,log=error.returncode,error.output
        except subprocess.CalledProcessError as error:
            (out/'failure.log').write_bytes(error.output);print(error.output.decode(errors='replace'));raise
        (out/(name+'-test.log')).write_bytes(log)
        if name=='production':
            assert code==0,log.decode(errors='replace');print(log.decode().strip())
            count=int(re.search(rb'PASS: (\d+)',log)[1])
            assert int(re.search(rb'BASELINE_GROUPS=(\d+)',log)[1])==69
            close_groups=int(re.search(rb'CLOSE_GROUPS=(\d+)',log)[1]);assert close_groups==17 and count==69+close_groups
            report.update(groups=count,close_groups=close_groups)
        else:
            assert code!=0 and b'Assertion' in log and b'Sanitizer' not in log and b'runtime error:' not in log,(name,code,log)
            negative[name]={'expected_failure':True,'exit_code':code};print(name+': semantic assertion caught')
        report['negative_controls']=negative;save()
    report['source_files_still_match_snapshot']=all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[p.relative_to(ROOT).as_posix()] for p in files)
    assert report['source_files_still_match_snapshot'] and len(negative)==5
    report['passed']=True;save()
if __name__=='__main__':main()
