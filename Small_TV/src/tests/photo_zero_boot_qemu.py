"""Forbid startup JPEG stamp programming when a persisted zero limit is loaded."""
import argparse
import json
from pathlib import Path
import socket
import sys
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ELFFile,ROOT
from photo_owner_qemu import process_handle
from photo_write_budget_qemu import descriptions,stop_at,trace_return
from qemu_storage import direct_flash_backing
import weather_qemu as weather


def main():
    """Use a disposable matching legacy copy; no physical device or guest writes."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--seed',type=Path,required=True,help='Stopped synthetic image with persisted JPEG limit0')
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    weather.vm=vm
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert vm.digest((args.qemu_root/row['file']).read_bytes())==row['sha256']
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest=json.loads((archive/'manifest.json').read_text());plan=json.loads((archive/'jpeg-cache-plan.json').read_text())
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf';entries,_=descriptions(elf)
    with elf.open('rb') as stream:
        values={s['st_value'] for s in ELFFile(stream).get_section_by_name('.symtab').iter_symbols() if s.name=='photo_worker_init'}
    assert len(values)==1;entry=next(iter(values))
    initial=bytearray(args.seed.read_bytes());assert len(initial)==0x400000
    # Preserve real saved preferences/NVS/source photos. Update only boot images
    # to this exact tested app, then construct vacant legacy scratch and stamp.
    for row in manifest['images']:
        if row['file'] in ('bootloader.bin','partition-table.bin','app.bin'):
            data=(archive/row['file']).read_bytes();assert vm.digest(data)==row['sha256']
            offset=int(row['offset'],0);initial[offset:offset+len(data)]=data
    for row in plan['candidate_extents']:initial[row['offset']:row['offset']+row['bytes']]=b'\xff'*row['bytes']
    assets=(archive/'assets.bin').read_bytes();stamp=assets.find(b'STVOWN1\0')
    assert stamp>=0 and assets.find(b'STVOWN1\0',stamp+1)<0
    stamp+=0x200000;assert stamp==0x28f720
    initial[stamp:stamp+64]=b'\xff'*64
    (args.output/'before.bin').write_bytes(initial)
    report=dict(passed=False,all_functionality_verified=False,network_acceptance=False,lcd_acceptance=False,
        hardware_tested=False,app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=manifest['elf_sha256'],
        source_sha256=manifest['source_sha256'],stamp_offset=stamp,owners_stopped=False,
        seed_sha256=vm.digest(args.seed.read_bytes()),before_sha256=vm.digest(initial),callbacks=[])
    files=[Path(__file__),Path(__file__).with_name('photo_write_budget_qemu.py'),Path(__file__).with_name('photo_owner_qemu.py'),
        Path(__file__).with_name('weather_qemu.py'),Path(__file__).with_name('gdb_observer.py'),
        elf,*[archive/n for n in ('manifest.json','source-manifest.json','app.bin','jpeg-cache-plan.json')],args.seed]
    report['inputs_sha256']={str(p.resolve()):vm.digest(p.read_bytes()) for p in files}
    server=weather.WeatherFixture();server.set_response(200);old_seed=vm.seed_clock_network
    vm.seed_clock_network=lambda *unused:initial
    session=observer=kernel=handle=None;folder=args.output/'vm'
    try:
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
        options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
            rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
            hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
            persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=server.port)
        session,prepared=vm.launch(options,folder);kernel,handle=process_handle(session['pid'])
        assert (folder/'flash.bin').read_bytes()==initial
        report.update(pid=session['pid'],name=session['name'])
        observer=Observer(port)
        with vm.QMP(session['qmp_port'],session['name']) as qmp:assert direct_flash_backing(qmp,folder)
        observer.breakpoint(entry);observer.breakpoint(entries['flash_program']);observer.breakpoint(entries['flash_erase'])
        assert stop_at(observer,set(observer.breakpoints))==entry
        observer.breakpoint(entry,False);returned=observer.register(1);observer.breakpoint(returned)
        report['callbacks']=trace_return(observer,entries,returned)
        report['init_status']=observer.register(10)
        for address in list(observer.breakpoints):observer.breakpoint(address,False)
        observer.resume();url=session['web_urls']['station'];wait_http(url,'/get_jpeg_write_limit')
        status,body=http(url,'/get_jpeg_write_limit');assert status==200 and json.loads(body)==dict(limit_kib=0)
        report['policy_kib']=0;assert clean_uart(folder)
        observer.close();observer=None
        vm.control(folder,'stop');assert kernel.WaitForSingleObject(handle,10000)==0
        kernel.CloseHandle(handle);handle=None;session=None;report['owners_stopped']=True
        after=(folder/'flash.bin').read_bytes();report['after_sha256']=vm.digest(after)
        assert not report['callbacks'],'Zero limit allowed startup JPEG program/erase'
        assert after[stamp:stamp+64]==b'\xff'*64
        for row in plan['candidate_extents']:assert initial[row['offset']:row['offset']+row['bytes']]==after[row['offset']:row['offset']+row['bytes']]
        assert all(vm.digest(Path(p).read_bytes())==digest for p,digest in report['inputs_sha256'].items())
        report['passed']=True
    except Exception as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if observer:observer.close()
        if session:
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(folder,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            report['owners_stopped']=True
        server.close();vm.seed_clock_network=old_seed;vm.save_json(args.output/'report.json',report)
    print('PASS zero-policy startup: unstamped legacy bytes stay unchanged',flush=True)


if __name__=='__main__':main()
