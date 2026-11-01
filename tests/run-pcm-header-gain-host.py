"""Qualify application PCM gain with independent Decimal vectors and sanitizers.

Public libopus gain CTL comparison is measured evidence, without an invented
numeric acceptance bound or a pre-quantization equivalence claim. No MCU or
production source is executed/modified. Existing captures are never overwritten.
"""
import argparse
from decimal import Decimal,localcontext,ROUND_HALF_UP
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
HEADER=Path('idf/components/native_stream/include/pcm_header_gain.h')
HARNESS=Path('tests/native/pcm_header_gain_host.c')
OPUS=Path('esp8266/rtos-sdk-native/components/opus_decoder/upstream/include')
INPUTS=[HEADER,HARNESS,*[OPUS/name for name in ('opus.h','opus_defines.h','opus_types.h')]]
GAINS=[-32768,-16384,-8192,-3072,-1536,-256,-1,0,1,256,1536,3072,8192,16384,32767]
FORMATS=[('U8',0,1),('S8',1,1),('S16LE',2,2),('S24LE',3,3),('S32LE',4,4)]


def need(condition,reason):
    if not condition:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()
def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def reference_vectors(precision):
    rows=[]
    with localcontext() as context:
        context.prec=precision
        for name,format_id,width in FORMATS:
            low=-(1<<(width*8-1));high=-low-1
            samples=sorted({n for n in (low,low+1,low//2,-32768,-1024,-3,-2,-1,0,1,2,3,1024,32767,high//2,high-1,high) if low<=n<=high})
            for gain in GAINS:
                factor=Decimal(10)**(Decimal(gain)/Decimal(5120))
                for sample in samples:
                    scaled=Decimal(sample)*factor
                    rounded=int(scaled.to_integral_value(rounding=ROUND_HALF_UP))
                    expected=max(low,min(high,rounded))
                    def pack(n):return [n+128] if name=='U8' else list(n.to_bytes(width,'little',signed=True))
                    rows.append(dict(format=name,format_id=format_id,width=width,gain_q8=gain,
                                     sample=sample,expected_sample=expected,input=pack(sample),expected=pack(expected)))
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh ignored capture required')
    out.mkdir(parents=True)
    report=dict(passed=False,state='preparing',sources=[],commands=[],production_integrated=False,native_mcu=False,
                application_integer_pcm_gain=True,numeric_conformance_claim=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def command(name,argv):
        argv=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+argv
        row=dict(name=name,argv=argv,state='starting',exit_status=None);report['commands'].append(row)
        paths={key:out/(name+'.'+key+'.log') for key in ('stdout','stderr')};start=time.monotonic()
        with paths['stdout'].open('wb') as stdout,paths['stderr'].open('wb') as stderr:
            child=subprocess.Popen(argv,stdout=stdout,stderr=stderr,shell=False);row.update(pid=child.pid,state='running');save()
            try:status=child.wait(timeout=180)
            except subprocess.TimeoutExpired:child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-start,3))
        for key,path in paths.items():row[key]=dict(path=path.name,bytes=path.stat().st_size,sha256=sha(path.read_bytes()))
        save();need(status==0 and not row.get('timed_out'),'actual native terminal zero: '+name)
        return paths['stdout'].read_bytes()
    save()
    try:
        for relative in [Path(__file__).resolve().relative_to(ROOT)]+INPUTS:
            body=(ROOT/relative).read_bytes();snapshot=out/'sources'/relative;snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(body)
            report['sources'].append(dict(path=relative.as_posix(),snapshot=snapshot.relative_to(out).as_posix(),bytes=len(body),sha256=sha(body)))
        vectors=reference_vectors(80);need(vectors==reference_vectors(120),'independent Decimal precision agreement')
        report['reference']=dict(arithmetic='Python Decimal',precisions=[80,120],identical_vectors=True,vectors=len(vectors),rounding='ROUND_HALF_UP',gains=GAINS,formats=[name for name,_,_ in FORMATS])
        (out/'reference-vectors.json').write_text(json.dumps(vectors,indent=2)+'\n',encoding='utf-8')
        generated=out/'vectors.h'
        lines=['#pragma once','typedef struct { int32_t gain; unsigned format,width; uint8_t input[4],expected[4]; } reference_vector;','static const reference_vector gain_vectors[] = {']
        for row in vectors:
            before=','.join(map(str,row['input']));after=','.join(map(str,row['expected']))
            lines.append('{%d,%u,%u,{%s},{%s}},'%(row['gain_q8'],row['format_id'],row['width'],before,after))
        lines.append('};');generated.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        report['generated']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in (generated,out/'reference-vectors.json')};save()
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0]
        compiler=command('compiler-realpath',['/usr/bin/readlink','-f','/usr/bin/gcc']).decode().strip()
        need(compiler.startswith('/usr/') and '\n' not in compiler,'resolved compiler path')
        report['compiler_identity']=command('compiler-sha256',['/usr/bin/sha256sum',compiler]).decode().strip()
        library=command('libopus-path',['/usr/bin/gcc','-print-file-name=libopus.so.0']).decode().strip()
        need(library.startswith('/usr/') and '\n' not in library,'installed libopus library')
        library=command('libopus-realpath',['/usr/bin/readlink','-f',library]).decode().strip()
        report['libopus_identity']=command('libopus-sha256',['/usr/bin/sha256sum',library]).decode().strip()
        libm=command('libm-realpath',['/usr/bin/readlink','-f','/lib/x86_64-linux-gnu/libm.so.6']).decode().strip()
        report['libm_identity']=command('libm-sha256',['/usr/bin/sha256sum',libm]).decode().strip()
        binary=out/'pcm-header-gain-host'
        command('build',['/usr/bin/gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wshadow','-Wformat=2','-Wstrict-prototypes',
                         '-fsanitize=address,undefined,float-cast-overflow','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                         '-I'+host((out/'sources'/HEADER).parent),'-I'+host(out/'sources'/OPUS),'-I'+host(out),
                         host(out/'sources'/HARNESS),library,'-lm','-o',host(binary)])
        report['binary']=dict(path=binary.name,bytes=binary.stat().st_size,sha256=sha(binary.read_bytes()),local_only=True)
        stdout=command('test',['/usr/bin/env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary)])
        rows=[json.loads(line) for line in stdout.decode().splitlines()];need(len(rows)==11 and all(row['passed'] for row in rows),'complete actual test transcript')
        summary=rows[-1];need(summary['reference_vectors']==len(vectors) and summary['vector_applications']==len(vectors)*4 and summary['identity_cases']==20 and summary['creator_observations']==9,'actual independent-vector/identity/reference inventory')
        need(rows[0]['factors']==65536 and rows[0]['pow_calls']==65535 and all(row['numerical_acceptance_bound'] is None and not row['numeric_conformance_claim'] for row in rows[1:-1]),'full gain range and observation-only creator comparison')
        for row in report['sources']:need(sha((ROOT/row['path']).read_bytes())==row['sha256']==sha((out/row['snapshot']).read_bytes()),'unchanged canonical/frozen input')
        need(command('libopus-post-sha256',['/usr/bin/sha256sum',library]).decode().strip()==report['libopus_identity'],'unchanged creator binary')
        need(command('libm-post-sha256',['/usr/bin/sha256sum',libm]).decode().strip()==report['libm_identity'],'unchanged libm')
        report.update(passed=True,state='complete',test_records=rows,all_source_bindings_unchanged=True);save()
        print(json.dumps(dict(capture=out.relative_to(ROOT).as_posix(),**summary)));return 0
    except Exception as error:
        report.update(passed=False,state='nonpass',failure=dict(type=type(error).__name__,reason=str(error)));save()
        print(json.dumps(dict(passed=False,capture=out.relative_to(ROOT).as_posix(),failure=report['failure'])));return 1


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
