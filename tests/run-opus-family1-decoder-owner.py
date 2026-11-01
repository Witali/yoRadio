"""Qualify anchored public handle ownership with a labelled creator-backed HOST seam."""
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
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
VENDOR=REPO/'.idf/esp-adf-libs/esp_audio_codec'
SOURCES=['idf/esp32-cyd2usb-native/main/opus_family1_decoder.h','idf/components/native_stream/include/opus_family1_mapping.h',
    'idf/components/native_stream/include/opus_multistream_framing.h','tests/native/opus_family1_decoder_host.c',
    'tests/native/opus_family1_public.h','tests/fixtures/opus_header_gain/generate.py','tests/run-opus-family1-decoder-owner.py']
LONG=ROOT/'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg'
LONG_SHA='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();reference=args.reference.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists() and reference.is_relative_to(ROOT/'.build'),'fresh ignored capture')
    need(sha(LONG)==LONG_SHA,'exact complete original120ms fixture');evidence=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['reference_fixtures']
    gain=json.loads((ROOT/'tests/results/cyd-opus-header-gain-20261101/manifest.json').read_bytes())
    need(sha(ROOT/'tests/fixtures/opus_header_gain/generate.py')==gain['canonical_source_sha256']['tests/fixtures/opus_header_gain/generate.py'],'reviewed data-only Ogg packet reader')
    out.mkdir(parents=True);report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},native_executed=False,production_selected=False,
        host_public_api_test_double=True,creator_synthesis_real=True,scripted_host_status_controls=True,owner_allocator_host_seam=True,native_esp_oom_qualified=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,relative):
        destination=out/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(Path(path).read_bytes());report['sources'].append(dict(path=str(Path(path).resolve()),snapshot=relative.as_posix(),**pin(path)))
    def command(name,argv):
        full=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv));row=dict(name=name,argv=full,state='starting',timeout_seconds=120);report['commands'].append(row);save();started=time.monotonic()
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
        for name in ('include/decoder/impl/esp_opus_dec.h','include/decoder/esp_audio_dec_reg.h','include/decoder/esp_audio_dec.h','include/esp_audio_types.h'):
            freeze(VENDOR/name,Path('sources/vendor')/name)
        paths=[]
        for c in (3,6,8):
            name='channels'+str(c)+'.packets';path=reference/name;expected=evidence['channels'+str(c)]['files'][name]
            need(pin(path)=={k:expected[k] for k in ('bytes','sha256')},'exact complete original20ms multistream packets');freeze(path,Path('fixtures')/name);paths.append(out/'fixtures'/name);report['fixtures'][name]=pin(path)
        freeze(LONG,Path('sources/fixtures/stereo-510-120ms.ogg'));reader_path=out/'sources/tests/fixtures/opus_header_gain/generate.py'
        spec=importlib.util.spec_from_file_location('reviewed_long_data_reader',reader_path);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        body=LONG.read_bytes();pages,packets=reader.parse(body);audio=packets[2:];need(len(audio)==92 and packets[0][9]==2,'all original full120ms audio packets')
        pre_skip=int.from_bytes(packets[0][10:12],'little');logical=int.from_bytes(body[pages[-1]['offset']+6:pages[-1]['offset']+14],'little')-pre_skip
        transport=struct.pack('<8s6I8s',b'OFAM101\0',2,1,1,pre_skip,logical,len(audio),bytes([0,1,0,0,0,0,0,0]))
        transport+=b''.join(struct.pack('<I',len(p))+p for p in audio);path=out/'fixtures/stereo120.packets';path.write_bytes(transport);paths.append(path)
        report['fixtures'][path.name]=dict(**pin(path),complete_original_packets=len(audio),coded_bodies_unchanged=True,source_sha256=LONG_SHA,pre_skip=pre_skip,logical_frames=logical)
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0];compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip()
        report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip();library=command('libopus-link-path',['/usr/bin/gcc','-print-file-name=libopus.so.0']).decode().strip();need(library.startswith('/usr/') and '\n' not in library,'installed public creator library')
        library=command('libopus-path',['readlink','-f',library]).decode().strip();report['libopus_identity']=command('libopus-sha',['sha256sum',library]).decode().strip();binary=out/'owner'
        command('build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-Wshadow','-fsanitize=address,undefined',
            '-fno-omit-frame-pointer','-fno-pie','-no-pie','-MMD','-MF',host(out/'owner.d'),'-I'+host(out/'sources/idf/components/native_stream/include'),
            '-I'+host(out/'sources/idf/esp32-cyd2usb-native/main'),'-I'+host(out/'sources/vendor/include'),'-I'+host(out/'sources/vendor/include/decoder'),
            '-I'+host(out/'sources/vendor/include/decoder/impl'),host(out/'sources/tests/native/opus_family1_decoder_host.c'),'-l:libopus.so.0','-lm','-o',host(binary)])
        report['executable']=dict(path=binary.name,local_only=True,**pin(binary));report['compiler_dependencies']=dict(path='owner.d',**pin(out/'owner.d'));save()
        result=json.loads(command('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),*[host(p) for p in paths]]))
        need(result['passed'] and result['positive_cases']==13 and result['host_contract_controls']==22 and result['creator_pcm_samples_exact']==2679360 and result['stable_cfg_addresses'] and
            result['scripted_host_statuses'] and result['owner_allocator_host_seam'] and result['native_esp_oom_qualified'] is False,'complete real creator synthesis and explicitly HOST-only contract/refusal cleanup inventory')
        report['measurements']=result;need(command('libopus-post-sha',['sha256sum',library]).decode().strip()==report['libopus_identity'],'unchanged creator library')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all original/frozen input bytes current')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),measurements=result)));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
