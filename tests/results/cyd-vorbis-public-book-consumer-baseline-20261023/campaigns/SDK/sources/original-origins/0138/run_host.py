"""Root-owned baseline ASan/UBSan consumer-only campaign; fresh explicit inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from oracle import need
from protocol import vector

HERE=Path(__file__).resolve().parent

def sha(data):return hashlib.sha256(data).hexdigest()


def sanitizer_clean_scope(row,stderr,comparison):
    """An ordinary vector mismatch exits1; that alone is not a sanitizer finding."""
    return (row['terminal'] and not row['timed_out'] and not row['interrupted'] and comparison is not None and
            row.get('returncode')==(0 if comparison['equal'] else 1) and not stderr)


def run(args):
    runtime,output=args.runtime.resolve(),args.output.resolve();compiler=args.compiler.resolve()
    need(not output.exists() and output.parent==runtime.parent and output!=runtime,'fresh separate host baseline output')
    need(sha(compiler.read_bytes())==args.compiler_sha256,'reviewed actual explicit host compiler SHA')
    readyraw=(runtime/'readiness.json').read_bytes();need(sha(readyraw)==args.runtime_readiness_sha256,'reviewed actual generated runtime readiness')
    ready=json.loads(readyraw)
    source_ready_raw=(HERE/'readiness.json').read_bytes();need(ready['source_readiness_sha256']==sha(source_ready_raw),'exact reviewed source preparation')
    for row in json.loads(source_ready_raw)['files']:
        raw=(HERE/row['path']).read_bytes();need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'every host diagnostic source identity')
    for row in ready['files']:
        raw=(runtime/row['path']).read_bytes();need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'every prepared runtime source identity')
    contract=json.loads((runtime/'contract.json').read_bytes());model=contract['model']
    need((model['case_count'],model['codeword_probes'],model['vector_calls'])==(36,123,365),'full predeclared host inventory')
    output.mkdir();commands=[];records=[]
    result=dict(schema='public-book-consumer-host-diagnostic-v1',completed=False,compiler_sha256=args.compiler_sha256,
        host_python_path=sys.executable,host_python_sha256=sha(Path(sys.executable).read_bytes()),
        runtime_readiness_sha256=args.runtime_readiness_sha256,commands=commands,records=records,
        host_consumer_diagnostics_completed=False,host_sanitizers_clean=False,complete_Fraction_comparison=False,
        all_Fraction_vectors_equal=False,actual_canonical_SDK_publication_completed=False,
        public_arithmetic_portability_qualified=False,full_standard_qualified=False,vendor_cause_diagnosed=False)
    def save():(output/'report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    def child(name,argv,timeout):
        start=time.monotonic();row=dict(name=name,argv=list(map(str,argv)),cwd=str(runtime),terminal=False,timed_out=False,interrupted=False)
        commands.append(row);save()
        env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        try:
            completed=subprocess.run(argv,cwd=runtime,env=env,capture_output=True,timeout=timeout,check=False)
            stdout,stderr=completed.stdout,completed.stderr;row.update(terminal=True,returncode=completed.returncode)
        except subprocess.TimeoutExpired as error:
            stdout,stderr=error.stdout or b'',error.stderr or b'';row.update(timed_out=True,returncode=None)
        except KeyboardInterrupt:
            row.update(interrupted=True);save();raise
        for stream,data in (('stdout',stdout),('stderr',stderr)):
            path=output/(name+'.'+stream+'.log');path.write_bytes(data);row[stream]=dict(path=path.name,bytes=len(data),sha256=sha(data))
        row['elapsed_seconds']=time.monotonic()-start;save();return row,stdout,stderr
    save();main=runtime/'project/main';binary=output/('consumer-baseline.exe' if os.name=='nt' else 'consumer-baseline')
    flags=['-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer']
    build,_,_=child('compile',[str(compiler),*flags,'-I',str(main),str(main/'consumer_unit.c'),'-o',str(binary)],120)
    result['compile_flags']=flags
    if not build['terminal'] or build.get('returncode')!=0:
        result.update(result='BASELINE_BUILD_FAILED',completed=True);save();return 1
    result['host_binary_sha256']=sha(binary.read_bytes());save()
    for ci,c in enumerate(model['cases']):
        for pi,p in enumerate(c['book']['probes']):
            for qi,point in enumerate(c['book']['points']):
                name=f'case{ci:02d}-probe{pi:02d}-point{qi}'
                row,stdout,stderr=child(name,[str(binary),str(ci),str(pi),str(qi)],15)
                item=dict(case=ci,probe=pi,point=point,wire_scope=p['wire_scope'],command=name,
                    sanitizer_clean=False)
                text=stdout.decode(errors='replace').strip()
                if text.startswith('PUBLIC_BOOK_CONSUMER_VECTOR '):
                    observed=vector(text,model,-1);need((observed['case'],observed['probe'],observed['point'])==(ci,pi,point),'actual host child operand binding');item['comparison']=observed
                else:item['comparison']=None
                item['sanitizer_clean']=sanitizer_clean_scope(row,stderr,item['comparison'])
                records.append(item);save()
    complete=len(records)==365 and all(row['terminal'] and not row['timed_out'] and not row['interrupted'] for row in commands)
    result.update(result='BASELINE_DIAGNOSTICS_RECORDED',completed=True,host_consumer_diagnostics_completed=complete,
        host_sanitizers_clean=complete and all(row['sanitizer_clean'] for row in records),
        complete_Fraction_comparison=complete and all(row['comparison'] is not None for row in records),
        all_Fraction_vectors_equal=complete and all(row['comparison'] is not None and row['comparison']['equal'] for row in records))
    save();return 0 if result['host_sanitizers_clean'] and result['all_Fraction_vectors_equal'] else 1


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('runtime','output','compiler'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('compiler-sha256','runtime-readiness-sha256'):p.add_argument('--'+name,required=True)
    raise SystemExit(run(p.parse_args()))
