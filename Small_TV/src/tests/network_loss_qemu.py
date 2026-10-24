"""Drop one specified virtual AP peer packet and observe real SDK/DHCP recovery."""
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


STAGES=('probe','authentication','association','discover','request','offer','ack')


def main():
    """Require one consumed fault and an unaffected peer; keep failed recovery visible."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--qemu',type=Path,required=True)
    parser.add_argument('--abi',type=Path,required=True)
    parser.add_argument('--stage',choices=STAGES,required=True)
    parser.add_argument('--peer',type=int,choices=(0,1),default=1)
    parser.add_argument('--expect-timeout',action='store_true',help='Before-fix control only, never recovery acceptance')
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    abi=json.loads(args.abi.read_text());assert abi['passed']
    for name,digest in abi['inputs_sha256'].items():assert sha(Path(name))==digest
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf';entries,base=symbols(elf)
    files=[Path(__file__),args.qemu,args.abi,elf,*[Path(__file__).with_name(n) for n in
        ('network_clients_qemu.py','network_event_abi.py','gdb_observer.py','photo_owner_qemu.py','control_oracle.py','weather_qemu.py')]]
    pins={str(p.resolve()):sha(p) for p in files}
    bit=1<<(args.peer*7+STAGES.index(args.stage))
    report=dict(passed=False,recovery_acceptance=False,before_control=args.expect_timeout,
        network_lifecycle_complete=False,all_functionality_verified=False,lcd_acceptance=False,
        rf_acceptance=False,hardware_tested=False,stage=args.stage,peer=args.peer,drop_bit=bit,
        app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=sha(elf),qemu_sha256=sha(args.qemu),
        inputs_sha256=pins,wire=abi['wire'],entries=entries,event_base_object=base,samples=[],owners_stopped=False)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu.resolve()),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='setup',display='none',
        persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=0)
    session=observer=kernel=handle=trace=None
    try:
        session,prepared=vm.launch(options,args.output/'vm');kernel,handle=process_handle(session['pid'])
        report.update(pid=session['pid'],name=session['name'],prepared=prepared)
        observer=Observer(port);trace=Events(observer,entries,base,abi['wire'],False)
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            assert qmp.execute('qom-get',path='/machine/wifi',property='softap-drop-next')==0
            try:qmp.execute('qom-set',path='/machine/wifi',property='softap-drop-next',value=1<<21)
            except RuntimeError:report['invalid_mask_rejected']=True
            else:raise AssertionError('Invalid fault mask accepted')
            assert qmp.execute('qom-get',path='/machine/wifi',property='softap-drop-next')==0
            qmp.execute('qom-set',path='/machine/wifi',property='softap-drop-next',value=bit)
            qmp.execute('qom-set',path='/machine/wifi',property='softap-client-mask',value=3)
        trace.until({'52:54:00:43:00:02','52:54:00:43:00:03'},1)
        observer.resume();url=session['web_urls']['setup'];wait_http(url,'/getclocktype')
        host_deadline=time.monotonic()+90;drop_started=None
        while True:
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                clients=json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-clients'))
                faults=json.loads(qmp.execute('qom-get',path='/machine/wifi',property='softap-client-faults'))
                pending=qmp.execute('qom-get',path='/machine/wifi',property='softap-drop-next')
                seconds=weather.virtual_seconds(qmp)
            sample=dict(guest_seconds=seconds,clients=clients,faults=faults,pending=pending)
            report['samples'].append(sample)
            count=faults[args.peer]['dropped'][STAGES.index(args.stage)]
            if count:
                assert count==1 and pending==0
                if drop_started is None:drop_started=faults[args.peer]['last_drop_us'][STAGES.index(args.stage)]/1e6
                good=all(r['model_state']==5 and r['offered_ipv4']!='0.0.0.0' for r in clients[:2])
                if good:report['recovery_acceptance']=True;break
                if seconds-drop_started>=12:break
            assert time.monotonic()<host_deadline,sample
            time.sleep(.1)
        assert drop_started is not None
        assert sum(sum(peer['dropped']) for peer in faults)==1
        assert clients[1-args.peer]['model_state']==5
        result=http(url,'/getclocktype');report['http']=dict(status=result[0],body_hex=result[1].hex())
        assert result==(200,b'0')
        assert report['recovery_acceptance'] is (not args.expect_timeout),sample
        assert len(trace.handles)==1 and not any(e['function']=='httpd_stop' for e in trace.rows)
        assert clean_uart(args.output/'vm') and all(sha(Path(name))==digest for name,digest in pins.items())
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
        vm.save_json(args.output/'report.json',report)
    print('PASS',args.stage,'before-control' if args.expect_timeout else 'actual-recovery',flush=True)


if __name__=='__main__':main()
