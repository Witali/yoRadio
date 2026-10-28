"""Boot an actual stopped pre-publication image and replace its interrupted JPEG."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from photo_owner_qemu import multipart,process_handle,Probe
from photo_flash_evidence import ready_frame,journal
import weather_qemu as weather

ROOT=Path(__file__).resolve().parents[3]


def sha(path):
    """Identify the actual interrupted snapshot and replacement input."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Use ordinary boot/HTTP only; no guest RAM, code or register writes."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--interrupted-flash',type=Path,required=True)
    parser.add_argument('--expected-frame-sha256',required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    from qemu_storage import direct_flash_backing
    weather.vm=vm
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    initial=args.interrupted_flash.read_bytes();assert len(initial)==0x400000
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest=json.loads((archive/'manifest.json').read_text())
    plan=json.loads((archive/'jpeg-cache-plan.json').read_text())
    head=journal(initial,plan);assert not head['entries'][4]['ready']
    fixture=ROOT/'Small_TV/src/tests/fixtures/jpeg_extended/flat-gray-progressive-8.jpg'
    files=[Path(__file__),Path(weather.__file__),args.interrupted_flash,fixture,*[archive/n for n in
        ('app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json','jpeg-cache-plan.json')]]
    inputs={str(p.resolve()):sha(p) for p in files}
    report=dict(passed=False,all_functionality_verified=False,hardware_tested=False,physical_power_cut_tested=False,
        lcd_tested=False,network_lifecycle_tested=False,app_sha256=next(x['sha256'] for x in manifest['images'] if x['file']=='app.bin'),
        elf_sha256=manifest['elf_sha256'],source_sha256=manifest['source_sha256'],inputs_sha256=inputs,
        interrupted_journal_generation=head['generation'],interrupted_flash_sha256=sha(args.interrupted_flash),
        scope='Actual stopped VM before JPEG publication; next real boot/upload/decode/readback; not a bit-level physical power cut',probes=[])
    previous=vm.seed_clock_network
    vm.seed_clock_network=lambda data,variant,state,yoradio,ssid=None:initial
    server=weather.WeatherFixture();server.set_response(200)
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
        persistent=True,paused=True,gdb_port=0,http_base_port=0,service_port=server.port)
    session=kernel=handle=probe=None;state=args.output/'vm';executor=ThreadPoolExecutor(max_workers=1)
    try:
        session,prepared=vm.launch(options,state);kernel,handle=process_handle(session['pid'])
        assert (state/'flash.bin').read_bytes()==initial
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            assert direct_flash_backing(qmp,state);qmp.execute('cont')
        url=session['web_urls']['station'];wait_http(url,'/getclocktype')
        status,body=http(url,'/get_Photo_File?file=5&chunk=0&size=0')
        assert status==200 and json.loads(body)==dict(exists=False,size=0)
        data=fixture.read_bytes();chunks=(len(data)+4095)//4096
        assert http(url,'/start_upload',dict(file_number=5,file_size=len(data),total_chunks=chunks),origin=url,timeout=30)==(200,b'OK')
        for index in range(chunks):assert multipart(url,5,index,chunks,data[index*4096:(index+1)*4096])==(200,b'OK')
        pending=executor.submit(http,url,'/finish_upload',dict(file_number=5,file_name='file5.jpg'),900,url)
        probe=Probe(url)
        while not pending.done():
            status,body=probe.get();assert status==200 and body
            report['probes'].append(dict(status=status,finish_pending=not pending.done()))
        status,body=pending.result();assert status==200 and body==b'OK'
        status,body=http(url,'/get_Photo_File?file=5&chunk=0&size=0')
        assert status==200 and json.loads(body)==dict(exists=True,size=len(data))
        assert clean_uart(state)
        probe.close();probe=None;vm.control(state,'stop');assert kernel.WaitForSingleObject(handle,10000)==0
        kernel.CloseHandle(handle);handle=None;session=None
        after=(state/'flash.bin').read_bytes()
        report['cache']=ready_frame(after,plan,4,sha(fixture),args.expected_frame_sha256)
        mutable=sorted([(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]+
            [(r['offset'],r['offset']+r['bytes']) for r in plan['candidate_extents']])
        cursor=0
        for start,end in mutable:assert initial[cursor:start]==after[cursor:start];cursor=end
        assert initial[cursor:]==after[cursor:]
        assert all(sha(Path(p))==digest for p,digest in inputs.items())
        report.update(passed=True,owners_stopped=True,protected_flash_exact=True,after_sha256=sha(state/'flash.bin'))
    except Exception as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if probe:probe.close()
        if session:
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(state,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
        executor.shutdown(wait=True,cancel_futures=True);server.close();vm.seed_clock_network=previous
        vm.save_json(args.output/'report.json',report)
    print('PASS actual interrupted-decode recovery:',report['cache'],flush=True)


if __name__=='__main__':main()
