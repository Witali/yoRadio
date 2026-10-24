"""Keep one AP client without DHCP and test the other client's ordinary HTTP path."""
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
from machine_oracle import ROOT
from network_clients_qemu import Events,sha,symbols
from photo_owner_qemu import process_handle
import weather_qemu as weather


def main():
    """Rearm a real DISCOVER loss, never a guest flag, then permit normal recovery."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--qemu',type=Path,required=True)
    parser.add_argument('--abi',type=Path,required=True)
    parser.add_argument('--peer',type=int,choices=(0,1),default=0)
    parser.add_argument('--expect-http-failure',action='store_true',help='Before-fix observation only')
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,clean_uart
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    abi=json.loads(args.abi.read_text());assert abi['passed']
    for name,digest in abi['inputs_sha256'].items():assert sha(Path(name))==digest
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf';entries,base=symbols(elf)
    files=[Path(__file__),args.abi,args.qemu,elf,*[Path(__file__).with_name(name) for name in
        ('network_clients_qemu.py','network_event_abi.py','gdb_observer.py','photo_owner_qemu.py','control_oracle.py','weather_qemu.py')]]
    pins={str(p.resolve()):sha(p) for p in files}
    report=dict(passed=False,expected_http_failure=args.expect_http_failure,network_lifecycle_complete=False,
        all_functionality_verified=False,lcd_acceptance=False,rf_acceptance=False,hardware_tested=False,
        app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=sha(elf),qemu_sha256=sha(args.qemu),
        inputs_sha256=pins,peer=args.peer,entries=entries,wire=abi['wire'],event_base_object=base,
        samples=[],owners_stopped=False)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu.resolve()),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='setup',display='none',
        persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=0)
    session=observer=kernel=handle=trace=None;executor=ThreadPoolExecutor(max_workers=1)
    bit=1<<(args.peer*7+3);pending=None
    try:
        session,prepared=vm.launch(options,args.output/'vm');kernel,handle=process_handle(session['pid'])
        report.update(pid=session['pid'],name=session['name'],prepared=prepared)
        observer=Observer(port);trace=Events(observer,entries,base,abi['wire'],False)
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            qmp.execute('qom-set',path='/machine/wifi',property='softap-drop-next',value=bit)
            qmp.execute('qom-set',path='/machine/wifi',property='softap-client-mask',value=3)
        trace.until({'52:54:00:43:00:02','52:54:00:43:00:03'},1)
        observer.resume();url=session['web_urls']['setup'];deadline=time.monotonic()+240
        phase='hold';first_drop=None
        while True:
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                clients=json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-clients'))
                faults=json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-client-faults'))
                mask=qmp.execute('qom-get',path='/machine/wifi',property='softap-drop-next')
                seconds=weather.virtual_seconds(qmp)
                count=faults[args.peer]['dropped'][3]
                if count and first_drop is None:first_drop=faults[args.peer]['last_drop_us'][3]/1e6
                row=dict(phase=phase,guest_seconds=seconds,clients=clients,faults=faults,pending_mask=mask)
                report['samples'].append(row)
                if phase=='hold':
                    if mask==0:qmp.execute('qom-set',path='/machine/wifi',property='softap-drop-next',value=bit)
                    healthy=clients[1-args.peer]['model_state']==5
                    if healthy and pending is None:pending=executor.submit(http,url,'/getclocktype',None,120)
                    if count>=2 and healthy and seconds-first_drop>=10:
                        assert clients[args.peer]['model_state']==6 and clients[args.peer]['offered_ipv4']=='0.0.0.0'
                        report['held_until']=row;report['http_done_while_held']=pending.done()
                        if pending.done():
                            status,body=pending.result();report['http_while_held']=dict(status=status,body_hex=body.hex())
                            assert (status,body)==(200,b'0')
                        qmp.execute('qom-set',path='/machine/wifi',property='softap-drop-next',value=0)
                        phase='recovery'
                elif all(r['model_state']==5 and r['offered_ipv4']!='0.0.0.0' for r in clients[:2]):
                    report['recovered']=row;break
            assert time.monotonic()<deadline,row
            time.sleep(.05)
        status,body=pending.result(timeout=60);report['pending_http_final']=dict(status=status,body_hex=body.hex())
        assert (status,body)==(200,b'0')
        status,body=http(url,'/getclocktype',timeout=30)
        report['http_after_recovery']=dict(status=status,body_hex=body.hex());assert (status,body)==(200,b'0')
        assert len(trace.handles)==1 and not any(e['function']=='httpd_stop' for e in trace.rows)
        assert clean_uart(args.output/'vm') and all(sha(Path(name))==digest for name,digest in pins.items())
        assert report['http_done_while_held'] is (not args.expect_http_failure),report['held_until']
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
    print('PASS stalled-peer bridge liveness',args.peer,flush=True)


if __name__=='__main__':main()
