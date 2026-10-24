"""Observe real AP peer events and HTTP lifetime in an isolated QEMU guest."""
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
from machine_oracle import ELFFile, ROOT
from photo_owner_qemu import process_handle
from photo_write_budget_qemu import stop_at


def sha(file):
    """Pin the actual running executable, guest image and observers independently."""
    return hashlib.sha256(file.read_bytes()).hexdigest()


class Events:
    """Read SDK entry/return boundaries without calling or changing guest code."""
    def __init__(self, observer, entries, base_object, wire, factory):
        self.observer, self.entries, self.base_object = observer, entries, base_object
        self.wire, self.factory, self.rows, self.active, self.handles = wire, factory, [], set(), []

    def visit(self, pc, depth=0):
        """Preserve nested observed calls when a Wi-Fi event preempts HTTP startup."""
        assert depth < 16
        observer=self.observer; name=next(name for name,address in self.entries.items() if address==pc)
        code=observer.memory(pc,2); returned=observer.register(1)
        assert returned not in self.entries.values()
        row=dict(function=name,pc=pc,return_pc=returned,instruction_sha256=hashlib.sha256(code).hexdigest())
        output=None
        if name=='wifi_event':
            base=observer.register(11);event=observer.register(12);data=observer.register(13)
            row.update(base=base,event_id=event,data_address=data)
            if base==int.from_bytes(observer.memory(self.base_object,4),'little') and event in (self.wire['connected_id'],self.wire['disconnected_id']):
                joined=event==self.wire['connected_id'];kind='connected' if joined else 'disconnected'
                size=7 if self.factory else self.wire[kind+'_bytes']
                raw=observer.memory(data,size);offset=0 if self.factory else self.wire[kind+'_mac']
                mac=':'.join(f'{byte:02x}' for byte in raw[offset:offset+6])
                row.update(kind=kind,mac=mac,event_data_hex=raw.hex())
                if joined:
                    assert mac not in self.active,'Duplicate AP connection event';self.active.add(mac)
                else:
                    assert mac in self.active,'Disconnect for an unobserved AP peer';self.active.remove(mac)
                print('Guest AP event:',kind,mac,flush=True)
        elif name=='httpd_start' and not self.factory: output=observer.register(10)
        self.rows.append(row)
        observer.breakpoint(pc,False)
        # Tail calls can share an ancestor's return breakpoint. Its owner
        # removes it; after a nested return, recheck PC before continuing.
        owns_return=returned not in observer.breakpoints
        if owns_return:observer.breakpoint(returned)
        while observer.register(32)!=returned:
            stopped=stop_at(observer,set(observer.breakpoints))
            if stopped!=returned:self.visit(stopped,depth+1)
        row['return_value']=observer.register(10)
        if output is not None:
            assert row['return_value']==0
            handle=int.from_bytes(observer.memory(output,4),'little');assert handle
            self.handles.append(handle);row['server_handle']=handle
        if self.factory and name in ('httpd_start','httpd_stop'):
            tracked=int.from_bytes(observer.memory(0x3fcc3a70,4),'little')
            row['tracked_server_handle']=tracked
            if name=='httpd_start':self.handles.append(tracked)
        assert observer.memory(pc,2)==code
        if owns_return:observer.breakpoint(returned,False)
        observer.breakpoint(pc)

    def until(self, peers, starts):
        """Require actual posted guest events, not QEMU's desired presence mask."""
        for address in self.entries.values():self.observer.breakpoint(address)
        for attempt in range(64):
            if self.active==peers and sum(row['function']=='httpd_start' for row in self.rows)>=starts:break
            self.visit(stop_at(self.observer,set(self.observer.breakpoints)))
        else:raise AssertionError('Expected peer transition was not reached')
        assert self.active==peers
        for address in list(self.observer.breakpoints):self.observer.breakpoint(address,False)


def symbols(path):
    """Reject absent or ambiguous native SDK/function objects in the exact ELF."""
    names={'wifi_event','httpd_start','httpd_stop','WIFI_EVENT'}
    with path.open('rb') as stream:
        table=list(ELFFile(stream).get_section_by_name('.symtab').iter_symbols())
        rows={name:{symbol['st_value'] for symbol in table if symbol.name==name and symbol['st_value']} for name in names}
    assert all(len(values)==1 for values in rows.values()),rows
    result={name:next(iter(values)) for name,values in rows.items()}
    return {name:result[name] for name in ('wifi_event','httpd_start','httpd_stop')},result['WIFI_EVENT']


