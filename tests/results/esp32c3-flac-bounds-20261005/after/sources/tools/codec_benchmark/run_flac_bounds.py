"""Run the actual shared FLAC core with exact input bounds and ASan/UBSan."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from run_output_dma_host import host, run, ROOT


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--baseline', action='store_true', help='Record sanitizer failures without calling them PASS')
    args=p.parse_args(); out=args.output.resolve();out.mkdir(parents=True, exist_ok=True)
    src=ROOT/'yoRadio/src/audioI2S/flac_decoder'
    test=ROOT/'tests/native/flac_bounds'
    fixture=ROOT/'tests/fixtures/esp32c3_calibration/flac-level8.flac'
    files=[src/'flac_decoder.cpp',src/'flac_decoder.h',test/'Arduino.h',test/'main.cpp',test/'edges.cpp',Path(__file__)]
    report=dict(sanitizers=True, fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),sources={}, cases={})
    for path in files:
        name=path.relative_to(ROOT).as_posix();target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(path.read_bytes());report['sources'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
    binary=out/'flac-bounds'
    flags=['g++','-std=c++14','-O2','-g','-DFLAC_OUTPUT_FRAMES=512','-DFLAC_SEGMENTED_WORKSPACE=1',
           '-fsanitize=address,undefined','-fno-pie','-no-pie','-I'+host(test),'-I'+host(src)]
    (out/'build.log').write_bytes(run(flags+[host(src/'flac_decoder.cpp'),host(test/'main.cpp'),'-o',host(binary)]))
    cases=['full','0','1','2','3','4','7','8','16','64','512','2048','8192']
    if not args.baseline: cases += ['tail-1','tail-2','tail-3']
    for case in cases:
        command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary),host(fixture),case,host(out/(case+'.pcm'))]
        try:
            log=run(command); result=dict(result='PASS',output=log.decode().strip())
        except subprocess.CalledProcessError as error:
            log=error.output;result=dict(result='FAIL',exit_code=error.returncode)
        (out/(case+'.log')).write_bytes(log);report['cases'][case]=result
    if not args.baseline:
        edges=out/'edges'
        (out/'edges-build.log').write_bytes(run(flags+[host(test/'edges.cpp'),'-o',host(edges)]))
        (out/'edges.log').write_bytes(run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1',host(edges)]))
        report['edge_cases']='PASS'
        # An independent decoder verifies the complete sample count and PCM.
        reference=subprocess.check_output(['ffmpeg','-v','error','-i',str(fixture),'-f','s16le','-acodec','pcm_s16le','-'])
        pcm=(out/'full.pcm').read_bytes()
        report['reference']=dict(decoder=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0],
                                 identical=pcm==reference,bytes=len(reference),sha256=hashlib.sha256(reference).hexdigest())
        if pcm!=reference:raise ValueError('PCM differs from the independent reference')
    report['passed']=all(c['result']=='PASS' for c in report['cases'].values())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['cases'],indent=2))
    return 0 if report['passed'] or args.baseline else 1


if __name__=='__main__':raise SystemExit(main())
