"""Execute only owned ESP32-C2 JPEG/NOR VMs and compare complete physical flash."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[4]


def sha(data):
    """Identify the exact firmware, emulator, flash and raw evidence bytes."""
    return hashlib.sha256(data).hexdigest()


def events(path):
    """SDK boot logs alone cannot pass the decoder gate."""
    result=[]
    for line in path.read_text(encoding='utf-8',errors='replace').splitlines() if path.exists() else []:
        if line.startswith('JPEG_DECODER_PROBE '):result.append(json.loads(line[len('JPEG_DECODER_PROBE '):]))
    return result


def boot(vm,options,state):
    """Own the new process handle and QMP, then stop/reap even after failure."""
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    session=None;handle=None;result={}
    try:
        session,prepared=vm.launch(options,state)
        handle=kernel.OpenProcess(0x100000,False,session['pid'])
        if not handle:raise ctypes.WinError(ctypes.get_last_error())
        before=(state/'flash.bin').read_bytes() # CPU remains paused.
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            qmp.execute('cont');deadline=time.monotonic()+300
            while time.monotonic()<deadline:
                rows=events(state/'uart.log')
                if any(row.get('event')=='failure' for row in rows):raise AssertionError(rows)
                if any(row.get('event')=='complete' for row in rows):break
                assert qmp.execute('query-status')['status']=='running'
                time.sleep(.2)
            else:raise TimeoutError('Owned JPEG decoder probe did not finish; UART retained')
        result=dict(session=session,sources=prepared['sources'],events=rows,owners_stopped=False)
    finally:
        if session:
            try:
                if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(state,'stop')
                if handle and kernel.WaitForSingleObject(handle,10000)!=0:raise RuntimeError('Owned JPEG QEMU did not exit')
            finally:
                if handle:kernel.CloseHandle(handle)
    result['owners_stopped']=True
    return result,before,(state/'flash.bin').read_bytes()


def main():
    """Two actual processes keep physical bytes; no guest memory/PC manipulation."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha((args.qemu_root/row['file']).read_bytes())==row['sha256'],row['file']
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    archive=ROOT/'firmware/development/small-tv-jpeg-decoder-probe';manifest=json.loads((archive/'manifest.json').read_text())
    elf=args.build/'small_tv_jpeg_decoder_probe.elf';assert sha(elf.read_bytes())==manifest['elf_sha256']
    build_inputs=json.loads((args.build/'inputs.json').read_text())
    assert all(sha(Path(p).read_bytes())==h for p,h in build_inputs.items())
    profile=ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'
    destination=args.output/'bundle/firmware/development/small-tv-esp32c2-reconstructed';destination.mkdir(parents=True)
    for row in manifest['images']:
        data=(archive/row['file']).read_bytes();assert sha(data)==row['sha256'];(destination/row['file']).write_bytes(data)
    (destination/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
    plan=json.loads((args.build/'resources/plan.json').read_text());ranges=plan['backing']['extents']
    options=SimpleNamespace(yoradio=str(args.output/'bundle'),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(profile),network='offline',display='none',persistent=True,paused=True,gdb_port=0,http_base_port=-1)
    report=dict(passed=False,all_functionality_verified=False,physical_hardware_tested=False,network_tested=False,lcd_tested=False,
        app_sha256=next(r['sha256'] for r in manifest['images'] if r['file']=='app.bin'),elf_sha256=manifest['elf_sha256'],
        qemu_sha256=sha((args.qemu_root/'bin/qemu-system-riscv32.exe').read_bytes()),boots=[],
        inputs_sha256={str(Path(__file__).resolve()):sha(Path(__file__).read_bytes()),str(profile):sha(profile.read_bytes())})
    try:
        previous=None
        for number in range(2):
            result,before,after=boot(vm,options,args.output/'vm')
            # Preserve observations before assertions, including failed observers.
            result.update(passed=False,initial_flash_sha256=sha(before),final_flash_sha256=sha(after))
            images=args.output/'flash-images';images.mkdir(exist_ok=True)
            for data in (before,after):
                path=images/(sha(data)+'.bin')
                if not path.exists():path.write_bytes(data)
                else:assert path.read_bytes()==data
            report['boots'].append(result)
            shutil.copyfile(args.output/'vm/uart.log',args.output/f'uart-{number}.log')
            shutil.copyfile(args.output/'vm/session.json',args.output/f'session-{number}.json')
            if previous is not None:assert previous==before
            assert len(before)==len(after)==0x400000
            changed=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
            # FIXED_TEST: replaying identical coefficients may leave identical
            # physical bytes. Require initial writes and positive SDK traffic on
            # BOTH boots; always compare EVERY protected byte, including replay.
            if number==0:assert changed
            assert all(any(r['offset']<=i<r['offset']+r['bytes'] for r in ranges) for i in changed)
            rows=result['events'];complete=next(r for r in rows if r.get('event')=='complete')
            assert complete['passed'] and complete['cases']==7 and complete['heap_final_requested']==0
            cases=[r for r in rows if r.get('event')=='case'];assert len(cases)==7 and all(r['passed'] for r in cases)
            assert next(r for r in cases if r['case']=='recover')['reused']
            assert next(r for r in cases if r['case']=='lossless16')['program_bytes']==0
            assert next(r for r in cases if r['case']=='full-cmyk12')['program_bytes']>0
            result.update(passed=True,changed_bytes=len(changed));previous=after
            print('PASS JPEG target process',number+1,':',complete,flush=True)
        for row in frozen['files']:assert sha((args.qemu_root/row['file']).read_bytes())==row['sha256']
        assert all(sha(Path(p).read_bytes())==h for p,h in build_inputs.items())
        report.update(passed=True,frozen_inputs_unchanged=True,build_inputs_unchanged=True)
    finally:
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()
