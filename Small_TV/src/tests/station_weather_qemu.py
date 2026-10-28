"""Observe native weather HTTP across real STA disconnection and DHCP recovery."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ROOT
from network_clients_qemu import Events,sha,symbols
from photo_owner_qemu import process_handle
from photo_write_budget_qemu import stop_at
from station_event_layout import describe
import weather_qemu as weather


class StationEvents(Events):
    """Observe actual station callbacks and restore only the external virtual AP."""
    def __init__(self,observer,entries,base,wire,layout,vm,session):
        super().__init__(observer,entries,base,wire,False)
        self.layout,self.vm,self.session=layout,vm,session
        self.restore=False;self.restorations=[]

    def state(self):
        """Read exact-ELF native atomic flags/counters without invoking guest code."""
        result={name:int.from_bytes(self.observer.memory(row['address'],row['bytes']),'little')
            for name,row in self.layout['objects'].items() if name not in ('IP_EVENT','WIFI_EVENT')}
        assert result['connected'] in (0,1) and result['ap_active'] in (0,1)
        return result

    def visit(self,pc,depth=0):
        """Keep SDK-owned IP data until its handler returns, then read actual state."""
        index=len(self.rows);captured={}
        if pc==self.entries['wifi_event']:
            base,event,data=(self.observer.register(i) for i in (11,12,13))
            ip_object=self.layout['objects']['IP_EVENT']['address']
            ip_base=int.from_bytes(self.observer.memory(ip_object,4),'little')
            wifi_base=int.from_bytes(self.observer.memory(self.base_object,4),'little')
            constants=self.layout['constants']
            if base==ip_base and event==constants['IP_EVENT_STA_GOT_IP']:
                raw=self.observer.memory(data,self.layout['got_ip']['bytes'])
                offset=self.layout['ip_offset']
                captured=dict(station_kind='got_ip',payload_hex=raw.hex(),ipv4=socket.inet_ntoa(raw[offset:offset+4]))
            elif base==wifi_base and event==constants['WIFI_EVENT_STA_DISCONNECTED']:
                captured=dict(station_kind='disconnected')
                if self.restore:
                    with self.vm.QMP(self.session['qmp_port'],self.session['name']) as qmp:
                        was=qmp.execute('qom-get',path='/machine/wifi',property='station-ap-online')
                        assert was is False
                        qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=True)
                        assert qmp.execute('qom-get',path='/machine/wifi',property='station-ap-online') is True
                    self.restorations.append(dict(event_index=index,external_before=was,external_after=True))
                    self.restore=False
        super().visit(pc,depth)
        self.rows[index].update(captured,station_after=self.state(),return_event_index=len(self.rows))

    def until_connected(self,leases):
        """Require SDK GOT_IP plus its native connected flag, not only model presence."""
        for address in self.entries.values():self.observer.breakpoint(address)
        for _ in range(128):
            good=sum(row.get('station_kind')=='got_ip' for row in self.rows)>=leases
            if good and self.state()['connected'] and len(self.handles)==1:break
            self.visit(stop_at(self.observer,set(self.observer.breakpoints)))
        else:raise AssertionError('Station did not regain a real IP lease')
        for address in list(self.observer.breakpoints):self.observer.breakpoint(address,False)


def cache(observer,vm,session,layout):
    """Read a paused worker flag and raw cache; decode only quiescent publications."""
    raw=observer.memory(layout['address'],layout['size'])
    state=int.from_bytes(observer.memory(layout['request_state_address'],4),'little')
    row=dict(worker_state=state,raw_hex=raw.hex(),generation=int.from_bytes(
        raw[layout['fields']['generation']:layout['fields']['generation']+4],'little'))
    if state==0:
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            row['weather']=weather.snapshot(qmp,'reconstructed',layout)
    return row


def wait_cache(observer,vm,session,layout,predicate):
    """Let the real worker run; sample consistently after an ordinary debugger pause."""
    deadline=time.monotonic()+120
    while True:
        row=cache(observer,vm,session,layout)
        if predicate(row):return row
        assert time.monotonic()<deadline,row
        observer.resume();time.sleep(.1);observer.interrupt()


def running_http(observer,http,url,path,values=None):
    """Run ordinary loopback HTTP without any guest code or register assignment."""
    observer.resume()
    try:return http(url,path,values,30,url)
    finally:observer.interrupt()


def main():
    """Hold weather responses during station loss, then require a fresh recovery fetch."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--qemu',type=Path,required=True)
    parser.add_argument('--abi',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    weather.vm=vm
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    abi=json.loads(args.abi.read_text());assert abi['passed']
    for name,digest in abi['inputs_sha256'].items():assert sha(Path(name))==digest
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    entries,base=symbols(elf);station=describe(elf);layout=weather.native_layout()
    files=[Path(__file__),args.abi,args.qemu,elf,*[Path(__file__).with_name(name) for name in
        ('station_event_layout.py','weather_qemu.py','network_clients_qemu.py','network_event_abi.py',
         'gdb_observer.py','photo_owner_qemu.py','photo_write_budget_qemu.py','control_oracle.py','photo_target_state.py')]]
    pins={str(p.resolve()):sha(p) for p in files}
    report=dict(passed=False,network_lifecycle_complete=False,all_functionality_verified=False,
        lcd_acceptance=False,rf_acceptance=False,hardware_tested=False,
        scope='Native station weather request during real SDK disconnect/GOT_IP, retained cache and fresh HTTP recovery; no LCD/RF acceptance.',
        app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=sha(elf),qemu_sha256=sha(args.qemu),
        inputs_sha256=pins,station_layout=station,weather_layout=layout,entries=entries,event_base_object=base,
        cases=[],events=[],owners_stopped=False)
    fixture=weather.WeatherFixture();fixture.set_response(200)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu.resolve()),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
        persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=fixture.port)
    session=observer=kernel=handle=trace=None
    try:
        session,prepared=vm.launch(options,args.output/'vm');kernel,handle=process_handle(session['pid'])
        report.update(pid=session['pid'],name=session['name'],prepared=prepared)
        observer=Observer(port);trace=StationEvents(observer,entries,base,abi['wire'],station,vm,session)
        trace.until_connected(1);url=session['web_urls']['station']
        observer.resume();wait_http(url,'/getclocktype');observer.interrupt()
        report['initial']=wait_cache(observer,vm,session,layout,lambda r:r['worker_state']==0 and
            r['weather']['valid'] and r['weather']['humidity']==67)
        for case,status in enumerate((200,503)):
            before=cache(observer,vm,session,layout);assert before['worker_state']==0
            fixture.set_response(status,negative=True);fixture.hold_response()
            held_started=time.monotonic()
            refresh=running_http(observer,http,url,'/updateCity',dict(city='Shenzhen,CN'))
            assert refresh==(200,b'OK')
            observer.resume()
            try:assert fixture.response_held.wait(20),'Weather request did not reach held fixture'
            finally:observer.interrupt()
            held=cache(observer,vm,session,layout);assert held['worker_state'] & 1
            row=dict(status=status,before=before,held=held,events_begin=len(trace.rows),requests_before=len(fixture.rows()),
                refresh_http=dict(status=refresh[0],body_hex=refresh[1].hex()))
            report['cases'].append(row)
            leases=sum(e.get('station_kind')=='got_ip' for e in trace.rows)
            trace.restore=True
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=False)
            trace.until_connected(leases+1)
            row.update(events_end=len(trace.rows),reconnected=trace.state())
            row['before_release']=cache(observer,vm,session,layout)
            row['held_host_seconds']=time.monotonic()-held_started
            assert row['held_host_seconds']<30 and not fixture.response_release.is_set()
            fixture.release_response()
            row['settled']=wait_cache(observer,vm,session,layout,lambda r:r['worker_state']==0)
            assert row['settled']['weather']['valid']
            if status==503:assert row['settled']['raw_hex']==before['raw_hex']
            else:assert row['settled']['weather']['humidity'] in (before['weather']['humidity'],41)
            fresh=weather.payload();fresh['main']['humidity']=78+case
            fixture.set_response(200,data=fresh);row['recovery_body']=fresh
            recovery=running_http(observer,http,url,'/updateCity',dict(city='Shenzhen,CN'))
            row['recovery_http']=dict(status=recovery[0],body_hex=recovery[1].hex())
            assert recovery==(200,b'OK')
            row['recovered']=wait_cache(observer,vm,session,layout,lambda r:r['worker_state']==0 and
                r['weather']['valid'] and r['weather']['humidity']==78+case)
            assert row['recovered']['generation']>row['settled']['generation']
            current_theme=running_http(observer,http,url,'/getclocktype')
            row['theme_http']=dict(status=current_theme[0],body_hex=current_theme[1].hex())
            assert current_theme==(200,b'0')
            vm.save_json(args.output/'report.json',report)
            print('STA weather',status,'recovered humidity',row['recovered']['weather']['humidity'],flush=True)
        assert len(trace.handles)==1 and not any(e['function']=='httpd_stop' for e in trace.rows)
        assert clean_uart(args.output/'vm')
        report['rom_boots']=(args.output/'vm/uart.log').read_bytes().count(b'ESP-ROM:esp32c2')
        assert report['rom_boots']==1
        assert all(sha(Path(name))==digest for name,digest in pins.items())
        report['passed']=True
    except BaseException as error:
        report['error']=type(error).__name__+': '+str(error);raise
    finally:
        fixture.release_response()
        if trace:report['events']=trace.rows;report['server_handles']=trace.handles;report['restorations']=trace.restorations
        if observer:observer.close()
        if session:
            vm.control(args.output/'vm','stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            report['owners_stopped']=True
        report['requests']=fixture.rows();fixture.close()
        vm.save_json(args.output/'report.json',report)
    print('PASS station weather disconnect/recovery',flush=True)


if __name__=='__main__':main()