def main():
    """Exercise two->one->zero->one with genuine SDK events and ordinary HTTP."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True,help='Immutable tools/profile snapshot')
    parser.add_argument('--qemu',type=Path,required=True,help='Separately pinned candidate emulator')
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--abi',type=Path,required=True)
    parser.add_argument('--firmware',choices=('reconstructed','original'),default='reconstructed')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    snapshot=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in snapshot['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    abi=json.loads(args.abi.read_text());assert abi['passed']
    for name,digest in abi['inputs_sha256'].items():assert sha(Path(name))==digest,name
    factory=args.firmware=='original'
    elf=(args.dependency_root/'.build/small-tv-reverse/factory-analysis.elf') if factory else ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    entries,base=(dict(wifi_event=0x4200c6e2,httpd_start=0x4200c5ec,httpd_stop=0x4200c578),0x3c0f1eb8) if factory else symbols(elf)
    files=[Path(__file__),args.abi,elf,args.qemu,*[Path(__file__).with_name(name) for name in
        ('network_event_abi.py','gdb_observer.py','photo_owner_qemu.py','photo_write_budget_qemu.py','control_oracle.py')]]
    pins={str(file.resolve()):sha(file) for file in files}
    report=dict(passed=False,network_lifecycle_complete=False,all_functionality_verified=False,lcd_acceptance=False,
        rf_acceptance=False,physical_hardware_tested=False,firmware=args.firmware,
        native_app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=sha(elf),qemu_sha256=sha(args.qemu),
        inputs_sha256=pins,tools_snapshot=snapshot,entries=entries,event_base_object=base,
        wire=abi['wire'],phases=[],events=[],owners_stopped=False,
        scope='Two actual AP associations; secondary departure and zero->primary return. Primary departure, multi-endpoint routing, RF/WPA and churn remain separate')
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(yoradio=str(ROOT),firmware=args.firmware,qemu=str(args.qemu.resolve()),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='setup',display='none',
        persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=0)
    folder=args.output/'vm';session=observer=handle=kernel=trace=None
    primary,secondary='52:54:00:43:00:02','52:54:00:43:00:03'
    try:
        session,prepared=vm.launch(options,folder);kernel,handle=process_handle(session['pid'])
        report.update(pid=session['pid'],name=session['name'],prepared=prepared)
        observer=Observer(port);observer.socket.settimeout(120)
        trace=Events(observer,entries,base,abi['wire'],factory)
        expected_starts=0
        for phase_index,(mask,peers) in enumerate(((1,{primary}),(3,{primary,secondary}),
            (1,{primary}),(0,set()),(1,{primary}))):
            before=len(trace.rows)
            expected_starts+=len(peers-trace.active)
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                qmp.execute('qom-set',path='/machine/wifi',property='softap-client-mask',value=mask)
                assert qmp.execute('qom-get',path='/machine/wifi',property='softap-client-mask')==mask
            trace.until(peers,expected_starts if factory else 1)
            row=dict(mask=mask,active_peers=sorted(trace.active),event_range=[before,len(trace.rows)])
            if factory:row['tracked_server_handle']=int.from_bytes(observer.memory(0x3fcc3a70,4),'little')
            report['phases'].append(row)
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                row['model_clients']=json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-clients'))
            if peers:
                observer.resume()
                try:
                    url=session['web_urls']['setup']
                    if peers:
                        # AP_STACONNECTED precedes the virtual client's DHCP.
                        # Wait for its actual packet-driven relay state before
                        # sending the first SYN; do not treat association alone
                        # as an application network readiness event.
                        deadline=time.monotonic()+60;started=time.monotonic()
                        while True:
                            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                                relay=json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-clients'))
                            current={peer['mac']:peer for peer in relay}
                            if all(current[mac]['model_state']==5 and current[mac]['offered_ipv4']!='0.0.0.0' for mac in peers):break
                            assert time.monotonic()<deadline,('Virtual peer relay did not become ready',relay)
                            time.sleep(.05)
                        row['relay_ready_clients']=relay;row['relay_wait_host_seconds']=time.monotonic()-started
                    if phase_index==0:wait_http(url,'/getclocktype')
                    try:
                        status,body=http(url,'/getclocktype',timeout=10)
                        row['http']=dict(status=status,body=body.decode())
                    except (OSError,ConnectionError) as error:
                        row['http']=dict(error=type(error).__name__)
                finally:observer.interrupt()
                assert row['http'].get('status')==200,row
            if not factory:
                assert sum(event['function']=='httpd_start' for event in trace.rows)==1
                assert not any(event['function']=='httpd_stop' for event in trace.rows)
            vm.save_json(args.output/'report.json',report)
            print('Phase mask',mask,'peers',sorted(peers),row.get('http'),flush=True)
        if factory:
            # The second start can fail on the occupied port and overwrite
            # the original handle with NULL. Then stop cannot reach that
            # first server. Check the actual defect rather than assuming
            # every disconnect necessarily stops the live listener.
            assert len(trace.handles)==3 and trace.handles[0] and trace.handles[1:]==[0,0]
            assert report['phases'][0]['tracked_server_handle']==trace.handles[0]
            assert all(not phase['tracked_server_handle'] for phase in report['phases'][1:])
            uart=(folder/'uart.log').read_bytes()
            assert uart.count(b'error in listen (112)')==2
            report['factory_loses_original_server_handle']=True
        assert clean_uart(folder)
        assert all(sha(Path(name))==digest for name,digest in pins.items())
        report['passed']=True
    except BaseException as error:
        report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if trace:report['events']=trace.rows;report['server_handles']=trace.handles
        if observer:observer.close()
        if session:
            vm.control(folder,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            report['owners_stopped']=True
        vm.save_json(args.output/'report.json',report)
    print('PASS selected real AP peer/lifetime cases:',args.firmware,flush=True)


if __name__=='__main__':main()
