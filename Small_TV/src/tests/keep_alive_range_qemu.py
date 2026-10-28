"""Observe an actual long SDK timer and natural cancellation in an owned VM.

This fixture writes exactly one synthetic peer-period halfword in disposable
guest RAM after PM initialization, before the connection producer reads it. It never changes registers,
instructions, source images or a physical device. The normal observer stays
read-only; the one bounded fixture write is explicit and separately recorded.
"""
import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.pm_runtime_layout import native_types
from verify_wifi_keep_alive import verify,complete
from gdb_observer import Observer


def ram(pointer,length):
    """Accept only aligned, bounded C2 data RAM objects, never a host address."""
    return pointer%4==0 and 0x3fca0000<=pointer<pointer+length<=0x3fce0000


def wait(predicate,message,seconds=30):
    """Wait only for a specific guest condition with a host-time stall bound."""
    end=time.monotonic()+seconds
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.1)
    raise TimeoutError(message)


def main():
    """Use a fresh network-only VM, real kernel process handle and exact build pins."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('helpers','qemu','rom','build','sdk','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[3]
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.helpers))
    import small_tv_vm as vm
    from small_tv_http_test import wait_http,clean_uart
    from runtime_supervisor_fixture import process_creation
    from weather_qemu import WeatherFixture
    import weather_qemu as weather
    weather.vm=vm
    archive=root/'firmware/development/small-tv-esp32c2-reconstructed'
    elf=(args.build/'small_tv_reconstructed.elf').read_bytes();app=(archive/'app.bin').read_bytes()
    libraries=args.sdk/'components/esp_wifi/lib/esp32c2'
    own=args.build/'esp-idf/app/CMakeFiles/__idf_app.dir/network/wifi_keep_alive.c.obj'
    timer=args.build/'esp-idf/esp_timer/CMakeFiles/__idf_esp_timer.dir/src/ets_timer_legacy.c.obj'
    source=args.sdk/'components/esp_timer/src/ets_timer_legacy.c'
    qualified=verify(elf,app,libraries,own.read_bytes(),timer.read_bytes(),source.read_bytes())
    linked=LinkedRuntime(elf,app);abi=native_types(linked.elf)
    parts=dict(members((libraries/'libnet80211.a').read_bytes()))
    leave=complete(linked,parts['wl_cnx.o'],'cnx_sta_leave',{})
    getter=complete(linked,parts['ieee80211_sta.o'],'sta_is_bss_max_idle_enabled',{})
    menuconfig=linked.symbol('g_wifi_menuconfig')['st_value']
    # pm_start can initialize peer state. Inject after its natural return,
    # immediately before the completely matched producer reads peer->period.
    entry=linked.symbol('cnx_sta_pm.part.0')['st_value']+38
    assert linked.read(entry,4,True)==bytes.fromhex('03552433')
    api=linked.symbol('esp_timer_start_once')['st_value']
    disable=int(qualified['disable']['start'],0)
    pm,cfg,gic=(qualified['g_pm'],qualified['g_pm_cfg'],linked.symbol('g_ic')['st_value'])
    profile=json.loads((root/'Small_TV/qemu/profiles/small-tv-c2.json').read_bytes())
    profile['devices']=[];profile['name']='small-tv-bss-timer-range-network-only'
    target=out/'network-profile.json';target.write_text(json.dumps(profile,indent=2)+'\n',encoding='utf-8')
    files=[Path(__file__),Path(__file__).with_name('gdb_observer.py'),Path(__file__).with_name('runtime_supervisor_fixture.py'),
        Path(__file__).with_name('weather_qemu.py'),args.qemu,args.rom,args.build/'small_tv_reconstructed.elf',own,timer,source,
        root/'Small_TV/qemu/profiles/small-tv-c2.json',target,*list(args.helpers.glob('*.py')),
        *list(archive.glob('*.json')),*list(archive.glob('*.bin')),*sorted(libraries.glob('*.a'))]
    pins={str(p.resolve()):sha(p.read_bytes()) for p in files}
    fixture=WeatherFixture(['Shenzhen,CN'])
    with socket.socket() as reserve:reserve.bind(('127.0.0.1',0));gdb_port=reserve.getsockname()[1]
    options=SimpleNamespace(yoradio=str(root),firmware='reconstructed',qemu=str(args.qemu),rom_elf=str(args.rom),
        hardware_profile=str(target),network='clock',display='none',persistent=False,paused=True,gdb_port=gdb_port,
        http_base_port=0,service_port=fixture.port,app_elf=str(args.build/'small_tv_reconstructed.elf'))
    result=dict(passed=False,inputs_sha256=pins,qualification=qualified,native_dwarf=abi,
        leave=leave,getter=getter,observations=[],fixture_writes=[],display_tested=False,
        physical_hardware_tested=False,whole_image_completeness_proved=False)
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD)
    kernel.GetExitCodeProcess.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD));kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
    session=observer=handle=None;folder=out/'vm';paused=True
    def stopped_at(address):
        """Require an actual hardware-breakpoint stop at the requested unchanged PC."""
        nonlocal paused
        with observer.time_limit(30):reply=observer.receive();pc=observer.register(32)
        assert reply.startswith(('T05','S05')) and pc==address,(reply,hex(pc),hex(address))
        paused=True
    def snapshot(phase):
        """Read only typed timer/config metadata; never task stacks or packet payloads."""
        assert paused
        reads=[]
        def take(address,size):
            assert size in (1,2,4,8) and len(reads)<16
            raw=observer.memory(address,size);reads.append(dict(address=address,size=size,hex=raw.hex()))
            return int.from_bytes(raw,'little')
        with observer.time_limit(3):
            marker=take(pm+496,4);backend=take(pm+508,4)
            assert marker==0x12121212 and ram(backend,32)
            row=dict(phase=phase,pc=observer.register(32),marker=marker,handle=backend,
                alarm=take(backend,8),pm_active=take(pm+14,1),bss_enabled=take(cfg+52,1),
                period=take(cfg+72,2),adjustment=take(cfg+56,4),menuconfig_word=take(menuconfig+64,4))
        row['raw_reads']=reads;result['observations'].append(row)
        print(json.dumps({k:v for k,v in row.items() if k!='raw_reads'}),flush=True)
        return row
    try:
        session,prepared=vm.launch(options,folder);result.update(session=session,prepared=prepared)
        handle=kernel.OpenProcess(0x100000|0x1000,False,session['pid'])
        if not handle:raise ctypes.WinError(ctypes.get_last_error())
        result['owner']=dict(pid=session['pid'],name=session['name'],creation=process_creation(handle))
        print(json.dumps(dict(launched=result['owner'])),flush=True)
        observer=Observer(gdb_port);observer.socket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        observer.breakpoint(entry);observer.resume();paused=False;stopped_at(entry)
        with observer.time_limit(3):
            peer=observer.register(8);station=int.from_bytes(observer.memory(gic+16,4),'little')
            assert ram(peer,824) and ram(station,232)
            assert int.from_bytes(observer.memory(station+228,4),'little')==peer
            original=observer.memory(peer+818,2)
            # This is the fixture's only writing operation. The ordinary Observer
            # request API is unchanged and continues to reject all write commands.
            command=f'M{peer+818:x},2:ffff'.encode('ascii')
            observer._send(b'$'+command+b'#'+f'{sum(command)%256:02x}'.encode('ascii'))
            assert observer.receive()=='OK' and observer.memory(peer+818,2)==b'\xff\xff'
            result['fixture_writes'].append(dict(address=peer+818,size=2,before_hex=original.hex(),after_hex='ffff'))
        observer.breakpoint(entry,False);observer.breakpoint(api);observer.resume();paused=False
        expected_delay=65535*1024000-2000000
        result['timer_api_calls']=[]
        for _ in range(64):
            stopped_at(api)
            with observer.time_limit(3):
                backend=int.from_bytes(observer.memory(pm+508,4),'little')
                passed=observer.register(10);delay=observer.register(11)|(observer.register(12)<<32)
                result['timer_api_calls'].append(dict(handle=passed,expected_handle=backend,delay_us=delay,
                    config_hex=observer.memory(cfg+52,24).hex(),return_pc=observer.register(1)))
            if passed==backend and delay==expected_delay:break
            observer.resume();paused=False
        else:raise AssertionError('No full-range timer API call observed')
        result['api_delay_us']=delay;result['api_handle']=passed
        return_pc=observer.register(1)
        ms=next(row for row in qualified['backends'] if row['name']=='ets_timer_arm')
        assert int(ms['start'],0)<=return_pc<int(ms['end'],0)
        observer.breakpoint(api,False);observer.breakpoint(return_pc);observer.resume();paused=False
        stopped_at(return_pc);assert observer.register(10)==0
        armed=snapshot('long-arm-return')
        assert armed['alarm']>expected_delay>0xffffffff and armed['period']==65535 and armed['bss_enabled']==1
        result['observed_feature_enabled']=bool(armed['menuconfig_word']&(1<<8))
        observer.breakpoint(return_pc,False);observer.resume();paused=False
        wait_http(session['web_urls']['station'],'/getclocktype',seconds=30)
        observer.interrupt();paused=True;snapshot('connected-long-timer')
        observer.breakpoint(disable);observer.resume();paused=False
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            assert all(row['name']!='lcd' for row in qmp.execute('qom-list',path='/machine/peripheral'))
            qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=False)
        stopped_at(disable);before=snapshot('cancel-entry')
        assert before['alarm']>0xffffffff
        return_pc=observer.register(1)
        assert int(leave['start'],0)<=return_pc<int(leave['end'],0)
        observer.breakpoint(disable,False);observer.breakpoint(return_pc);observer.resume();paused=False
        stopped_at(return_pc);after=snapshot('cancel-return');assert after['alarm']==0
        observer.breakpoint(return_pc,False);observer.resume();paused=False
        result['long_timer_cancelled_by_station_leave']=True
        result['passed']=True
    except Exception as error:
        result['error']=repr(error);raise
    finally:
        if observer:observer.close()
        if session:
            try:
                vm.control(folder,'stop')
                assert handle and kernel.WaitForSingleObject(handle,10000)==0
                code=wintypes.DWORD();assert kernel.GetExitCodeProcess(handle,ctypes.byref(code))
                result['exit_code']=code.value;assert code.value==0
                vm.ensure_stopped(folder);result['owned_stop_completed']=True
            except Exception as error:result['cleanup_error']=repr(error);result['passed']=False
            result['uart_clean']=clean_uart(folder);result['passed'] &= result['uart_clean']
        if handle:kernel.CloseHandle(handle)
        fixture.close();result['inputs_unchanged']=all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
        result['passed'] &= result['inputs_unchanged']
        vm.save_json(out/'report.json',result)
    print(json.dumps(dict(passed=result['passed'],api_delay_us=result['api_delay_us'],cancelled=True)))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
