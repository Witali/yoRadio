"""Observe the real PM stop exit and timer metadata during an owned station outage."""
import argparse
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

from pm_runtime_test import run as qualify,SOURCES
from pm_runtime_metadata import decode
from audit_factory_xrefs import sha
from gdb_observer import Observer


def wait(predicate,message,seconds=20):
    """Wait for a concrete guest event, bounded by host time as a stall guard."""
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        if predicate():return
        time.sleep(.1)
    raise TimeoutError(message)


def main():
    """Use new disposable firmware copies; do not touch existing long-run VM owners."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','old-pp','new-pp','rom','yoradio','tools','qemu','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--variants',nargs='+',choices=('factory','native'),default=['factory','native'])
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path[:0]=[str(args.tools),str(args.yoradio/'Small_TV/qemu/parity')]
    import small_tv_vm as vm
    from small_tv_http_test import wait_http,http,clean_uart
    from weather_qemu import read_bytes
    import weather_qemu as weather
    import compare
    units=qualify(args.factory.read_bytes(),args.native.read_bytes(),args.old_pp,args.new_pp,args.rom.read_bytes())
    layout=units['layout'];source=Path(__file__).resolve().parents[1]
    archive=args.yoradio/'firmware/development/small-tv-esp32c2-reconstructed'
    files=[args.factory,args.native,args.old_pp,args.new_pp,args.rom,args.qemu,Path(__file__),
        source/'tests/gdb_observer.py',source/'tests/weather_qemu.py',
        args.yoradio/'Small_TV/qemu/profiles/small-tv-c2.json',args.yoradio/'Small_TV/full-flash.bin',
        args.yoradio/'Small_TV/manifest.json',args.yoradio/'Small_TV/qemu/parity/compare.py']
    files += [source/name for name in SOURCES]+list(args.tools.glob('*.py'))
    files += list(archive.glob('*.json'))+list(archive.glob('*.bin'))
    pins={str(p.resolve()):sha(p.read_bytes()) for p in files}
    assert (archive/'app.bin').read_bytes()[176:208].hex()==layout['native_elf_sha256']
    previous_seed=vm.seed_clock_network;vm.seed_clock_network=compare.seed_settings;compare.CURRENT_THEME='simple'
    weather.vm=vm;fixture=weather.WeatherFixture(['Shenzhen,CN']);fixture.set_response(200)
    result=dict(passed=False,qualification=units,inputs_sha256=pins,flows={},
                full_runtime_lifecycle_proved=False,physical_hardware_tested=False,whole_image_completeness_proved=False)
    try:
        for variant in args.variants:
            firmware='original' if variant=='factory' else 'reconstructed'
            l=layout['layouts'][variant];folder=args.output/variant
            flow=dict(passed=False,observations=[],http_statuses=[]);result['flows'][variant]=flow
            session=observer=qmp=None;paused=True;offline=False
            with socket.socket() as reserve:reserve.bind(('127.0.0.1',0));gdb_port=reserve.getsockname()[1]
            options=SimpleNamespace(yoradio=str(args.yoradio),qemu=str(args.qemu),rom_elf=str(args.rom),
                hardware_profile=str(args.yoradio/'Small_TV/qemu/profiles/small-tv-c2.json'),firmware=firmware,
                network='clock',display='none',persistent=False,paused=True,gdb_port=gdb_port,service_port=fixture.port)
            def snapshot(phase):
                """Retain only the decoder's bounded numeric reads while this CPU is stopped."""
                assert paused
                raw=[]
                def capture(address,size):
                    """No general memory export: decoder chooses all reads and pointer guards."""
                    data=observer.memory(address,size);raw.append(dict(address=address,size=size,hex=data.hex()));return data
                with observer.time_limit(3):
                    pc=observer.register(32);metadata=decode(capture,l)
                row=dict(phase=phase,pc=pc,metadata=metadata,raw_reads=raw)
                flow['observations'].append(row)
                assert metadata['rom_pm_pointer']==l['pm'] and metadata['osi_pointer']==l['osi_table']
                print(json.dumps(dict(variant=variant,phase=phase,pc=hex(pc),metadata=metadata)),flush=True)
                return row
            try:
                session,prepared=vm.launch(options,folder);flow.update(session=session,sources=prepared['sources'])
                print(json.dumps(dict(launched=variant,pid=session['pid'],name=session['name'])),flush=True)
                observer=Observer(gdb_port);observer.socket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
                observer.socket.settimeout(20);observer.resume();paused=False
                with vm.QMP(session['qmp_port'],session['name']) as qmp:
                    wait_http(session['web_urls']['station'],expected=b'/setclocktype')
                    def counter():
                        """Read the existing virtual microsecond counter without modifying time."""
                        return int.from_bytes(read_bytes(qmp,0x6004d000,4),'little')
                    def connected():
                        """Read the actual atomic application connection flag."""
                        return read_bytes(qmp,l['connected'],1)[0]==l['connected_value']
                    for _ in range(3):
                        status,_body=http(session['web_urls']['station'],'/getclocktype',timeout=10)
                        assert status==200;flow['http_statuses'].append(status)
                        first=counter();wait(lambda:((counter()-first)&0xffffffff)>=1000000,'Guest clock stalled during priming')
                    observer.interrupt();paused=True
                    baseline=snapshot('connected')
                    assert baseline['metadata']['application_connected_hint'] and baseline['metadata']['pm_active']
                    observer.breakpoint(l['stop_exit']);observer.resume();paused=False
                    qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=False);offline=True
                    with observer.time_limit(30):reply=observer.receive();pc=observer.register(32)
                    if not reply.startswith(('T05','S05')) or pc!=l['stop_exit']:
                        raise AssertionError('Natural outage did not reach the qualified PM stop exit')
                    paused=True;stop=snapshot('stop-return');flow['stop_exit_observed']=True
                    before,after=baseline['metadata']['timer_armed'],stop['metadata']['timer_armed']
                    flow['timer_was_armed']=before
                    flow['timer_armed_at_stop_exit']=after
                    flow['cancellation_conclusion']=('inactive-before-stop' if before is not True else
                        'disarmed-at-stop-exit' if after is False else 'still-armed-at-stop-exit')
                    observer.breakpoint(l['stop_exit'],False)
                    if variant=='native':observer.breakpoint(l['cancel_entry'])
                    observer.resume();paused=False
                    if variant=='native':
                        # Observe the real tail-call helper and its caller's
                        # continuation, without injecting any timer operation.
                        with observer.time_limit(10):reply=observer.receive();pc=observer.register(32)
                        if not reply.startswith(('T05','S05')) or pc!=l['cancel_entry']:
                            raise AssertionError('Expected natural keep-alive cancellation')
                        paused=True
                        caller=observer.register(1);flow['cancel_caller_return']=caller
                        assert not caller&1 and 0x42000000<=caller<0x42180000
                        snapshot('cancel-entry');observer.breakpoint(l['cancel_entry'],False)
                        observer.breakpoint(caller);observer.resume();paused=False
                        with observer.time_limit(10):reply=observer.receive();pc=observer.register(32)
                        if not reply.startswith(('T05','S05')) or pc!=caller:
                            raise AssertionError('Cancellation did not return to its real caller')
                        paused=True;cancelled=snapshot('cancel-return')
                        assert cancelled['metadata']['timer_armed'] is False
                        observer.breakpoint(caller,False);observer.resume();paused=False
                        wait(lambda:not connected(),'Native application did not clear its connection flag',seconds=5)
                    else:
                        # Factory writes its state only after esp_wifi_connect
                        # returns; a previously connected value is not a live link bit.
                        first=counter();wait(lambda:((counter()-first)&0xffffffff)>=1000000,'Factory outage observation stalled')
                    observer.interrupt();paused=True;disconnected=snapshot('disconnected')
                    assert not disconnected['metadata']['pm_active']
                    assert qmp.execute('qom-get',path='/machine/wifi',property='station-ap-online') is False
                    if variant=='native':assert not disconnected['metadata']['application_connected_hint']
                    observer.resume();paused=False
                    qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=True);offline=False
                    wait_http(session['web_urls']['station'],'/getclocktype',seconds=30)
                    if variant=='native':wait(connected,'Native station did not reconnect after AP recovery')
                    else:wait(lambda:bool(read_bytes(qmp,l['pm']+14,1)[0]),'Factory PM did not restart after AP recovery')
                    observer.interrupt();paused=True;recovery=snapshot('reconnected');observer.resume();paused=False
                    assert not stop['metadata']['pm_active'] and recovery['metadata']['pm_active']
                    flow['passed']=True
            except Exception as error:
                flow['error']=repr(error)
                if observer is not None:
                    try:
                        if not paused:observer.interrupt();paused=True
                        snapshot('failure')
                    except Exception as capture_error:flow['capture_error']=repr(capture_error)
                # Preserve a factory failure and still observe the native image.
                # The final report must fail; one image cannot stand in for both.
            finally:
                # The with-statement has already closed QMP on an exception.
                # Quit the owned VM rather than writing to that closed stream.
                if offline:flow['ap_offline_at_cleanup']=True
                if observer:observer.close()
                if session:
                    try:vm.control(folder,'stop');flow['owned_stop_completed']=True
                    except Exception as error:flow['cleanup_error']=repr(error);flow['passed']=False
                flow['uart_clean']=clean_uart(folder);flow['passed'] &= flow['uart_clean']
                vm.save_json(folder/'pm-runtime-observation.json',flow)
            print(json.dumps(dict(finished=variant,passed=flow['passed'],conclusion=flow.get('cancellation_conclusion'),
                                  error=flow.get('error'))),flush=True)
        result['inputs_unchanged']=all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
        result['passed']=result['inputs_unchanged'] and all(f['passed'] for f in result['flows'].values())
    finally:
        result['inputs_unchanged']=all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
        vm.seed_clock_network=previous_seed;fixture.close();vm.save_json(args.output/'report.json',result)
    print(json.dumps(dict(passed=result['passed'],variants=list(result['flows']))))
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
