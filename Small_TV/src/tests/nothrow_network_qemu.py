"""Check production setup, real NVS persistence, HTTP and SNTP with no display device."""
import argparse
import ctypes
from ctypes import wintypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace


def network_ready(sample, state, previous, expected_address):
    """Use this VM's configured STA address, not an old SLIRP subnet constant."""
    return bool(sample is not None and sample['response_count']>previous and
                abs(sample['difference_seconds'])<1 and state['connected'] and
                state['time_synced'] and not state['ap_active'] and
                state['station_address']==expected_address)


def main():
    """Use one owned VM at a time; preserve actual process exits and immutable input pins."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('helpers','qemu','rom','elf','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[3]
    sys.path.insert(0,str(args.helpers))
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    from runtime_supervisor_fixture import process_creation
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    profile=json.loads((root/'Small_TV/qemu/profiles/small-tv-c2.json').read_bytes())
    assert [d['id'] for d in profile['devices']]==['lcd']
    profile['devices']=[];profile['name']='small-tv-nothrow-network-only'
    target=out/'network-profile.json';target.write_text(json.dumps(profile,indent=2)+'\n',newline='\n')
    archive=root/'firmware/development/small-tv-esp32c2-reconstructed'
    files=[Path(__file__),args.elf,args.qemu,args.rom,target,root/'Small_TV/qemu/profiles/small-tv-c2.json']
    files+=list(args.helpers.glob('*.py'))+[archive/name for name in
        ('app.bin','assets.bin','bootloader.bin','partition-table.bin','manifest.json','source-manifest.json')]
    pins={str(p.resolve()):vm.digest(p.read_bytes()) for p in files}
    report=dict(passed=False,inputs_sha256=pins,sessions=[],phases=[],display_tested=False,
                full_vm_oom_injection=False,physical_hardware_tested=False)
    class Weather(BaseHTTPRequestHandler):
        """Keep optional weather retries on loopback during this NVS/network check."""
        def do_GET(self):
            """Return a deterministic retryable error without logging guest headers or URLs."""
            self.send_response(503);self.send_header('Content-Length','0');self.end_headers()
        def log_message(self,*args):
            """Suppress request details; they are irrelevant to this network contract."""
    server=ThreadingHTTPServer(('127.0.0.1',0),Weather)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    options=SimpleNamespace(yoradio=str(root),firmware='reconstructed',qemu=str(args.qemu),rom_elf=str(args.rom),
        hardware_profile=str(target),network='setup',display='none',persistent=True,paused=False,
        gdb_port=0,http_base_port=0,service_port=server.server_port,app_elf=str(args.elf))
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=(wintypes.DWORD,wintypes.BOOL,wintypes.DWORD);kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=(wintypes.HANDLE,wintypes.DWORD)
    kernel.GetExitCodeProcess.argtypes=(wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD))
    kernel.CloseHandle.argtypes=(wintypes.HANDLE,)
    active=None;handle=None;folder=out/'vm'
    def launch():
        """Capture the real kernel creation identity while the launched QMP owner is live."""
        nonlocal active,handle
        active,prepared=vm.launch(options,folder)
        handle=kernel.OpenProcess(0x100000|0x1000,False,active['pid'])
        if not handle:raise ctypes.WinError(ctypes.get_last_error())
        identity=dict(pid=active['pid'],creation=process_creation(handle),name=active['name'])
        report['sessions'].append(dict(session=active,owner=identity,prepared=prepared))
        print(json.dumps(dict(launched=identity)),flush=True)
    def stop():
        """Quit only the named QMP owner and wait on its retained process handle."""
        nonlocal active,handle
        if active is None:return
        vm.control(folder,'stop')
        assert handle and kernel.WaitForSingleObject(handle,10000)==0,'Owned QEMU did not exit'
        code=wintypes.DWORD();assert kernel.GetExitCodeProcess(handle,ctypes.byref(code))
        report['sessions'][-1]['exit_code']=code.value;assert code.value==0
        kernel.CloseHandle(handle);handle=None;active=None;vm.ensure_stopped(folder)
    def station(phase, previous=0):
        """Require actual HTTP settings and a fresh SDK-synchronized NTP result."""
        url=active['web_urls']['station'];body=wait_http(url,'/getclocktype',expected=b'2')
        assert body.strip()==b'2'
        with vm.QMP(active['qmp_port'],active['name']) as qmp:
            assert all(n['name']!='lcd' for n in qmp.execute('qom-list',path='/machine/peripheral'))
            diagnostics=qmp.execute('qom-get',path='/machine/wifi',property='debug-logging')
            layout=vm.application_state_layout(options)
            expected=next(e['guest_address'] for e in active['web_endpoints'] if e['name']=='station')
            start=time.monotonic();initial=vm.radio_virtual_us(qmp);polls=0
            network=dict(passed=False,expected_station_address=expected)
            while True:
                sample=vm.ntp_reply_observation(qmp,folder,True,diagnostics,layout)
                state=vm.application_state(qmp,layout);polls+=1
                network.update(state=state,ntp=sample,polls=polls,host_seconds=time.monotonic()-start,
                               guest_seconds=((vm.radio_virtual_us(qmp)-initial)&0xffffffff)/1e6)
                if network_ready(sample,state,previous,expected):network['passed']=True;break
                if network['host_seconds']>60 or network['guest_seconds']>20:
                    report['failed_network_observation']=network
                    raise TimeoutError('No fresh SDK clock/STA state: '+json.dumps(network))
                time.sleep(.1)
        assert network['passed'] and clean_uart(folder)
        raw=(folder/'flash.bin').read_bytes()[0x3e7000:0x3e7400]
        assert raw[4:69].split(b'\0')[0]==b'yoRadio-QEMU'
        assert int.from_bytes(raw[0x160:0x164],'little')==1
        report['phases'].append(dict(name=phase,http_status=200,clocktype=2,network=network,
            rom_boots=(folder/'uart.log').read_bytes().count(b'ESP-ROM:esp32c2'),raw_settings_hex=raw.hex()))
        return network['ntp']['response_count']
    try:
        launch();urls=active['web_urls'];wait_http(urls['setup'],expected=b'/configure')
        status,body=http(urls['setup'],'/scan',timeout=20)
        assert status==200 and any(r.get('ssid')=='yoRadio-QEMU' for r in json.loads(body))
        assert http(urls['setup'],'/setclocktype',{'clocktype':2})[0]==200
        assert http(urls['setup'],'/configure',{'ssid':'yoRadio-QEMU','password':''})[0]==200
        station('configure-reboot');stop()
        launch();count=station('persistent-cold-boot')
        vm.control(folder,'reset');station('reset',count);stop()
        report['passed']=True
    except BaseException as error:
        report['error']=repr(error);raise
    finally:
        try:stop()
        finally:
            if handle:kernel.CloseHandle(handle)
            server.shutdown();server.server_close();worker.join(5)
            report['inputs_unchanged']=all(vm.digest(Path(p).read_bytes())==digest for p,digest in pins.items())
            report['passed'] &= report['inputs_unchanged'] and not worker.is_alive()
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    assert report['passed']
    print(json.dumps(dict(passed=True,phases=len(report['phases']),owners_exited=True,display_tested=False)),flush=True)


if __name__=='__main__':main()
