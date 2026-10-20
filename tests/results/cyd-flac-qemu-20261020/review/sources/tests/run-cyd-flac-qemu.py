"""Execute frozen shared custom FLAC on ESP32 SDK6.0.2 under local Xtensa QEMU.

130 independently FFmpeg-checked fixtures x4 feed schedules; every PCM byte is
compared in the actual core1 SDK callback. This adapter/core gate does not run
the actual CYD decoder_task, inject OOM, use RF/DMA or touch a physical device.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT/'tests/target/cyd_flac_qemu'
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--idf',type=Path,default=Path('C:/Work/yoRadio/.idf/v6.0.2'))
    parser.add_argument('--idf-tools',type=Path,default=Path('C:/Work/yoRadio/.idf/tools-v6.0.2'))
    parser.add_argument('--idf-python',type=Path,help='Pinned SDK virtualenv Python; defaults below --idf-tools')
    parser.add_argument('--qemu',type=Path,default=Path('C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe'))
    parser.add_argument('--rom-directory',type=Path,default=Path('C:/Work/QEMU-ESP32/pc-bios'))
    parser.add_argument('--ffmpeg',type=Path,help='FFmpeg executable; defaults to PATH')
    parser.add_argument('--powershell',type=Path,help='PowerShell7 executable; defaults to PATH')
    parser.add_argument('--build-timeout',type=int,default=600)
    parser.add_argument('--qemu-timeout',type=int,default=480)
    args=parser.parse_args()
    if sys.platform!='win32':parser.error('This SDK/QEMU launcher currently supports Windows only')
    if not 1<=args.build_timeout<=3600 or not 1<=args.qemu_timeout<=3600:
        parser.error('Build and emulator timeouts must be1..3600 seconds')
    out=args.output.resolve()
    if out==ROOT or out in ROOT.parents or (out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/'.build')):
        parser.error('Use a fresh output below repository .build/ or outside the repository; source directories are protected')
    sdk=args.idf.resolve();idf_tools=args.idf_tools.resolve()
    idf_python=(args.idf_python or idf_tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe').resolve()
    qemu=args.qemu.resolve();rom_directory=args.rom_directory.resolve()
    ffmpeg_value=args.ffmpeg or shutil.which('ffmpeg')
    powershell_value=args.powershell or shutil.which('pwsh.exe') or shutil.which('pwsh')
    if not ffmpeg_value or not powershell_value:parser.error('FFmpeg and PowerShell7 are required')
    ffmpeg=Path(ffmpeg_value).resolve();powershell=Path(powershell_value).resolve()
    if any(out==path or out.is_relative_to(path) for path in (sdk,idf_tools,qemu.parent,rom_directory,ffmpeg.parent)):
        parser.error('Output must not overlap installed SDK/tool/ROM directories')
    if not out.is_relative_to(ROOT/'.build'):
        enclosing=next((path for path in out.parents if (path/'.git').exists()),None)
        if enclosing and not out.is_relative_to(enclosing/'.build'):
            parser.error('Output inside another repository must be below its .build/ directory')
    required=[sdk/'tools/idf.py',sdk/'export.ps1',idf_tools/'idf-env.json',idf_python,qemu,
        rom_directory/'esp32-v3-rom.bin',rom_directory/'esp32-v3-rom-app.bin',ffmpeg,powershell]
    if any(not path.is_file() for path in required):
        parser.error('Missing installed dependencies: '+', '.join(str(path) for path in required if not path.is_file()))
    out.mkdir(parents=True,exist_ok=False)
    report = {'passed':False,'scope':__doc__,'physical_hardware':False,
        'actual_cyd_decoder_task':False,'oom_injection':False,'source_sha256':{},'commands':[]}
    files = ['idf/components/custom_flac/CMakeLists.txt','idf/components/custom_flac/custom_flac_adapter.cpp',
        'idf/components/custom_flac/custom_flac_adapter.h','idf/components/custom_codec_support/CMakeLists.txt',
        'idf/components/custom_codec_support/Arduino.h','yoRadio/src/audioI2S/CodecMemoryArena.cpp',
        'yoRadio/src/audioI2S/CodecMemoryArena.h','yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp',
        'yoRadio/src/audioI2S/flac_decoder/flac_decoder.h','tools/audio_test_server/generate_flac_depths.py']
    frozen=out/'sources/repository'
    for name in files:
        path=ROOT/name;target=frozen/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        report['source_sha256'][str(path)]=sha(path)
    for path in [*sorted((HARNESS/'project').rglob('*')),HARNESS/'sdk-build.ps1',HARNESS/'README.md']:
        if not path.is_file():continue
        target=out/'sources/harness'/path.relative_to(HARNESS);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        report['source_sha256'][str(path)]=sha(path)
    runner=Path(__file__).resolve();target=out/'sources/runner'/runner.name
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(runner.read_bytes())
    report['source_sha256'][str(runner)]=sha(runner)
    frozen_hashes={str(path.relative_to(out)):sha(path) for path in (out/'sources').rglob('*') if path.is_file()}
    tool_paths = [qemu,rom_directory/'esp32-v3-rom.bin',rom_directory/'esp32-v3-rom-app.bin',
        idf_python,sdk/'tools/tools.json',powershell]
    report['runtime_sha256']={str(path):sha(path) for path in tool_paths}
    environment=os.environ.copy();environment['GIT_OPTIONAL_LOCKS']='0';environment['PYTHONUTF8']='1'

    def execute(name,command,timeout=60, binary=False):
        started=time.monotonic()
        child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env=environment,
            creationflags=subprocess.CREATE_NO_WINDOW)
        try: log,_=child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=15)
            log,_=child.communicate(timeout=15);(out/(name+'.log')).write_bytes(log)
            raise RuntimeError(name+' timed out')
        if not binary:(out/(name+'.log')).write_bytes(log)
        report['commands'].append({'name':name,'command':command,'exit_status':child.returncode,
            'elapsed_seconds':time.monotonic()-started,'output_sha256':hashlib.sha256(log).hexdigest()})
        if child.returncode:raise RuntimeError(name+' failed: '+log.decode(errors='replace')[-6000:])
        return log if binary else log.decode(errors='replace')

    try:
        sdk_head=execute('sdk-head',['git','-c','core.longpaths=true','-C',str(sdk),'rev-parse','HEAD']).strip()
        assert sdk_head==SDK_COMMIT
        assert not execute('sdk-tracked-changes',['git','-c','core.longpaths=true','-C',str(sdk),'status','--porcelain','--untracked-files=no']).strip()
        report['sdk_commit']=sdk_head
        report['runtime_sha256'][str(ffmpeg)]=sha(ffmpeg)
        execute('ffmpeg-version',[str(ffmpeg),'-version'])
        sys.dont_write_bytecode=True
        spec=importlib.util.spec_from_file_location('frozen_fixtures',frozen/'tools/audio_test_server/generate_flac_depths.py')
        generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
        small=generator.generate(out/'fixtures/small');large=generator.generate(out/'fixtures/large',large_blocks=True)
        rows=[(out/'fixtures/small',row) for row in small['fixtures']]+[(out/'fixtures/large',row) for row in large['fixtures']]
        assert len(rows)==130 and len({row['name'] for _,row in rows})==130
        data=bytearray(16+len(rows)*96);struct.pack_into('<4I',data,0,0x514c4643,1,len(rows),96)
        fixtures=[]
        for index,(folder,row) in enumerate(rows):
            encoded=folder/row['file'];assert sha(encoded)==row['sha256']
            pcm=execute('ffmpeg-'+str(index),[str(ffmpeg),'-v','error','-xerror','-i',str(encoded),'-f','s16le','-acodec','pcm_s16le','-'],binary=True)
            assert len(pcm)==row['pcm_bytes'] and hashlib.sha256(pcm).hexdigest()==row['pcm_sha256'],row['name']
            expected=encoded.with_suffix('.pcm');expected.write_bytes(pcm)
            data.extend(bytes((-len(data))%4));encoded_offset=len(data);data.extend(encoded.read_bytes())
            data.extend(bytes((-len(data))%4));pcm_offset=len(data);data.extend(pcm)
            name=row['name'].encode('ascii');assert len(name)<64
            struct.pack_into('<8I64s',data,16+index*96,index,row['bits'],row['channels'],row['rate'],
                encoded_offset,row['bytes'],pcm_offset,row['pcm_bytes'],name)
            fixtures.append({'id':index,**row,'encoded_path':str(encoded),'expected_pcm_path':str(expected),
                'encoded_offset':encoded_offset,'pcm_offset':pcm_offset,'ffmpeg_byte_oracle':True})
        assert len(data)<=0x300000
        blob=out/'fixtures.bin';blob.write_bytes(data)
        (out/'fixture-manifest.json').write_text(json.dumps(fixtures,indent=2)+'\n',encoding='utf-8')
        report['fixture_count']=len(fixtures);report['fixture_blob_bytes']=len(data)
        fixture_hashes={str(path.relative_to(out)):sha(path) for path in (out/'fixtures').rglob('*') if path.is_file()}
        fixture_hashes['fixtures.bin']=sha(blob);fixture_hashes['fixture-manifest.json']=sha(out/'fixture-manifest.json')
        print('Frozen130 fixtures; independentFFmpeg PCM16 identity verified; blob',len(data),'bytes',flush=True)
        execute('build',[str(powershell),'-NoLogo','-NoProfile','-NonInteractive','-File',
            str(out/'sources/harness/sdk-build.ps1'),'-OutputDirectory',str(out),'-IdfDirectory',str(sdk),
            '-IdfToolsDirectory',str(idf_tools),'-IdfPythonExecutable',str(idf_python)],timeout=args.build_timeout)
        build=out/'build';description=json.loads((build/'project_description.json').read_text())
        assert description['target']=='esp32' and Path(description['idf_path']).resolve()==sdk
        elf=build/description['app_elf'];app=build/description['app_bin']
        assert elf.read_bytes()[:4]==b'\x7fELF' and struct.unpack_from('<H',elf.read_bytes(),18)[0]==94
        assert app.read_bytes()[0]==0xe9 and struct.unpack_from('<H',app.read_bytes(),12)[0]==0
        config=json.loads((build/'config/sdkconfig.json').read_text())
        assert not config['FREERTOS_UNICORE'] and config['HEAP_POISONING_LIGHT'] and config['FREERTOS_CHECK_STACKOVERFLOW_CANARY'] and config['COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE']
        commands=json.loads((build/'compile_commands.json').read_text())
        for name in ['idf/components/custom_flac/custom_flac_adapter.cpp','yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp']:
            selected=[row for row in commands if Path(row['file']).resolve()==(frozen/name).resolve()]
            assert len(selected)==1 and '-DFLAC_OUTPUT_FRAMES=512' in selected[0]['command'] and '-DFLAC_SEGMENTED_WORKSPACE=1' in selected[0]['command'] and '-O3' in selected[0]['command']
        compiler=Path(description['c_compiler']);report['runtime_sha256'][str(compiler)]=sha(compiler)
        execute('compiler-version',[str(compiler),'--version'])
        cache=(build/'CMakeCache.txt').read_text()
        for name,key in [('ninja','CMAKE_MAKE_PROGRAM'),('cmake','CMAKE_COMMAND')]:
            path=Path(re.search(r'^'+key+r':[A-Z_]+=(.+)$',cache,re.M).group(1).strip())
            report['runtime_sha256'][str(path)]=sha(path);execute(name+'-version',[str(path),'--version'])
        recipe=json.loads((build/'flasher_args.json').read_text())
        assert recipe['extra_esptool_args']['chip']=='esp32' and recipe['bootloader']['offset']=='0x1000' and recipe['app']['offset']=='0x10000'
        parts=(build/'partition_table/partition-table.bin').read_bytes();ranges=[]
        for offset in range(0,len(parts),32):
            magic=struct.unpack_from('<H',parts,offset)[0]
            if magic==0xffff:break
            if magic==0xebeb:
                assert parts[offset+16:offset+32]==hashlib.md5(parts[:offset]).digest();break
            assert magic==0x50aa
            kind,subtype,address,size,label,flags=struct.unpack_from('<BBII16sI',parts,offset+2)
            assert address+size<=0x400000 and size
            ranges.append((address,address+size,label.rstrip(b'\0').decode()))
        ranges.sort();assert all(a[1]<=b[0] for a,b in zip(ranges,ranges[1:]))
        assert (0x10000,0x100000,'factory') in ranges and (0x100000,0x400000,'fixtures') in ranges
        assert app.stat().st_size<=0xf0000
        flash=out/'qemu-flash.bin';merge=[str(idf_python),'-m','esptool','--chip','esp32','merge-bin','--output',str(flash),*recipe['write_flash_args']]
        flash_files=[(int(offset,0),build/filename) for offset,filename in recipe['flash_files'].items()]+[(0x100000,blob)]
        for offset,path in sorted(flash_files):merge.extend([hex(offset),str(path)])
        merge.extend(['--pad-to-size','4MB']);execute('merge',merge)
        merged=flash.read_bytes();assert len(merged)==0x400000
        assert all(merged[offset:offset+path.stat().st_size]==path.read_bytes() for offset,path in flash_files)
        artifacts=[elf,app,flash,build/'project_description.json',build/'flasher_args.json',build/'compile_commands.json',
            build/'config/sdkconfig.json',out/'sdkconfig',build/'partition_table/partition-table.bin']
        artifact_hashes={str(path.relative_to(out)):sha(path) for path in artifacts}
        bundle={'frozen_sources_sha256':frozen_hashes,'fixture_sha256':fixture_hashes,
            'runtime_sha256':report['runtime_sha256'],'artifact_sha256':artifact_hashes,'sdk_commit':sdk_head,
            'partitions':ranges,'expected_unique_cases':520,'feed_schedules':[0,1,127,2048]}
        (out/'execution-bundle.json').write_text(json.dumps(bundle,indent=2)+'\n',encoding='utf-8')
        report['execution_bundle_sha256']=sha(out/'execution-bundle.json')
        print('ActualXtensa build+image/config/flash verified; starting520case QEMU matrix',flush=True)
        execute('qemu-version',[str(qemu),'--version'])
        log=execute('qemu',[str(qemu),'-M','esp32','-smp','2','-L',str(rom_directory),
            '-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none',
            '-drive','file='+str(flash).replace(',',',,')+',if=mtd,format=raw'],timeout=args.qemu_timeout)
        assert len(re.findall(r'CYD_FLAC_QEMU_BOOT target=esp32 sdk=v6\.0\.2\b.*owner_core=1 coordinator_core=0 output_frames=512',log))==1
        actual=[json.loads(line.split('CYD_FLAC_QEMU_CASE ',1)[1]) for line in log.splitlines() if line.startswith('CYD_FLAC_QEMU_CASE ')]
        assert len(actual)==520 and len({(row['id'],row['schedule']) for row in actual})==520
        assert {(row['id'],row['schedule']) for row in actual}=={(i,s) for i in range(130) for s in (0,1,127,2048)}
        for row in actual:
            assert row['pcm_bytes']==fixtures[row['id']]['pcm_bytes'] and row['callbacks']>0 and row['feeds']>0 and row['stack_free']>0
        assert len(re.findall(r'CYD_FLAC_QEMU_COMPLETE fixtures=130 cases=520 guards=48 byte_compare=1 heap_integrity=1 owner_core=1 coordinator_core=0 actual_cyd_task=0 oom_injection=0 hardware=0',log))==1
        assert not re.search(r'Guru Meditation|assert failed|panic.ed|watchdog.*triggered|stack smashing|CORRUPT HEAP',log,re.I)
        assert all(sha(Path(name))==digest for name,digest in report['source_sha256'].items())
        for group in [frozen_hashes,fixture_hashes,artifact_hashes]:assert all(sha(out/name)==digest for name,digest in group.items())
        assert all(sha(Path(name))==digest for name,digest in report['runtime_sha256'].items())
        assert execute('sdk-head-after',['git','-c','core.longpaths=true','-C',str(sdk),'rev-parse','HEAD']).strip()==sdk_head
        assert not execute('sdk-tracked-changes-after',['git','-c','core.longpaths=true','-C',str(sdk),'status','--porcelain','--untracked-files=no']).strip()
        report.update(passed=True,exact_pcm_cases=actual,guards=48,all_bound_inputs_current=True,
            warnings=re.findall(r'^.*\bwarning:.+$',(out/'build.log').read_text(errors='replace'),re.M))
    finally:
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('PASS130 fixtures x4schedules=520 exactPCM16 comparisons +48 SDKguards; adapter/core only',flush=True)


if __name__=='__main__':
    main()
