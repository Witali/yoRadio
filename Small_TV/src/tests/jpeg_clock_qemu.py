"""Independent complete clock-frame continuity during real foreground JPEG work."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import argparse
import datetime as dt
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

from control_oracle import verify_inputs
from frame_replay import SceneMachine,panel_rgb,write_rgb_png
from gdb_observer import Observer
from machine_oracle import Machine,Panel,ROOT
from photo_cache_frames_qemu import native_entries
from photo_owner_qemu import multipart,process_handle
from photo_target_state import describe
import photo_runtime_metrics as metrics
from jpeg_clock_contract import validate,rejection_checks
from qemu_storage import direct_flash_backing
import scene_qemu as scene
import weather_qemu as weather


def stop_at(observer,addresses):
    """Continue normally to a hardware breakpoint, without assigning PC or RAM."""
    reply=observer.request('c');pc=observer.register(32)
    assert reply.startswith(('T05','S05')) and pc in addresses,(reply,hex(pc),addresses)
    return pc


def clean_frame(machine,theme,data,registers):
    """Rebuild every pixel from semantic inputs on a blank isolated reference LCD."""
    machine.panel=Panel()
    if theme=='classic':machine.render(data,reset=True,cursor=registers['a4'],force_status=True)
    else:
        scene.seed_time(machine,data)
        if theme=='simple':machine.simple(reset=True,second_update=True,minute_update=True)
        else:
            machine.dial(reset=True)
            if not registers['a2']:machine.dial(reset=False)
    return panel_rgb(machine.panel)


def run_theme(vm,args,theme,symbols,loop_end,state_addresses,fixture,metric_layout):
    """Own one VM; trigger decode by HTTP and observe full foreground clock frames."""
    import compare
    from small_tv_http_test import http,wait_http,clean_uart
    folder=args.output/theme;folder.mkdir()
    previous_seed=vm.seed_clock_network
    previous_theme,previous_mask=compare.CURRENT_THEME,compare.CURRENT_PHOTO_MASK
    compare.CURRENT_THEME=theme;compare.CURRENT_PHOTO_MASK=0
    vm.seed_clock_network=compare.seed_settings
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
        persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=fixture.port)
    result=dict(passed=False,theme=theme,control=args.control,frames=[],observations=[],owners_stopped=False,
        checks={},reference='clean native RV32 and corrected literal factory RV32; no pixel masks',
        fixture=args.fixture,resources={})
    observer=session=kernel=handle=None;pending=None;executor=ThreadPoolExecutor(max_workers=1)
    before=None;deadline=time.monotonic()+900
    try:
        session,prepared=vm.launch(options,folder);kernel,handle=process_handle(session['pid'])
        before=(folder/'flash.bin').read_bytes();(folder/'before.bin').write_bytes(before)
        result['prepared_sha256']=prepared['prepared_flash_sha256']
        observer=Observer(port);observer.socket.settimeout(120)
        entry=symbols['factory_draw_'+theme]
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            assert direct_flash_backing(qmp,folder)
            qmp.execute('qom-set',path='/machine/wifi',property='ntp-unix-seconds',
                value=int(dt.datetime(2026,10,13,12,34,55,tzinfo=dt.timezone.utc).timestamp()))
        observer.resume();url=session['web_urls']['station'];wait_http(url,'/getclocktype')
        observer.interrupt();observer.breakpoint(entry)
        observer.continue_to(entry);observer.breakpoint(entry,False)
        # Complete ordinary startup rendering before starting the upload. Every
        # later reference starts clean; no actual target panel is copied into it.
        observer.breakpoint(loop_end);observer.continue_to(loop_end);observer.breakpoint(loop_end,False)
        observer.resume()
        image=ROOT/'Small_TV/src/tests/fixtures/jpeg_extended'/args.fixture
        data=image.read_bytes();chunks=(len(data)+4095)//4096
        assert http(url,'/start_upload',{'file_number':5,'file_size':len(data),'total_chunks':chunks},origin=url,timeout=30)==(200,b'OK')
        for index in range(chunks):assert multipart(url,5,index,chunks,data[index*4096:(index+1)*4096])==(200,b'OK')
        observer.interrupt()
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            result['work_started_guest']=weather.virtual_seconds(qmp)
        decode_return=None
        if not args.control:
            decoder=symbols['jpeg_decoder_decode'];observer.breakpoint(decoder)
            pending=executor.submit(http,url,'/finish_upload',{'file_number':5,'file_name':'file5.jpg'},900,url)
            observer.continue_to(decoder);observer.breakpoint(decoder,False)
            decode_return=observer.register(1);observer.breakpoint(decode_return)
            assert observer.memory(state_addresses['decoding'],1)==b'\1'
            assert observer.memory(state_addresses['background'],1)==b'\0'
            assert int.from_bytes(observer.memory(state_addresses['slot'],4),'little')==4
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                result['decoder_entry_guest']=weather.virtual_seconds(qmp)
                result['resources']['entry']=metrics.snapshot(qmp,folder,'decode-entry',metric_layout)
            worker=result['resources']['entry']['worker']['tcb_address']
            diagnostic=observer.register(12)
            result['decoder_entry']=decoder;result['decoder_return']=decode_return
        dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
        assets=json.loads((ROOT/'Small_TV/assets/manifest.json').read_text())
        if theme=='classic':
            native=SceneMachine('native',dump,assets,dependency_root=args.dependency_root,omit_photo_owner=True)
            factory=SceneMachine('factory-weather-corrected',dump,assets,dependency_root=args.dependency_root)
        else:
            native=Machine('native',dependency_root=args.dependency_root)
            factory=Machine('factory-corrected' if theme=='dial' else 'factory',dependency_root=args.dependency_root)
        ended=False
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            while not ended:
                assert time.monotonic()<deadline,'Clock/decode observation exceeded its host bound'
                observer.breakpoint(entry)
                pc=stop_at(observer,{entry,decode_return} if decode_return else {entry})
                if pc==decode_return:
                    observer.breakpoint(decode_return,False)
                    result['decoder_status']=observer.register(10)
                    result['decoder_exit_guest']=weather.virtual_seconds(qmp)
                    result['resources']['exit']=metrics.snapshot(qmp,folder,'decode-exit',metric_layout,worker,diagnostic)
                    ended=True;break
                code=observer.memory(entry,4)
                registers={name:observer.register(number) for name,number in
                    [('a0',10),('a1',11),('a2',12),('a3',13),('a4',14),('a5',15),('a6',16)]}
                clock=scene.inputs(observer,'reconstructed',theme,registers)
                active=observer.memory(state_addresses['decoding'],1)==b'\1'
                background=observer.memory(state_addresses['background'],1)!=b'\0'
                source_slot=int.from_bytes(observer.memory(state_addresses['slot'],4),'little')
                observer.breakpoint(entry,False);observer.breakpoint(loop_end)
                at=stop_at(observer,{loop_end,decode_return} if decode_return else {loop_end})
                if at==decode_return:
                    observer.breakpoint(decode_return,False);result['decoder_status']=observer.register(10)
                    result['decoder_exit_guest']=weather.virtual_seconds(qmp);ended=True
                    result['resources']['exit']=metrics.snapshot(qmp,folder,'decode-exit',metric_layout,worker,diagnostic)
                    observer.continue_to(loop_end)
                observer.breakpoint(loop_end,False)
                assert observer.memory(entry,4)==code
                active_end=observer.memory(state_addresses['decoding'],1)==b'\1' and not ended
                guest=weather.virtual_seconds(qmp)
                result['observations'].append(dict(guest_seconds=guest,active=active,active_end=active_end,
                    background=background,clock=asdict(clock)))
                useful=theme!='simple' or registers['a3'] or registers['a4']
                if useful and (args.control or active and active_end):
                    index=len(result['frames']);actual=scene.picture(qmp,folder,str(index)+'-complete')
                    expected=clean_frame(native,theme,clock,registers)
                    original=clean_frame(factory,theme,clock,registers)
                    different=sum(actual[i:i+3]!=expected[i:i+3] for i in range(0,len(actual),3))
                    factory_different=sum(actual[i:i+3]!=original[i:i+3] for i in range(0,len(actual),3))
                    light=scene.backlight(observer)
                    row=dict(guest_seconds=guest,clock=asdict(clock),registers=registers,
                        active=active,active_end=active_end,background=background,source_slot=source_slot,
                        different_pixels=different,factory_different_pixels=factory_different,compared_pixels=57600,
                        actual_sha256=vm.digest(actual),native_sha256=vm.digest(expected),factory_sha256=vm.digest(original),
                        code_unchanged=True,backlight=light,passed=not different and not factory_different and light['brightness']==1000)
                    result['frames'].append(row)
                    print('Clock decode:',theme,'frame',index,'second',clock.second,'active',active,
                          'differences',different,factory_different,flush=True)
                    if not row['passed']:
                        write_rgb_png(folder/(str(index)+'-native.png'),expected)
                        write_rgb_png(folder/(str(index)+'-factory.png'),original)
                        raise AssertionError('Complete clock frame differs during foreground decode')
                if args.control and guest-result['work_started_guest']>=15:ended=True
                assert len(result['frames'])<150
        for address in list(observer.breakpoints):observer.breakpoint(address,False)
        observer.resume()
        if pending:
            status,body=pending.result(timeout=90);result['finish_status']=status;result['finish_body']=body.decode()
            assert status==200 and body==b'OK' and result['decoder_status']==0,(status,body,result)
        frames=result['frames'];assert len(frames)>=3
        times=[dt.datetime(c['clock']['year'],c['clock']['month'],c['clock']['day'],c['clock']['hour'],
            c['clock']['minute'],c['clock']['second']) for c in frames]
        assert len(set(times))>=3 and len({(t.hour,t.minute) for t in times})>=2,'No real minute rollover observed'
        assert all(t.date()==dt.date(2026,10,13) and t.hour==20 for t in times)
        assert all(a<=b for a,b in zip(times,times[1:]))
        gaps=[b['guest_seconds']-a['guest_seconds'] for a,b in zip(frames,frames[1:])]
        assert max(gaps)<=2.5,'Clock frame gap exceeds its guest-time budget'
        if not args.control:
            assert frames[0]['guest_seconds']-result['decoder_entry_guest']<=2.5
            assert result['decoder_exit_guest']-frames[-1]['guest_seconds']<=2.5
        result['max_frame_gap_guest_seconds']=max(gaps)
        result['checks'].update(all_pixels_checked=True,real_minute_rollover=True,actual_decode_overlap=not args.control,
            hardware_breakpoints_only=True,no_guest_state_writes=True)
        assert clean_uart(folder);result['passed']=True
    except Exception as error:
        result['error']=type(error).__name__+': '+str(error);raise
    finally:
        if observer:observer.close()
        if session:
            for name in ('uart.log','qemu.log','session.json'):
                if (folder/name).exists():(folder/('retained-'+name)).write_bytes((folder/name).read_bytes())
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(folder,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            result['owners_stopped']=True
            if before is not None:
                after=(folder/'flash.bin').read_bytes()
                plan=json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/jpeg-cache-plan.json').read_text())
                mutable=sorted([(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]+
                    [(r['offset'],r['offset']+r['bytes']) for r in plan['candidate_extents']])
                cursor=0
                for start,end in mutable:
                    assert before[cursor:start]==after[cursor:start];cursor=end
                assert before[cursor:]==after[cursor:]
                result['checks']['protected_flash_exact']=True
        executor.shutdown(wait=True,cancel_futures=True)
        vm.seed_clock_network=previous_seed;compare.CURRENT_THEME,compare.CURRENT_PHOTO_MASK=previous_theme,previous_mask
        vm.save_json(folder/'clock-report.json',result)
    return result


def main():
    """Separate LCD gate: service HTTP is a trigger, not a network latency criterion."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--themes',nargs='+',choices=('classic','simple','dial'),default=['classic','simple','dial'])
    parser.add_argument('--control',action='store_true')
    parser.add_argument('--fixture',choices=('flat-gray-progressive-8.jpg','rich-progressive420-8.jpg','full-cmyk12.jpg'),
        default='flat-gray-progressive-8.jpg',help='Exact prequalified input; all clock criteria remain unchanged')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));sys.path.insert(0,str(ROOT/'Small_TV/qemu/parity'))
    import small_tv_vm as vm
    weather.vm=vm;scene.vm=vm
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert vm.digest((args.qemu_root/row['file']).read_bytes())==row['sha256']
    symbols,loop_end=native_entries();elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    layout=describe(elf);codec=layout['globals']['codec']
    metric_layout=metrics.describe(elf,layout,args.dependency_root)
    (args.output/'resource-layout.json').write_text(json.dumps(metric_layout,indent=2)+'\n',encoding='utf-8',newline='\n')
    addresses={name:codec['address']+codec['fields'][name]['offset'] for name in ('decoding','background')}
    addresses['slot']=codec['address']+codec['fields']['cache']['offset']+codec['fields']['cache']['fields']['slot']['offset']
    fixture=weather.WeatherFixture();payload=weather.payload();payload['weather'][0].update(main='Clear',description='clear',icon='01d')
    payload['wind']['deg']=90;fixture.set_response(200,data=payload)
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed';manifest=json.loads((archive/'manifest.json').read_text())
    files=[Path(__file__),*[ROOT/'Small_TV/src/tests'/name for name in ('photo_target_state.py','photo_owner_qemu.py',
        'photo_cache_frames_qemu.py','photo_cache_frame_contract.py','scene_qemu.py','gdb_observer.py','machine_oracle.py',
        'classic_oracle.py','weather_render_oracle.py','frame_replay.py','control_oracle.py','jpeg_oracle.py','weather_qemu.py','qemu_storage.py','jpeg_clock_contract.py','photo_runtime_metrics.py')],
        ROOT/'Small_TV/qemu/parity/compare.py',elf,ROOT/'Small_TV/src/tests/fixtures/jpeg_extended'/args.fixture,
        *[archive/name for name in ('app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json','jpeg-cache-plan.json')]]
    inputs={str(p.resolve()):vm.digest(p.read_bytes()) for p in files}
    inputs.update(metric_layout['sdk_sources'])
    report=dict(passed=False,control=args.control,all_functionality_verified=False,network_acceptance=False,
        rf_tested=False,hardware_tested=False,app_sha256=verify_inputs(ROOT,args.dependency_root),
        elf_sha256=manifest['elf_sha256'],source_sha256=manifest['source_sha256'],
        qemu_sha256=vm.digest((args.qemu_root/'bin/qemu-system-riscv32.exe').read_bytes()),inputs_sha256=inputs,
        state_addresses=addresses,fixture=args.fixture,fixture_sha256=vm.digest((ROOT/'Small_TV/src/tests/fixtures/jpeg_extended'/args.fixture).read_bytes()),
        resource_layout_sha256=vm.digest((args.output/'resource-layout.json').read_bytes()),
        complete_theme_matrix=set(args.themes)=={'classic','simple','dial'},themes={})
    try:
        for theme in args.themes:report['themes'][theme]=run_theme(vm,args,theme,symbols,loop_end,addresses,fixture,metric_layout)
        report['passed']=True
    except Exception as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:
        report['synthetic_weather_requests']=fixture.rows();fixture.close()
        report['inputs_unchanged']=all(vm.digest(Path(p).read_bytes())==digest for p,digest in inputs.items())
        report['passed'] &= report['inputs_unchanged']
        if report['passed'] and report['complete_theme_matrix']:
            try:validate(report);report['contract_rejections']=rejection_checks(report)
            except ValueError as error:report['passed']=False;report['error']=str(error)
        vm.save_json(args.output/'report.json',report)
    if not report['passed']:raise AssertionError(report.get('error','Clock gate failed'))


if __name__=='__main__':main()
