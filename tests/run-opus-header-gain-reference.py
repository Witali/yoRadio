"""Decode complete raw Opus packets with installed public libopus and explicit gain.

No vendor or firmware executes here. Original packets remain identical across
three gain variants; reference gain is applied to float output before PCM16
rounding/clipping. Actual tools, frozen source, logs/statuses and local PCM are
bound. This observes the reference, not a new numeric-conformance tolerance.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=Path('tests/native/opus_header_gain_reference.c')
GENERATOR=Path('tests/fixtures/opus_header_gain/generate.py')
SOURCE=Path('tests/fixtures/esp32c3_calibration/opus-510.ogg')


def need(value,why):
    if not value:raise ValueError(why)


def sha(body):return hashlib.sha256(body).hexdigest()


def pin(path):
    path=Path(path);return dict(bytes=path.stat().st_size,sha256=sha(path.read_bytes()))


def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh ignored capture');out.mkdir(parents=True)
    report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},vendor_executed=False,production_code_changed=False)
    report_path=out/'report.json'
    def save():report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def command(name,argv,timeout=120):
        full=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+argv
        row=dict(name=name,argv=full,state='starting');report['commands'].append(row);save();start=time.monotonic()
        with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
            child=subprocess.Popen(full,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL)
            row.update(pid=child.pid,state='running');save()
            try:status=child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-start,3))
        for stream in ('stdout','stderr'):
            path=out/(name+'.'+stream+'.log');row[stream]=dict(path=path.name,**pin(path))
        save();need(status==0 and not row.get('timed_out'),'actual terminal zero: '+name)
        return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        for relative in (Path(__file__).resolve().relative_to(ROOT),REFERENCE,GENERATOR,SOURCE):
            body=(ROOT/relative).read_bytes();snapshot=out/'sources'/relative;snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(body)
            report['sources'].append(dict(path=relative.as_posix(),snapshot=snapshot.relative_to(out).as_posix(),**pin(snapshot)))
        spec=importlib.util.spec_from_file_location('reviewed_opus_header_gain_data',ROOT/GENERATOR)
        generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
        source=(ROOT/SOURCE).read_bytes();need(sha(source)==generator.SOURCE_SHA,'exact complete source')
        pages,packets=generator.parse(source);need(len(packets)==553 and len(pages)==15,'all original packets/pages')
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0]
        compiler=command('compiler-realpath',['readlink','-f','/usr/bin/gcc']).decode().strip()
        report['compiler_identity']=command('compiler-sha256',['sha256sum',compiler]).decode().strip()
        library=command('libopus-path',['/usr/bin/gcc','-print-file-name=libopus.so.0']).decode().strip()
        need(library.startswith('/usr/') and '\n' not in library,'installed public libopus path')
        library=command('libopus-realpath',['readlink','-f',library]).decode().strip()
        report['libopus_identity']=command('libopus-sha256',['sha256sum',library]).decode().strip()
        binary=out/'reference'
        command('reference-build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',host(out/'sources'/REFERENCE),
            '-l:libopus.so.0','-lm','-o',host(binary)])
        report['executable']=dict(path=binary.name,local_only=True,**pin(binary));save()
        for name,gain in generator.VARIANTS:
            changed=generator.mutate(source,gain);audit=generator.verify_pair(source,changed,gain)
            _,variant_packets=generator.parse(changed);need(variant_packets[2:]==packets[2:],'all original encoded audio packets unchanged')
            packet_path=out/(name+'.packets')
            body=struct.pack('<8sIIQIi',b'OGAIN01\0',48000,2,528960,551,gain)
            body+=b''.join(len(packet).to_bytes(4,'little')+packet for packet in variant_packets[2:]);packet_path.write_bytes(body)
            pcm=out/(name+'.pcm')
            result=json.loads(command(name+'-reference',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),host(packet_path),host(pcm)]))
            need(result['reference'].startswith('libopus ') and result['gain_q8']==gain and result['packets']==551 and
                 result['raw_frames']==528960 and result['pcm_bytes']==2115840 and result['nonzero']>0 and
                 result['library_header_gain_used'] is False and result['numeric_conformance_claim'] is False,
                 'complete public raw reference and explicit normative gain')
            need(pcm.stat().st_size==2115840,'all full raw PCM written')
            report['fixtures'][name]=dict(audit=audit,measurements=result,
                packet_transport=dict(path=packet_path.name,local_only=True,**pin(packet_path)),
                pcm=dict(path=pcm.name,local_only=True,**pin(pcm)));save()
        values=[row['measurements'] for row in report['fixtures'].values()]
        need(len({(r['raw_float_peak'],r['raw_float_energy']) for r in values})==1,'same raw float signal before gain in all fresh reference handles')
        need(len({row['pcm']['sha256'] for row in report['fixtures'].values()})==3,'three genuine distinct normative gained PCM outputs')
        need(command('libopus-post-sha256',['sha256sum',library]).decode().strip()==report['libopus_identity'],'reference library unchanged')
        need(command('compiler-post-sha256',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'compiler unchanged')
        for row in report['sources']:
            need(pin(ROOT/row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all source snapshots unchanged')
        report.update(passed=True,completed=True,all_source_bindings_current=True)
        print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),
            gains={name:row['measurements'] for name,row in report['fixtures'].items()})))
        return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
