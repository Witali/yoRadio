"""Check actual FLAC core/adapter against known PCM and FFmpeg under sanitizers."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from run_output_dma_host import ROOT,host,run

sys.path.insert(0,str(ROOT/'tools'))
from audio_test_server.generate_flac_depths import generate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--revision',help='Record an earlier implementation without modifying the checkout')
    parser.add_argument('--fixtures',type=Path,help='Reuse a generated manifest directory')
    parser.add_argument('--case',action='append',help='Restrict fixture names, e.g. for the old-code baseline')
    parser.add_argument('--allocation-failures',action='store_true',help='Fail persistent C malloc/realloc points and verify cleanup/reopen')
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    folder=args.fixtures.resolve() if args.fixtures else out/'fixtures'
    manifest=json.loads((folder/'manifest.json').read_text()) if args.fixtures else generate(folder)
    if args.case:
        assert set(args.case) <= {s['name'] for s in manifest['fixtures']}
        manifest['fixtures']=[s for s in manifest['fixtures'] if s['name'] in args.case]
    (out/'fixture_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    decoder='yoRadio/src/audioI2S/flac_decoder/'
    adapter='idf/esp32c3-oled-native/components/custom_flac/'
    files=[decoder+'flac_decoder.cpp',decoder+'flac_decoder.h',adapter+'custom_flac_adapter.cpp',adapter+'custom_flac_adapter.h',
        'tests/native/flac_bounds/Arduino.h','tests/native/flac_bounds/main.cpp',
        'tools/audio_test_server/generate_flac_depths.py',Path(__file__).relative_to(ROOT).as_posix()]
    files += [p.relative_to(ROOT).as_posix() for p in (ROOT/'tests/native/flac_depths').rglob('*') if p.is_file()]
    report=dict(revision=args.revision,sanitizers=True,sources={},cases=[],ffmpeg=subprocess.check_output(['ffmpeg','-version'],text=True).splitlines()[0])
    for name in files:
        data=subprocess.check_output(['git','show',args.revision+':'+name],cwd=ROOT) if args.revision and name.startswith((decoder,adapter)) else (ROOT/name).read_bytes()
        path=out/'sources'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        report['sources'][name]=hashlib.sha256(data).hexdigest()
    source=out/'sources'
    common=['g++','-std=c++14','-O2','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',
        '-I'+host(source/'tests/native/flac_bounds'),'-I'+host(source/decoder)]
    for variant in ('segmented','contiguous','adapter'):
        flags=common+([] if variant=='contiguous' else ['-DFLAC_SEGMENTED_WORKSPACE=1','-DFLAC_OUTPUT_FRAMES=512'])
        if variant=='adapter':
            flags+=['-I'+host(source/'tests/native/flac_depths'),'-I'+host(source/adapter),host(source/adapter/'custom_flac_adapter.cpp')]
            if args.revision:flags+=['-DBASELINE']
        harness=source/('tests/native/flac_depths/adapter.cpp' if variant=='adapter' else 'tests/native/flac_bounds/main.cpp')
        (out/(variant+'-build.log')).write_bytes(run(flags+[host(source/decoder/'flac_decoder.cpp'),host(harness),'-o',host(out/variant)]))
    if args.allocation_failures:
        assert not args.revision
        flags=common+['-DFLAC_SEGMENTED_WORKSPACE=1','-DFLAC_OUTPUT_FRAMES=512',
            '-I'+host(source/'tests/native/flac_depths'),'-I'+host(source/adapter),
            '-Wl,--wrap=malloc,--wrap=realloc,--wrap=free']
        (out/'oom-build.log').write_bytes(run(flags+[host(source/decoder/'flac_decoder.cpp'),
            host(source/adapter/'custom_flac_adapter.cpp'),host(source/'tests/native/flac_depths/oom.cpp'),'-o',host(out/'oom')]))
    for spec in manifest['fixtures']:
        fixture=folder/spec['file'];name=spec['name'];case=dict(name=name,variants={})
        assert hashlib.sha256(fixture.read_bytes()).hexdigest()==spec['sha256']
        ref=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(fixture),'-f','s16le','-acodec','pcm_s16le','-'])
        digest=hashlib.sha256(ref).hexdigest()
        assert digest==spec['pcm_sha256'] and len(ref)==spec['pcm_bytes'], name
        case['reference']=dict(sha256=digest,bytes=len(ref),known_pcm_identical=True)
        for variant in ('segmented','contiguous','adapter'):
            pcm=out/(name+'-'+variant+'.pcm')
            command=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(out/variant),host(fixture)]
            if variant!='adapter':command+=['full']
            command+=[host(pcm)]
            try:
                log=run(command);actual=pcm.read_bytes();identical=actual==ref
                result=dict(result='PASS' if identical else 'FAIL',identical=identical,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),output=log.decode().strip())
            except subprocess.CalledProcessError as error:
                log=error.output;result=dict(result='FAIL',exit_code=error.returncode)
            (out/(name+'-'+variant+'.log')).write_bytes(log);case['variants'][variant]=result
        if args.allocation_failures:
            try:
                log=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(out/'oom'),host(fixture)])
                result=dict(result='PASS',output=log.decode().strip())
            except subprocess.CalledProcessError as error:
                log=error.output;result=dict(result='FAIL',exit_code=error.returncode)
            (out/(name+'-oom.log')).write_bytes(log);case['allocation_failures']=result
        report['cases'].append(case)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(name,','.join(v+':'+r['result'] for v,r in case['variants'].items()),flush=True)
    failures=sum(r['result']!='PASS' for c in report['cases'] for r in c['variants'].values())
    failures+=sum(c.get('allocation_failures',{}).get('result','PASS')!='PASS' for c in report['cases'])
    report['passed']=not failures;report['failures']=failures
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if not failures or args.revision else 1


if __name__=='__main__':raise SystemExit(main())
