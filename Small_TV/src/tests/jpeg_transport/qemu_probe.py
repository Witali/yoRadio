"""Run only owned target storage VMs; no network/LCD criteria or physical flashing."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import sys
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[4]


def sha(data):
    """Identify exact firmware, generated resources and emulator inputs."""
    return hashlib.sha256(data).hexdigest()


def events(path):
    """Parse bounded structured probe lines; SDK boot logs are not pass criteria."""
    rows=[]
    for line in path.read_text(encoding='utf-8',errors='replace').splitlines() if path.exists() else []:
        if line.startswith('JPEG_TRANSPORT_PROBE '):rows.append(json.loads(line[len('JPEG_TRANSPORT_PROBE '):]))
    return rows


def boot(vm,options,state):
    """Own an actual process handle, start paused, wait for UART, quit and reap.

    A second call reopens the persistent drive in a fresh QEMU process. No old
    emulator RAM/cache is accepted as proof of cold persistence.
    """
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    session=None;handle=None
    try:
        session,prepared=vm.launch(options,state)
        handle=kernel.OpenProcess(0x100000,False,session['pid'])
        if not handle:raise ctypes.WinError(ctypes.get_last_error())
        before=(state/'flash.bin').read_bytes() # CPU is still paused: no baseline race.
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            qmp.execute('cont')
            for attempt in range(600):
                rows=events(state/'uart.log')
                if any(row.get('event')=='failure' for row in rows):raise AssertionError(rows)
                authorization=next((row for row in rows if row.get('event')=='authorization'),None)
                completed=next((row for row in rows if row.get('event')=='complete'),None)
                if authorization and (not authorization['authorized'] or completed):break
                assert qmp.execute('query-status')['status']=='running'
                time.sleep(.1)
            else:raise TimeoutError('Target storage probe did not finish')
        result=dict(session=session,sources=prepared['sources'],events=rows,owners_stopped=False)
    finally:
        if session:
            try:
                if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(state,'stop')
                if handle and kernel.WaitForSingleObject(handle,10000)!=0:raise RuntimeError('Owned QEMU did not exit')
            finally:
                if handle:kernel.CloseHandle(handle)
    after=(state/'flash.bin').read_bytes();result['owners_stopped']=True
    return result,before,after


def main():
    """FIXED_TEST: supply offline/reconstructed launch arguments and pause before
    capturing the pristine baseline. Check rejection, writes and fresh-process boot.
    """
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha((args.qemu_root/row['file']).read_bytes())==row['sha256'],row['file']
    sys.path.insert(0,str(args.qemu_root/'tools'))
    import small_tv_vm as vm
    archive=ROOT/'firmware/development/small-tv-storage-probe'
    source_manifest=json.loads((archive/'manifest.json').read_text())
    profile=ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'
    image={row['file']:(archive/row['file']).read_bytes() for row in source_manifest['images']}
    for row in source_manifest['images']:assert sha(image[row['file']])==row['sha256']
    report=dict(passed=False,scope=__doc__,physical_hardware_tested=False,network_tested=False,lcd_tested=False,
                app_sha256=sha(image['app.bin']),qemu_sha256=sha((args.qemu_root/'bin/qemu-system-riscv32.exe').read_bytes()),
                cases=[],inputs_sha256={str(Path(__file__).resolve()):sha(Path(__file__).read_bytes())})
    try:
        for variant in ('matching','unmarked','raw-unknown-flags','extra-partition'):
            folder=args.output/variant;bundle=folder/'bundle';copies=dict(image)
            if variant=='unmarked':
                body=bytearray(copies['assets.bin']);body[0x28f720-0x200000:0x28f720-0x200000+64]=b'\xff'*64;copies['assets.bin']=bytes(body)
            if variant in ('raw-unknown-flags','extra-partition'):
                table=bytearray(copies['partition-table.bin'])
                records=bytearray(table[:4*32])
                if variant=='raw-unknown-flags':struct.pack_into('<I',records,3*32+28,0x80)
                else:records+=struct.pack('<HBBII16sI',0x50aa,1,0x41,0x1f0000,4096,b'occupied',0)
                md5=b'\xeb\xeb'+b'\xff'*14+hashlib.md5(records).digest()
                copies['partition-table.bin']=bytes(records+md5+b'\xff'*(len(table)-len(records)-32))
            destination=bundle/'firmware/development/small-tv-esp32c2-reconstructed';destination.mkdir(parents=True)
            manifest=json.loads(json.dumps(source_manifest))
            for row in manifest['images']:
                data=copies[row['file']];(destination/row['file']).write_bytes(data);row.update(sha256=sha(data),bytes=len(data))
            (destination/'manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
            options=SimpleNamespace(yoradio=str(bundle),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
                rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
                hardware_profile=str(profile),network='offline',display='none',persistent=True,paused=True,gdb_port=0,http_base_port=-1)
            state=folder/'vm';case=dict(variant=variant,passed=False)
            try:
                first,before,after=boot(vm,options,state);case['boots']=[first]
                case['initial_flash_sha256']=sha(before)
                authorization=next((r for r in first['events'] if r.get('event')=='authorization'),None)
                completed=next((r for r in first['events'] if r.get('event')=='complete'),None)
                assert authorization and authorization['authorized']==(variant=='matching'),first['events']
                if variant=='matching':
                    assert completed and completed['passed'] and not completed['cold']
                    shutil.copyfile(state/'uart.log',folder/'uart-first.log')
                    cold,cold_before,cold_after=boot(vm,options,state);case['boots'].append(cold)
                    assert cold_before==after==cold_after
                    completed=next(r for r in cold['events'] if r.get('event')=='complete')
                    assert completed['cold'] and completed['passed']
                    assert completed['data_program_bytes']==completed['data_erases']==0
                if variant!='matching':assert after==before
                else:
                    changed=[i for i,(old,new) in enumerate(zip(before,after)) if old!=new]
                    expected={0x187000+4090+i:(0xff if i<5 else i+1) for i in range(32)}
                    expected.update({0x1fa000+i:37+i for i in range(8)})
                    assert changed==sorted(i for i,value in expected.items() if before[i]!=value)
                    assert all(after[i]==value for i,value in expected.items())
                    case['changed_bytes']=len(changed)
                case.update(passed=True,final_flash_sha256=sha(after),owners_stopped=True)
            finally:
                report['cases'].append(case)
        for row in frozen['files']:assert sha((args.qemu_root/row['file']).read_bytes())==row['sha256']
        report['frozen_inputs_unchanged']=True
        report['passed']=len(report['cases'])==4 and all(c['passed'] for c in report['cases'])
    finally:
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    processes=sum(len(case['boots']) for case in report['cases'])
    print('PASS target storage:',len(report['cases']),'variants,',processes,'owned processes; flash/cold boot/guard rejection')


if __name__=='__main__':
    main()
