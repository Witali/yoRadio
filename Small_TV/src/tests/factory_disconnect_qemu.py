"""Observe factory disconnect boundaries without treating an observation timeout as acceptance."""
import argparse
import json
from pathlib import Path
import socket
import sys
import threading
import time
from types import SimpleNamespace

def main():
    """Trace one owned factory VM, pinning sources and keeping unfinished recovery explicit."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','old-pp','new-pp','rom','yoradio','tools','qemu','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    ROOT=Path(__file__).resolve().parents[3];src=ROOT/'Small_TV/src'
    sys.path[:0]=[str(src/'tests'),str(src/'tools')]
    from pm_runtime_test import run,SOURCES
    from pm_runtime_metadata import decode
    from gdb_observer import Observer
    from audit_factory_xrefs import Image,sha
    parent=args.yoradio
    helpers=args.tools
    sys.path[:0]=[str(helpers),str(parent/'Small_TV/qemu/parity')]
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    import compare
    import weather_qemu as weather
    from weather_qemu import read_bytes

    out=args.output;out.mkdir(parents=True,exist_ok=False)
    factory=args.factory
    native=args.native
    old=args.old_pp
    new=args.new_pp
    rom=args.rom
    qemu=args.qemu
    units=run(factory.read_bytes(),native.read_bytes(),old,new,rom.read_bytes());layout=units['layout']['layouts']['factory']
    image=Image(factory.read_bytes());ret=layout['stop_exit']+10
    assert image.read(ret,2,True)==b'\x82\x80'
    entries={ret:'pm-stop-ret',0x4200c602:'application-event',0x4200c656:'connect-return',0x4206c438:'station-leave-tail',0x4206dfb2:'crypto-call',0x4206dfba:'crypto-return',0x4206dfd6:'sdk-callback-call',0x4206dfd8:'sdk-callback-return',0x4206e03e:'disconnect-post-call',0x4206e042:'disconnect-post-return',0x4206e41c:'alternate-disconnect-path'}
    code={hex(address):image.read(address,8,True).hex() for address in entries}
    files=[Path(__file__),factory,native,old,new,rom,qemu,parent/'Small_TV/full-flash.bin',
           parent/'Small_TV/manifest.json',parent/'Small_TV/qemu/parity/compare.py',parent/'Small_TV/qemu/profiles/small-tv-c2.json']
    files += [src/name for name in SOURCES]+[src/'tests/gdb_observer.py',src/'tests/weather_qemu.py']+list(helpers.glob('*.py'))
    pins={str(file.resolve()):sha(file.read_bytes()) for file in files}
    previous=vm.seed_clock_network;vm.seed_clock_network=compare.seed_settings;compare.CURRENT_THEME='simple'
    weather.vm=vm;fixture=weather.WeatherFixture(['Shenzhen,CN']);fixture.set_response(200)
    report=dict(scope=__doc__,passed=False,code=code,events=[],controller={},inputs_sha256=pins,
                full_runtime_lifecycle_proved=False,physical_hardware_tested=False,whole_image_completeness_proved=False)
    session=observer=thread=None;paused=True

    def snapshot():
        """Capture the same bounded numeric metadata and the actual return register."""
        raw=[]
        def memory(address,size):
            data=observer.memory(address,size);raw.append(dict(address=address,size=size,hex=data.hex()));return data
        with observer.time_limit(3):
            result=dict(pc=observer.register(32),ra=observer.register(1),metadata=decode(memory,layout),raw_reads=raw)
        return result

    def controller():
        """One QMP owner restores the external AP after a guest second while RSP traces."""
        state=report['controller']
        try:
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=False)
                first=int.from_bytes(read_bytes(qmp,0x6004d000,4),'little');state['offline_counter']=first
                deadline=time.monotonic()+15
                while time.monotonic()<deadline:
                    now=int.from_bytes(read_bytes(qmp,0x6004d000,4),'little')
                    if (now-first)&0xffffffff>=1000000:break
                    time.sleep(.05)
                else:raise TimeoutError('No guest second elapsed before AP restore')
                qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=True)
                state['online_counter']=now
                state['online']=qmp.execute('qom-get',path='/machine/wifi',property='station-ap-online')
        except Exception as error:state['error']=repr(error)

    try:
        with socket.socket() as port:port.bind(('127.0.0.1',0));gdb=port.getsockname()[1]
        options=SimpleNamespace(yoradio=str(parent),qemu=str(qemu),rom_elf=str(rom),
            hardware_profile=str(parent/'Small_TV/qemu/profiles/small-tv-c2.json'),firmware='original',
            network='clock',display='none',persistent=False,paused=True,gdb_port=gdb,service_port=fixture.port)
        session,prepared=vm.launch(options,out/'vm');report.update(session=session,sources=prepared['sources'])
        print(json.dumps(dict(launched=session['pid'],name=session['name'])),flush=True)
        observer=Observer(gdb);observer.socket.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
        observer.socket.settimeout(20)
        observer.resume();paused=False
        wait_http(session['web_urls']['station'],expected=b'/setclocktype')
        for _ in range(3):assert http(session['web_urls']['station'],'/getclocktype')[0]==200;time.sleep(1)
        observer.interrupt();paused=True;report['baseline']=snapshot()
        for address in entries:observer.breakpoint(address)
        observer.resume();paused=False
        thread=threading.Thread(target=controller);thread.start()
        for _ in range(16):
            try:
                with observer.time_limit(10):reply=observer.receive()
            except TimeoutError:
                report['observation_timeout']=True
                with observer.time_limit(3):observer.interrupt()
                paused=True;report['last']=snapshot();break
            paused=True;row=snapshot();pc=row['pc']
            assert reply.startswith(('T05','S05')) and pc in entries
            row['boundary']=entries[pc]
            if pc==0x4200c602:
                row['event_base']=observer.register(11);row['event_id']=observer.register(12)
            if pc==0x4206dfd6:row['indirect_target']=observer.register(15)
            if pc==0x4206e03e:row['posted_event_id']=observer.register(10);row['posted_event_bytes']=observer.register(12)
            if pc==0x4206e042:row['post_return_value']=observer.register(10)
            if pc in (ret,0x4206c438):
                caller=row['ra'];assert not caller&1 and 0x42000020<=caller<0x420b29d4
                entries[caller]='pm-stop-caller' if pc==ret else 'station-leave-caller';observer.breakpoint(caller)
                report['pm_stop_caller' if pc==ret else 'station_leave_caller']=caller
            report['events'].append(row);print(json.dumps({k:v for k,v in row.items() if k not in ('raw_reads','metadata')}),flush=True)
            observer.breakpoint(pc,False);entries.pop(pc)
            observer.resume();paused=False
        else:report['observation_limit']=True
        thread.join(timeout=16);assert not thread.is_alive()
        report['inputs_unchanged']=all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
    except Exception as error:report['error']=repr(error)
    finally:
        if observer:observer.close()
        if session:
            try:vm.control(out/'vm','stop');report['owned_stop_completed']=True
            except Exception as error:report['cleanup_error']=repr(error)
        if thread:thread.join(timeout=6)
        report['controller_stopped']=not thread or not thread.is_alive()
        fixture.close();vm.seed_clock_network=previous
        report['uart_clean']=clean_uart(out/'vm')
        report['inputs_unchanged']=all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
        vm.save_json(out/'report.json',report)
    print(json.dumps(dict(events=len(report['events']),controller=report['controller'],error=report.get('error'),
                         last=report.get('last',{}).get('pc'),cleanup=report.get('owned_stop_completed'))))
    if (report.get('error') or report.get('cleanup_error') or report['controller'].get('error') or
        not report.get('owned_stop_completed') or not report['controller_stopped'] or
        not report['uart_clean'] or not report['inputs_unchanged']):
        raise SystemExit(1)


if __name__=='__main__':main()
