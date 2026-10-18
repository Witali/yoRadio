"""Compile actual shared native web transport against deterministic SDK seams.

This fault suite verifies ownership, credential parsing, retries and deadlines.
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
    source=without_includes(COMPONENT/'native_web_transport.c')
    variants={'production':source,
        'mutant-plaintext-bypass':source.replace('if (!atomic_load(&s_secure)) return lwip_send(', 'if (true) return lwip_send('),
        'mutant-lost-tls-owner':source.replace('if (context->tls) esp_tls_server_session_delete(context->tls);','if (false) esp_tls_server_session_delete(context->tls);'),
        'mutant-unchecked-key-pair':source.replace('if (!result) result = mbedtls_pk_check_pair(&chain.pk, &private_key);','/* incorrect: pair unchecked */'),
        'mutant-renewed-write-budget':source.replace('while (written < size) {','while (written < size) { started = (uint64_t)esp_timer_get_time();')}
    negative={}
    for name,contents in variants.items():
        if name!='production':assert contents!=source
        unit=out/(name+'.c');binary=out/name
        unit.write_text('#include "stubs.h"\n'+without_includes(COMPONENT/'include/native_web_transport.h')+'\n'+contents+'\n#include "faults.c"\n')
        try:
            (out/(name+'-build.log')).write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+host(TEST),host(unit),'-o',host(binary)]))
            code=0
            try:log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','30',host(binary)])
            except subprocess.CalledProcessError as error:code,log=error.returncode,error.output
        except subprocess.CalledProcessError as error:
            (out/'failure.log').write_bytes(error.output);print(error.output.decode(errors='replace'));raise
        (out/(name+'-test.log')).write_bytes(log)
        if name=='production':
            assert code==0,log.decode(errors='replace');print(log.decode().strip())
            count=int(re.search(rb'PASS: (\d+)',log)[1])
        else:
            assert code!=0 and b'Assertion' in log and b'Sanitizer' not in log,(name,code,log)
            negative[name]={'expected_failure':True,'exit_code':code};print(name+': semantic assertion caught')
    report={'passed':True,'groups':count,'negative_controls':negative,'sanitizers':['ASan','UBSan'],'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'scope':'Actual production transport code with deterministic NVS, crypto, TLS, HTTPD, allocation, socket and clock seams. No real crypto/TLS handshake, NVS power-loss, board timing/RAM proof.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
