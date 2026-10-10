"""Test actual guarded SDK GHASH against bit-serial NIST and AES-GCM tag equations.

Only platform types/includes are substituted. No hardware AES performance or
complete TLS/side-channel qualification is inferred from this host seam.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from patch_gcm_byte_ghash import patch, reduction8

STUBS='''#include <stdint.h>
#include <stddef.h>
#include <string.h>
#define AES_BLOCK_BYTES 16
typedef struct {
    uint8_t H[16],ghash[16]; uint64_t HL[16],HH[16];
    uint8_t ghash_buf[16]; size_t ghash_buf_len;
} esp_gcm_context;
static void mbedtls_platform_zeroize(void *p, size_t n) {
    volatile uint8_t *v=p; while(n--) *v++=0;
}
'''

def host(path):
    path=Path(path).resolve().as_posix()
    return '/mnt/'+path[0].lower()+path[2:] if sys.platform=='win32' else path

def run(args):
    return subprocess.check_output((['wsl.exe','--exec'] if sys.platform=='win32' else [])+args,stderr=subprocess.STDOUT)

def extract(text):
    table=text[text.index('/* Function to xor two data blocks */'):text.index('/* Update the key value in gcm context */')]
    start=text.index('static void esp_gcm_ghash(esp_gcm_context *ctx, const unsigned char *x, size_t x_len, uint8_t *z)\n{')
    return table+text[start:text.index('/* Function to init AES GCM context to zero */')]

def vectors():
    rng=random.Random(0x38d2026); records=[]
    for key_bytes in (16,32):
        for aad_length in (0,1,13,16,127,128,129,1024):
            for length in (0,1,15,16,17,127,128,129,255,1024,16384):
                key=rng.randbytes(key_bytes); nonce=rng.randbytes(12)
                aad=rng.randbytes(aad_length); plaintext=rng.randbytes(length)
                ecb=Cipher(algorithms.AES(key),modes.ECB()).encryptor()
                h=ecb.update(bytes(16)); mask=ecb.update(nonce+b'\0\0\0\1'); ecb.finalize()
                encrypted=AESGCM(key).encrypt(nonce,plaintext,aad)
                ciphertext,tag=encrypted[:-16],encrypted[-16:]
                pad=lambda b:b+bytes((-len(b))%16)
                body=pad(aad)+pad(ciphertext)+struct.pack('>QQ',8*len(aad),8*len(ciphertext))
                expected=bytes(a^b for a,b in zip(tag,mask))
                records.append(struct.pack('<I',len(body))+h+expected+body)
    return struct.pack('<I',len(records))+b''.join(records)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--idf',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    port=args.idf/'components/mbedtls/port'
    src=port/'aes/esp_aes_gcm.c';header=port/'include/aes/esp_aes_gcm.h'
    original=src.read_text();patched=patch(src.read_bytes(),header.read_bytes()).decode()
    (args.output/'sdk-original.c').write_bytes(src.read_bytes())
    (args.output/'sdk-header.h').write_bytes(header.read_bytes())
    (args.output/'sdk-patched.c').write_text(patched)
    (args.output/'gcm_reduction8.inc').write_bytes(reduction8())
    (args.output/'vectors.bin').write_bytes(vectors())
    report=dict(result='RUNNING',variants={},sources={},scope=__doc__.strip())
    for source in (Path(__file__),ROOT/'tools/patch_gcm_byte_ghash.py',
                   ROOT/'idf/esp32c3-oled-native/main/gcm_byte_ghash.inc',ROOT/'tests/native/gcm_ghash_test.c'):
        report['sources'][source.relative_to(ROOT).as_posix()]=hashlib.sha256(source.read_bytes()).hexdigest()
        (args.output/source.name).write_bytes(source.read_bytes())
    # Prove the guard rejects changed source and layout before testing math.
    for source,layout in ((src.read_bytes()+b'\n',header.read_bytes()),(src.read_bytes(),header.read_bytes()+b'\n')):
        try:patch(source,layout)
        except ValueError:pass
        else:raise AssertionError('Source guard accepted unaudited input')
    for candidate,text in ((0,original),(1,patched)):
        name='candidate' if candidate else 'baseline'
        unit=args.output/(name+'.c');binary=args.output/name
        unit.write_text(STUBS+f'\n#define CANDIDATE {candidate}\n'+extract(text)+'\n#include "gcm_ghash_test.c"\n')
        command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Wno-unused-function',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(args.output),host(unit),'-o',host(binary)]
        (args.output/(name+'-build.log')).write_bytes(run(command))
        log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(args.output/'vectors.bin')])
        (args.output/(name+'.log')).write_bytes(log)
        report['variants'][name]=dict(result='PASS',output=log.decode(),command=command)
        print(name,log.decode(),flush=True)
    report.update(result='PASS',original_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
        patched_sha256=hashlib.sha256(patched.encode()).hexdigest(),
        vectors_sha256=hashlib.sha256((args.output/'vectors.bin').read_bytes()).hexdigest())
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS guarded GHASH comparison',flush=True)

if __name__=='__main__':main()
