"""Check new pure family1 helpers against complete creator inputs and boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['idf/components/native_stream/include/opus_family1_mapping.h','idf/components/native_stream/include/opus_multistream_framing.h',
         'tests/native/opus_family1_helpers_host.c','tests/native/opus_family1_public.h','tests/run-opus-family1-helpers.py']
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();reference=args.reference.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists() and reference.is_relative_to(ROOT/'.build'),'fresh ignored capture and qualified local fixture source')
    evidence=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['reference_fixtures']
    out.mkdir(parents=True);report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},production_integrated=False,native_executed=False,private_abi_used=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,relative):
        destination=out/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(Path(path).read_bytes())
        report['sources'].append(dict(path=str(Path(path).resolve()),snapshot=relative.as_posix(),**pin(path)))
    def command(name,argv):
        full=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv));row=dict(name=name,argv=full,state='starting',timeout_seconds=120)
        report['commands'].append(row);save();started=time.monotonic()
        with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
            child=subprocess.Popen(full,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);row.update(pid=child.pid,state='running');save()
            try:status=child.wait(timeout=120)
            except subprocess.TimeoutExpired:child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-started,3))
        for stream in ('stdout','stderr'):
            path=out/(name+'.'+stream+'.log');row[stream]=dict(path=path.name,**pin(path))
        save();need(status==0 and not row.get('timed_out'),'actual terminal zero: '+name);return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:freeze(ROOT/name,Path('sources')/name)
        for channels in (3,6,8):
            name='channels'+str(channels)+'.packets';path=reference/name;expected=evidence['channels'+str(channels)]['files'][name]
            need(pin(path)=={k:expected[k] for k in ('bytes','sha256')},'exact unchanged creator-valid full packet bodies')
            freeze(path,Path('fixtures')/name);report['fixtures'][name]=pin(path)
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0]
        compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip();report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip()
        library=command('libopus-link-path',['/usr/bin/gcc','-print-file-name=libopus.so.0']).decode().strip();need(library.startswith('/usr/') and '\n' not in library,'installed public creator library')
        library=command('libopus-path',['readlink','-f',library]).decode().strip();report['libopus_identity']=command('libopus-sha',['sha256sum',library]).decode().strip()
        binary=out/'helpers';command('build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-Wshadow',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-MMD','-MF',host(out/'helpers.d'),
            '-I'+host(out/'sources/idf/components/native_stream/include'),host(out/'sources/tests/native/opus_family1_helpers_host.c'),
            '-l:libopus.so.0','-lm','-o',host(binary)])
        report['executable']=dict(path=binary.name,local_only=True,**pin(binary));report['compiler_dependencies']=dict(path='helpers.d',**pin(out/'helpers.d'));save()
        data=command('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),
            *[host(out/'fixtures'/('channels'+str(c)+'.packets')) for c in (3,6,8)]])
        rows=[json.loads(line) for line in data.decode().splitlines()];report['measurements']=rows;save()
        need(len(rows)==16 and rows[0]['valid_nm_pairs']==16511 and rows[0]['all_channel_counts']==132088 and rows[0]['all_decoded_indices']>2000000 and
            rows[-1]['passed'] and rows[-1]['creator_cases']==11 and rows[-1]['assertions']>6000000,'complete exhaustive syntax and meaningful independent creator differential inventory')
        creator=[r for r in rows if r['suite']=='creator-differential'];extreme=[r for r in rows if r['suite']=='creator-extreme-plc']
        need(len(creator)==11 and all(r['bounded_gather_exact'] and r['float_samples_exact']>0 and r['needed_handles']<=8 for r in creator) and
            [(r['streams'],r['coupled'],r['decoded_channels']) for r in extreme]==[(255,0,255),(128,127,255)] and all(r['exact'] for r in extreme),
            'real active/default/arbitrary duplicate/silent/unused maps and creator-valid maximum-N PLC boundaries')
        need(command('libopus-post-sha',['sha256sum',library]).decode().strip()==report['libopus_identity'],'unchanged reference library')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all original/frozen input bindings current')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),summary=rows[-1])));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
