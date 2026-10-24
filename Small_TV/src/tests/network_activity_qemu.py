"""Observe real AP departures inside scan/photo/theme requests, without LCD gates."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import json
from pathlib import Path
import socket
import sys
import time
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from machine_oracle import ELFFile, ROOT
from network_clients_qemu import Events, sha, symbols
from photo_owner_qemu import multipart, process_handle
from photo_write_budget_qemu import stop_at


PRIMARY, SECONDARY = '52:54:00:43:00:02', '52:54:00:43:00:03'
TARGETS = ('esp_wifi_scan_start', 'photo_upload_start_detailed', 'photo_upload_chunk',
           'photo_upload_finish_detailed', 'settings_select_theme')


def activity_symbols(elf):
    """Use exact compiled function entries, rejecting missing or ambiguous symbols."""
    with elf.open('rb') as stream:
        table = list(ELFFile(stream).get_section_by_name('.symtab').iter_symbols())
    rows = {name:{s['st_value'] for s in table if s.name == name and s['st_value']} for name in TARGETS}
    assert all(len(values) == 1 for values in rows.values()), rows
    return {name:next(iter(values)) for name,values in rows.items()}


class ActivityEvents(Events):
    """Change external peer presence at a real function entry inside HTTP handling."""
    def __init__(self, observer, entries, base, wire, vm, session):
        super().__init__(observer, entries, base, wire, False)
        self.vm, self.session, self.trigger, self.pending = vm, session, None, None

    def visit(self, pc, depth=0):
        """Keep all normal guest logic and capture nested SDK event/return ordering."""
        trigger = self.trigger
        begin = len(self.rows)
        if trigger and pc == self.entries[trigger['function']] and not trigger['fired']:
            trigger.update(fired=True, event_index=len(self.rows), entry_pc=pc,
                active_before=sorted(self.active), arguments=[self.observer.register(i) for i in range(10,15)],
                http_pending_at_entry=not self.pending.done())
            assert trigger['http_pending_at_entry']
            with self.vm.QMP(self.session['qmp_port'],self.session['name']) as qmp:
                trigger['mask_before'] = qmp.execute('qom-get',path='/machine/wifi',property='softap-client-mask')
                qmp.execute('qom-set',path='/machine/wifi',property='softap-client-mask',value=trigger['mask'])
                assert qmp.execute('qom-get',path='/machine/wifi',property='softap-client-mask') == trigger['mask']
        super().visit(pc,depth)
        self.rows[begin]['return_event_index'] = len(self.rows)


def peers(mask):
    """Map requested physical presence to distinct expected SDK event identities."""
    return {mac for index,mac in enumerate((PRIMARY,SECONDARY)) if mask & (1 << index)}


def ready(observer, vm, session, wanted):
    """Wait for real DHCP ACK state, without changing guest registers or networking."""
    observer.resume()
    try:
        deadline = time.monotonic()+60
        while True:
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                clients = json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-clients'))
            rows = {r['mac']:r for r in clients}
            if all(rows[mac]['online'] and rows[mac]['model_state']==5 and
                   rows[mac]['offered_ipv4']!='0.0.0.0' for mac in wanted):return clients
            assert time.monotonic()<deadline,clients
            time.sleep(.05)
    finally:observer.interrupt()


def operation(trace, targets, executor, function, mask, call):
    """Prove a normal request was in flight when its actual peer transition began."""
    observer = trace.observer; original = trace.entries
    trace.entries = {**original,function:targets[function]}
    trigger = dict(function=function,mask=mask,fired=False)
    trace.trigger = trigger; begin = len(trace.rows)
    for address in trace.entries.values():observer.breakpoint(address)
    future = executor.submit(call)
    trace.pending = future
    try:
        for _ in range(96):
            trace.visit(stop_at(observer,set(observer.breakpoints)))
            returned = [r for r in trace.rows[begin:] if r['function']==function and 'return_value' in r]
            if trigger['fired'] and returned and trace.active == peers(mask):break
        else:raise AssertionError('Operation/peer transition was not completed')
        assert len(returned)==1 and returned[0]['return_value']==0,returned
        assert len(trace.handles)==1 and not any(r['function']=='httpd_stop' for r in trace.rows)
        trigger.update(event_range=[begin,len(trace.rows)],active_after=sorted(trace.active))
        for address in list(observer.breakpoints):observer.breakpoint(address,False)
        observer.resume()
        try:
            status,body = future.result(timeout=900)
        finally:observer.interrupt()
        trigger.update(http=dict(status=status,body_hex=body.hex()))
        assert status==200,trigger
        return trigger,body
    finally:
        trace.entries = original; trace.trigger = None; trace.pending = None


def main():
    """Run actual scan/upload/theme traffic across alternating AP peer departures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--qemu',type=Path,required=True)
    parser.add_argument('--abi',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--cycles',type=int,default=2)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert 1<=args.cycles<=10
    args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    abi=json.loads(args.abi.read_text());assert abi['passed']
    for name,digest in abi['inputs_sha256'].items():assert sha(Path(name))==digest,name
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    entries,base=symbols(elf);targets=activity_symbols(elf)
    fixture=ROOT/'Small_TV/src/tests/fixtures/jpeg_extended/flat-gray-progressive-8.jpg'
    data=fixture.read_bytes();assert len(data)<=4096
    assert sha(fixture)=='45263a1cb1be94439742e66e5cfe09553cc9495aff6efee87ba465b6acebf5ec'
    files=[Path(__file__),args.abi,args.qemu,elf,fixture,*[Path(__file__).with_name(n) for n in
        ('network_clients_qemu.py','network_event_abi.py','gdb_observer.py','photo_owner_qemu.py',
         'photo_write_budget_qemu.py','control_oracle.py','machine_oracle.py')]]
    pins={str(p.resolve()):sha(p) for p in files}
    report=dict(passed=False,network_lifecycle_complete=False,all_functionality_verified=False,
        lcd_acceptance=False,rf_acceptance=False,hardware_tested=False,
        scope='Native AP scan/photo/theme requests with actual SDK peer transitions; one bridged host path. No STA weather/RF/full lifecycle acceptance.',
        app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=sha(elf),qemu_sha256=sha(args.qemu),
        inputs_sha256=pins,tools_snapshot=frozen,wire=abi['wire'],entries=entries,
        activity_entries=targets,event_base_object=base,cycles=args.cycles,operations=[],readbacks=[],events=[],owners_stopped=False)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu.resolve()),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='setup',display='none',
        persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=0)
    session=observer=kernel=handle=trace=None;executor=ThreadPoolExecutor(max_workers=1)
    try:
        session,prepared=vm.launch(options,args.output/'vm');kernel,handle=process_handle(session['pid'])
        report.update(pid=session['pid'],name=session['name'],prepared=prepared)
        observer=Observer(port);trace=ActivityEvents(observer,entries,base,abi['wire'],vm,session)
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            qmp.execute('qom-set',path='/machine/wifi',property='softap-client-mask',value=3)
        trace.until(peers(3),1);report['initial_clients']=ready(observer,vm,session,peers(3))
        url=session['web_urls']['setup']
        observer.resume();wait_http(url,'/getclocktype');observer.interrupt()
        for cycle in range(args.cycles):
            steps=[('scan','esp_wifi_scan_start',2,lambda:http(url,'/scan',timeout=120)),
                ('start','photo_upload_start_detailed',3,lambda:http(url,'/start_upload',dict(file_number=5,file_size=len(data),total_chunks=1),900,url)),
                ('chunk','photo_upload_chunk',1,lambda:multipart(url,5,0,1,data)),
                ('finish','photo_upload_finish_detailed',3,lambda:http(url,'/finish_upload',dict(file_number=5,file_name='file5.jpg'),900,url)),
                ('theme','settings_select_theme',2,lambda:http(url,'/setclocktype',dict(clocktype=1),30,url)),
                ('reselect','settings_select_theme',3,lambda:http(url,'/setclocktype',dict(clocktype=1),30,url))]
            for label,function,mask,call in steps:
                row,body=operation(trace,targets,executor,function,mask,call)
                row.update(cycle=cycle,action=label);report['operations'].append(row)
                if label=='scan':
                    records=json.loads(body)
                    assert {r['ssid'] for r in records}=={'yoRadio-QEMU','QEMU-2','QEMU-3'},records
                    assert all(r['rssi']<0 for r in records),records
                else:assert body==b'OK'
                row['ready_clients']=ready(observer,vm,session,peers(mask))
                vm.save_json(args.output/'report.json',report)
                print('Activity',cycle,label,'mask',mask,'HTTP',row['http']['status'],flush=True)
            observer.resume()
            try:
                theme=http(url,'/getclocktype')
                downloaded=http(url,'/get_Photo_File?file=5&chunk=0&size=4096')
                report['readbacks'].append(dict(cycle=cycle,theme_status=theme[0],theme_hex=theme[1].hex(),
                    photo_status=downloaded[0],photo_hex=downloaded[1].hex()))
                assert theme==(200,b'1') and downloaded==(200,data)
            finally:observer.interrupt()
        assert clean_uart(args.output/'vm')
        assert all(sha(Path(name))==digest for name,digest in pins.items())
        report['passed']=True
    except BaseException as error:
        report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if trace:report['events']=trace.rows;report['server_handles']=trace.handles
        if observer:observer.close()
        if session:
            vm.control(args.output/'vm','stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            report['owners_stopped']=True
        executor.shutdown(wait=True,cancel_futures=True)
        vm.save_json(args.output/'report.json',report)
    print('PASS AP scan/photo/theme traffic across real peer transitions',flush=True)


if __name__=='__main__':main()
