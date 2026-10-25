"""Check the actual lookup1 integer-root helper with a Python bignum oracle.

Native-long and explicit int32 arithmetic models run under ASan/UBSan. Only the
helper and its two accessed book fields are extracted, so this does not prove
target ABI, raw setup acceptance, PCM or full Vorbis conformance. The separately
generated target corpus is for native ILP32 SDK/QEMU checks of the whole source.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
SETUPS = {name: ROOT/'idf'/profile/'main/vorbis_repair/setup.c' for name, profile in
          (('esp32', 'esp32-cyd2usb-native'), ('esp32c3', 'esp32c3-oled-native'))}
MAX_ENTRIES = (1 << 24)-1

DRIVER = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
typedef struct { TEST_WORD dim, entries; } codebook;
#include "helper.inc"
static uint32_t get(FILE *stream) {
    unsigned char b[4]; assert(fread(b,1,4,stream)==4);
    return (uint32_t)b[0]|(uint32_t)b[1]<<8|(uint32_t)b[2]<<16|(uint32_t)b[3]<<24;
}
static void put(FILE *stream,uint32_t value) {
    unsigned char b[4]={(unsigned char)value,(unsigned char)(value>>8),
                      (unsigned char)(value>>16),(unsigned char)(value>>24)};
    assert(fwrite(b,1,4,stream)==4);
}
int main(int argc,char **argv) {
    assert(argc==3); FILE *in=fopen(argv[1],"rb"),*out=fopen(argv[2],"wb"); assert(in&&out);
    uint32_t count=get(in); put(out,count); put(out,sizeof(TEST_WORD)*8);
    for(uint32_t i=0;i<count;i++) {
        uint32_t entries=get(in),dimensions=get(in); (void)get(in);
        assert(entries>=1&&entries<=UINT32_C(16777215)&&dimensions>=1&&dimensions<=65535);
        codebook book={(TEST_WORD)dimensions,(TEST_WORD)entries},copy=book;
        TEST_WORD value=_book_maptype1_quantvals(&book);
        assert(book.entries==copy.entries&&book.dim==copy.dim);
        assert(value>=1&&value<=(TEST_WORD)entries); put(out,(uint32_t)value);
    }
    assert(fgetc(in)==EOF); assert(!fclose(in)); assert(!fclose(out)); return 0;
}
'''


def need(condition, message):
    if not condition: raise ValueError(message)


def sha(data): return hashlib.sha256(data).hexdigest()


def function(text, name):
    match = re.search(r'^static (?:long|int) '+re.escape(name)+r'\([^\n]*\)\s*\{', text, re.M)
    need(match is not None, 'actual source function '+name)
    start, depth = match.start(), 1
    cursor = text.index('{', match.start())+1
    while depth:
        need(cursor<len(text), 'balanced function source')
        depth += (text[cursor]=='{')-(text[cursor]=='}')
        cursor += 1
    return text[start:cursor]+'\n'


def oracle(entries, dimensions):
    # Deliberately use exact unbounded powers and descending bit construction,
    # independent of the production bounded-multiply binary search.
    value = 0
    for bit in range((entries.bit_length()-1)//dimensions, -1, -1):
        candidate = value | (1 << bit)
        if pow(candidate, dimensions)<=entries: value = candidate
    need(pow(value, dimensions)<=entries<pow(value+1, dimensions), 'exact root inequalities')
    return value


def vectors():
    boundaries = {(e,d) for d in (1,2,3,4,5,7,8,15,16,23,24,31,32,33,63,64,65,255,256,32767,65535)
                  for k in range(1,25) for e in ((1 << k)-1, 1 << k, (1 << k)+1) if e<=MAX_ENTRIES}
    for base in (*range(2,65),4094,4095):
        for dimensions in range(2,25):
            power = pow(base, dimensions)
            if power>MAX_ENTRIES: break
            boundaries.update((power+delta, dimensions) for delta in (-1,0,1) if power+delta<=MAX_ENTRIES)
    pairs = boundaries | {(e,d) for e in range(1,513) for d in range(1,65)}
    rng = random.Random(0x564f52424953)
    pairs.update((rng.randint(1,MAX_ENTRIES),rng.randint(1,65535)) for _ in range(1500))
    return [dict(entries=e,dimensions=d,expected=oracle(e,d)) for e,d in sorted(pairs)], boundaries


def packed(rows):
    return struct.pack('<I',len(rows))+b''.join(struct.pack('<III',r['entries'],r['dimensions'],r['expected']) for r in rows)


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--baseline-ref',help='Optional immutable Git ref to demonstrate the old arithmetic under UBSan')
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh .build output')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'target-cases').mkdir()
    report=dict(completed=False,passed=False,scope=__doc__,commands=[],sources={},variants={},
                raw_decoder_executed=False,target_executed=False,physical_device=False,full_G6_qualified=False)
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path, name):
        data=path.read_bytes();(out/'sources'/name).write_bytes(data)
        report['sources'][str(path)]=dict(sha256=sha(data),snapshot='sources/'+name)
        return data
    save()
    try:
        freeze(Path(__file__),'test-vorbis-quantvals.py')
        owner=ROOT/'tests/test-vorbis-floor1-render.py'
        tree=ast.parse(freeze(owner,'owned-supervisor-source.py'))
        assignments=[node for node in tree.body if isinstance(node,ast.Assign) and
                     any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(assignments)==1,'one existing owned-process supervisor literal')
        supervisor=ast.literal_eval(assignments[0].value)
        need(isinstance(supervisor,str),'literal owned supervisor')
        (out/'supervisor.py').write_text(supervisor,encoding='utf-8',newline='\n')
        bodies={name:function(freeze(path,name+'-setup.c').decode().replace('\r\n','\n'),
                              '_book_maptype1_quantvals') for name,path in SETUPS.items()}
        need(bodies['esp32']==bodies['esp32c3'],'both canonical arithmetic implementations equal')
        report['function_source_line_endings_normalized']=True
        rows,boundaries=vectors();(out/'inputs.bin').write_bytes(packed(rows))
        target=[row for row in rows if (row['entries'],row['dimensions']) in boundaries]
        model=dict(schema='vorbis-quantvals-cases-v1',cases=target)
        (out/'target-cases/cases.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8')
        header=('#pragma once\n#include <stdint.h>\n#define QUANTVALS_CASE_COUNT '+str(len(target))+'\n'
                'typedef struct { uint32_t entries; uint32_t dimensions; uint32_t expected; } quantvals_case_t;\n'
                'static const quantvals_case_t quantvals_cases[QUANTVALS_CASE_COUNT] = {\n'+
                ''.join('    {%d, %d, %d},\n'%(r['entries'],r['dimensions'],r['expected']) for r in target)+'};\n')
        (out/'target-cases/cases.h').write_text(header,encoding='utf-8',newline='\n')
        report.update(cases=len(rows),target_cases=len(target),input_sha256=sha((out/'inputs.bin').read_bytes()))
        def run(name,argv,expected=0):
            nonce=uuid.uuid4().hex;request=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
            request.write_text(json.dumps(dict(nonce=nonce,argv=argv,timeout=60,receipt=host(receipt),stop=host(stop))),encoding='utf-8')
            command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[host(out/'supervisor.py'),host(request)]
            entry=dict(name=name,argv=command,child_argv=argv,nonce=nonce);report['commands'].append(entry);save()
            child=None;error=None;start=time.monotonic()
            stdout=out/(name+'.stdout.log');stderr=out/(name+'.stderr.log')
            try:
                with stdout.open('xb') as so,stderr.open('xb') as se:
                    child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                    entry['transport_pid']=child.pid;save();child.wait(timeout=80)
            except BaseException as exc: error=exc
            finally:
                if child is not None and child.poll() is None:
                    stop.write_text(nonce,encoding='utf-8')
                    try: child.wait(timeout=15)
                    except subprocess.TimeoutExpired: child.kill();child.wait(timeout=5);entry['forced_transport_stop']=True
                actual=json.loads(receipt.read_bytes()) if receipt.exists() else {}
                entry.update(supervisor=actual,transport_returncode=None if child is None else child.poll(),
                    elapsed_seconds=time.monotonic()-start,stdout_sha256=sha(stdout.read_bytes()) if stdout.exists() else None,
                    stderr_sha256=sha(stderr.read_bytes()) if stderr.exists() else None);save()
            need(actual.get('nonce')==nonce and actual.get('request_sha256')==sha(request.read_bytes()) and
                 actual.get('final') is True and actual.get('new_session') is True and actual.get('child_reaped') is True and
                 actual.get('group_gone') is True and actual.get('state')=='terminal' and
                 actual.get('child_returncode')==expected and entry['transport_returncode']==0 and
                 not entry.get('forced_transport_stop') and 'cleanup_error' not in actual,'owned terminal/cleanup '+name)
            if error is not None: raise error
            return stdout.read_bytes(),stderr.read_bytes()
        run('compiler-version',['gcc','--version'])
        run('compiler-machine',['gcc','-dumpmachine'])
        flags=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic',
               '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie']
        for variant in ('native-long','int32-model'):
            directory=out/variant;directory.mkdir()
            body=bodies['esp32'] if variant=='native-long' else re.sub(r'\blong\b','int32_t',bodies['esp32'])
            (directory/'helper.inc').write_text(body,encoding='utf-8',newline='\n')
            (directory/'driver.c').write_text(DRIVER,encoding='utf-8',newline='\n')
            word='long' if variant=='native-long' else 'int32_t'
            run(variant+'-compile',flags+['-DTEST_WORD='+word,host(directory/'driver.c'),'-o',host(directory/'test')])
            so,se=run(variant+'-execute',[host(directory/'test'),host(out/'inputs.bin'),host(directory/'outputs.bin')])
            need(not so and not se,'clean sanitized numerical run')
            output=(directory/'outputs.bin').read_bytes();values=struct.unpack('<'+'I'*(len(output)//4),output)
            need(len(values)==len(rows)+2 and values[0]==len(rows) and
                 (variant!='int32-model' or values[1]==32) and list(values[2:])==[r['expected'] for r in rows],
                 'every exact root matches independent bignum oracle')
            report['variants'][variant]=dict(cases=len(rows),word_bits=values[1],exact=True,output_sha256=sha(output),
                transformation='none' if variant=='native-long' else 'only long tokens in extracted helper become int32_t; two synthetic field types also int32_t')
        if args.baseline_ref:
            git=subprocess.run(['git','-c','core.longpaths=true','show',args.baseline_ref+':idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c'],
                               cwd=ROOT,check=True,capture_output=True,timeout=30)
            directory=out/'baseline';directory.mkdir();(directory/'setup.c').write_bytes(git.stdout)
            text=git.stdout.decode();body=function(text,'_ilog')+function(text,'_book_maptype1_quantvals')
            (directory/'helper.inc').write_text(body,encoding='utf-8',newline='\n')
            (directory/'driver.c').write_text(DRIVER,encoding='utf-8',newline='\n')
            (directory/'inputs.bin').write_bytes(packed([dict(entries=2,dimensions=64,expected=1)]))
            run('baseline-compile',flags+['-DTEST_WORD=long',host(directory/'driver.c'),'-o',host(directory/'test')])
            so,se=run('baseline-execute',[host(directory/'test'),host(directory/'inputs.bin'),host(directory/'outputs.bin')],expected=1)
            need(b'runtime error: signed integer overflow:' in se and b'helper.inc:' in se,'named original power-overflow diagnosis')
            report['baseline']=dict(ref=args.baseline_ref,source_sha256=sha(git.stdout),entries=2,dimensions=64,
                                    signed_power_overflow_detected=True,scope='native long sanitizer witness; not target decoder execution')
        need(all(sha(Path(path).read_bytes())==pin['sha256'] for path,pin in report['sources'].items()),'frozen source unchanged')
        report.update(completed=True,passed=True);save()
        print(json.dumps({k:report[k] for k in ('completed','passed','cases','target_cases','variants')}));return 0
    except BaseException as exc:
        report.update(completed=False,passed=False,error=repr(exc));save();raise


if __name__=='__main__': sys.exit(main())
