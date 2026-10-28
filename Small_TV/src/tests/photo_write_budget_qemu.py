"""Count actual JPEG flash callbacks under a configurable per-image write quota."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
import socket
import struct
import sys
import time
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ELFFile,ROOT
from photo_owner_qemu import multipart,process_handle
from photo_flash_evidence import journal,ready_frame
from photo_target_state import shape
from qemu_storage import direct_flash_backing
import weather_qemu as weather


def descriptions(path):
    """Resolve unique real callbacks and the diagnostic wire in the exact ELF."""
    names={'flash_program','flash_erase','photo_upload_start_detailed',
        'photo_upload_finish_detailed','photo_worker_draw'}
    with path.open('rb') as stream:
        elf=ELFFile(stream);symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
        entries={name:{s['st_value'] for s in symbols if s.name==name and s['st_value']} for name in names}
        assert all(len(v)==1 for v in entries.values()),entries
        diagnostic=None
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name=die.attributes.get('DW_AT_name')
                if die.tag!='DW_TAG_typedef' or not name or name.value!=b'photo_diagnostic_t':continue
                value=shape(die)
                if value.get('fields'):
                    assert diagnostic is None or diagnostic==value
                    diagnostic=value
        assert diagnostic
    return {name:next(iter(values)) for name,values in entries.items()},diagnostic


def read_diagnostic(observer,address,layout):
    """Read returned numeric fields while the caller still owns this diagnostic."""
    raw=observer.memory(address,layout['bytes'])
    return {name:int.from_bytes(raw[field['offset']:field['offset']+field['bytes']],'little')
        for name,field in layout['fields'].items() if field['bytes'] in (1,2,4,8) and not field.get('fields')}


def stop_at(observer,addresses):
    """Use only unqualified continue and hardware breakpoints, never a PC write."""
    reply=observer.request('c');pc=observer.register(32)
    assert reply.startswith(('T05','S05')) and pc in addresses,(reply,hex(pc),addresses)
    return pc


def trace_return(observer,entries,returned):
    """Execute real raw callbacks to completion, counting every attempted byte."""
    program,erase=entries['flash_program'],entries['flash_erase'];events=[]
    while True:
        pc=stop_at(observer,{returned,program,erase})
        if pc==returned:break
        event=dict(kind='program' if pc==program else 'erase',address=observer.register(11),
            bytes=observer.register(13) if pc==program else 4096)
        code=observer.memory(pc,2);callback_return=observer.register(1)
        observer.breakpoint(pc,False);observer.breakpoint(callback_return)
        observer.continue_to(callback_return)
        event['status']=observer.register(10);assert event['status']==0,event
        observer.breakpoint(callback_return,False);observer.breakpoint(pc)
        assert observer.memory(pc,2)==code
        events.append(event);assert len(events)<10000
    return events


def operation(observer,entries,layout,executor,http,url,start,arguments):
    """Trace one ordinary asynchronous HTTP operation from real entry to return."""
    entry=entries['photo_upload_start_detailed' if start else 'photo_upload_finish_detailed']
    observer.breakpoint(entry)
    pending=executor.submit(http,url,'/start_upload' if start else '/finish_upload',arguments,900,url)
    observer.continue_to(entry);observer.breakpoint(entry,False)
    returned=observer.register(1);diagnostic=observer.register(13 if start else 11)
    for address in (returned,entries['flash_program'],entries['flash_erase']):observer.breakpoint(address)
    events=trace_return(observer,entries,returned)
    result=dict(callbacks=events,return_status=observer.register(10),diagnostic=read_diagnostic(observer,diagnostic,layout))
    for address in list(observer.breakpoints):observer.breakpoint(address,False)
    observer.resume();status,body=pending.result(timeout=90);observer.interrupt()
    result.update(status=status,body=body.decode(),program_bytes=sum(e['bytes'] for e in events if e['kind']=='program'),
        erase_calls=sum(e['kind']=='erase' for e in events))
    return result


def running_http(observer,http,url,path,values=None):
    """Issue a normal request with no debug stop left armed."""
    observer.resume()
    try:return http(url,path,values,30,url)
    finally:observer.interrupt()


def main():
    """Separate storage/policy gate, including real zero-limit cold cache draw."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
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
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf';entries,layout=descriptions(elf)
    fixtures=ROOT/'Small_TV/src/tests/fixtures/jpeg_extended'
    files=[Path(__file__),elf,*[Path(__file__).with_name(n) for n in
        ('gdb_observer.py','photo_owner_qemu.py','photo_flash_evidence.py','photo_target_state.py','qemu_storage.py','weather_qemu.py','control_oracle.py')],
        *[archive/n for n in ('app.bin','assets.bin','manifest.json','source-manifest.json','jpeg-cache-plan.json')],
        fixtures/'full-cmyk12.jpg',fixtures/'flat-gray-progressive-8.jpg']
    inputs={str(p.resolve()):vm.digest(p.read_bytes()) for p in files}
    report=dict(passed=False,all_functionality_verified=False,network_acceptance=False,lcd_acceptance=False,
        hardware_tested=False,app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=manifest['elf_sha256'],
        source_sha256=manifest['source_sha256'],qemu_sha256=vm.digest((args.qemu_root/'bin/qemu-system-riscv32.exe').read_bytes()),
        inputs_sha256=inputs,entries=entries,diagnostic_layout=layout,boots=[],cases=[])
    server=weather.WeatherFixture();server.set_response(200);old_seed=vm.seed_clock_network
    retained=None;session=observer=kernel=handle=None;executor=ThreadPoolExecutor(max_workers=1)
    try:
        for boot in range(2):
            folder=args.output/('warm' if boot==0 else 'cold');folder.mkdir()
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
            options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
                rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
                hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
                persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=server.port)
            if retained is not None:vm.seed_clock_network=lambda *unused:retained
            session,prepared=vm.launch(options,folder);kernel,handle=process_handle(session['pid'])
            report['boots'].append(dict(pid=session['pid'],name=session['name'],owners_stopped=False))
            before=(folder/'flash.bin').read_bytes();(folder/'before.bin').write_bytes(before)
            assert vm.digest(before)==prepared['prepared_flash_sha256']
            observer=Observer(port)
            with vm.QMP(session['qmp_port'],session['name']) as qmp:assert direct_flash_backing(qmp,folder)
            url=session['web_urls']['station']
            if boot==0:
                observer.resume();wait_http(url,'/getclocktype');observer.interrupt()
                status,body=running_http(observer,http,url,'/get_jpeg_write_limit');assert status==200 and json.loads(body)==dict(limit_kib=200)
                for name,accepted in (('full-cmyk12.jpg',False),('flat-gray-progressive-8.jpg',True)):
                    data=(fixtures/name).read_bytes();chunks=(len(data)+4095)//4096
                    start=operation(observer,entries,layout,executor,http,url,True,
                        dict(file_number=5,file_size=len(data),total_chunks=chunks))
                    assert start['status']==200 and start['body']=='OK'
                    observer.resume()
                    for index in range(chunks):assert multipart(url,5,index,chunks,data[index*4096:(index+1)*4096])==(200,b'OK')
                    observer.interrupt()
                    finish=operation(observer,entries,layout,executor,http,url,False,dict(file_number=5,file_name='file5.jpg'))
                    total=start['program_bytes']+finish['program_bytes'];assert total<=204800
                    assert finish['diagnostic']['program_bytes']==total
                    if accepted:assert finish['status']==200 and finish['body']=='OK' and not finish['diagnostic']['write_limit']
                    else:
                        assert finish['status']==400 and finish['body'].startswith('flash-write-limit;')
                        assert finish['diagnostic']['write_limit'] and finish['diagnostic']['required']>204800 and finish['diagnostic']['available']==204800
                        assert not journal((folder/'flash.bin').read_bytes(),plan)['entries'][4]['ready']
                    report['cases'].append(dict(name=name,start=start,finish=finish,total_program_bytes=total))
                    print('Budget:',name,finish['status'],'program',total,finish['body'],flush=True)
                assert running_http(observer,http,url,'/set_jpeg_write_limit',dict(limit_kib=0))==(200,b'OK')
                zero_before=(folder/'flash.bin').read_bytes();(folder/'zero-before.bin').write_bytes(zero_before)
                zero=operation(observer,entries,layout,executor,http,url,True,dict(file_number=5,file_size=508,total_chunks=1))
                assert zero['status']==400 and zero['body'].startswith('flash-writes-disabled;')
                assert not zero['program_bytes'] and not zero['erase_calls'] and zero_before==(folder/'flash.bin').read_bytes()
                report['zero_start']=zero
                for slot in range(1,5):
                    assert running_http(observer,http,url,'/set_checkbox_state',dict(checkbox_id=f'file{slot}-switch',checked=False))==(200,b'OK')
                # Factory/native theme2 is photo; theme3 is the analog dial.
                assert running_http(observer,http,url,'/setclocktype',dict(clocktype=2))==(200,b'OK')
                observer.resume();deadline=time.monotonic()+60
                while True:
                    raw=(folder/'flash.bin').read_bytes()
                    if struct.unpack_from('<I',raw,0x3e7000+0x168)[0]==2 and struct.unpack_from('<I',raw,0x3e7000+0x1a4)[0]==16:break
                    assert time.monotonic()<deadline;time.sleep(.1)
                observer.interrupt()
            else:
                assert before==retained
                # Trace from actual boot, not just after readiness publication.
                # A first nonblocking draw can meet the owner just before it
                # releases its mutex; observe the ordinary retry instead.
                observer.breakpoint(entries['flash_program']);observer.breakpoint(entries['flash_erase'])
                attempts=[]
                for attempt in range(10):
                    observer.breakpoint(entries['photo_worker_draw'])
                    pc=stop_at(observer,set(observer.breakpoints));assert pc==entries['photo_worker_draw'],'JPEG write during zero-policy boot'
                    observer.breakpoint(entries['photo_worker_draw'],False);assert observer.register(10)==4
                    returned=observer.register(1);observer.breakpoint(returned)
                    events=trace_return(observer,entries,returned);status=observer.register(10)
                    assert not events
                    attempts.append(status);observer.breakpoint(returned,False)
                    if status==0:break
                    assert status==0x103,'Unexpected readonly draw failure'
                assert attempts[-1]==0,'Readonly cached draw never completed'
                for address in list(observer.breakpoints):observer.breakpoint(address,False)
                status,body=running_http(observer,http,url,'/get_jpeg_write_limit');assert status==200 and json.loads(body)==dict(limit_kib=0)
                report['cold_zero_draw']=dict(source_slot=4,status=0,callbacks=events,policy_kib=0,attempts=attempts,
                    raw_callbacks_traced_from_reset=True)
            assert clean_uart(folder)
            observer.close();observer=None
            vm.control(folder,'stop');assert kernel.WaitForSingleObject(handle,10000)==0
            kernel.CloseHandle(handle);handle=None
            report['boots'][-1]['owners_stopped']=True
            session=None;after=(folder/'flash.bin').read_bytes()
            report.setdefault('frames',[]).append(ready_frame(after,plan,4,vm.digest((fixtures/'flat-gray-progressive-8.jpg').read_bytes()),
                'a3ec07b094d96c0fc6b420ba1a8666639a108c9e925c5f199c3e8f6f8ee10745'))
            if boot==0:retained=after
            else:
                for r in plan['candidate_extents']:
                    assert before[r['offset']:r['offset']+r['bytes']]==after[r['offset']:r['offset']+r['bytes']]
                report['cold_generated_bytes_unchanged']=True
        assert all(vm.digest(Path(p).read_bytes())==digest for p,digest in inputs.items())
        report['passed']=True
    except Exception as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if observer:observer.close()
        if session:
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(folder,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            report['boots'][-1]['owners_stopped']=True
        executor.shutdown(wait=True,cancel_futures=True);server.close();vm.seed_clock_network=old_seed
        vm.save_json(args.output/'report.json',report)
    print('PASS current C2 JPEG physical write quota and zero cold cache',flush=True)


if __name__=='__main__':main()
