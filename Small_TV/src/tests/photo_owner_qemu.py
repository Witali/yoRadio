"""Actual async photo HTTP/cache persistence; no LCD or RF acceptance criterion."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import ctypes
from ctypes import wintypes
import hashlib
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import os
import re
from pathlib import Path
import sys
import threading
import time
from types import SimpleNamespace
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[3]


def sha(path):
    """Identify exact saved firmware, vectors and emulator bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Weather(BaseHTTPRequestHandler):
    """Owned loopback fixture; guest weather never needs an Internet service."""
    def do_GET(self):
        data=b'{"main":{"temp":295.15},"weather":[{"icon":"01d","description":"Fixture"}],"wind":{"speed":1},"sys":{"country":"CN"},"name":"Fixture"}'
        self.send_response(200);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

    def log_message(self,*arguments):
        """Do not mix background fixture logging into evidence JSON."""
        pass


class Probe:
    """Reuse one HTTP/1.1 connection as a browser normally does.

    Opening hundreds of short-lived TCP connections while a slow guest runs
    additionally tests TIME_WAIT/connection-churn RAM, a different workload.
    The same10second timeout and zero-error criterion still apply here.
    """
    def __init__(self,url):
        endpoint=urlsplit(url);assert endpoint.hostname=='127.0.0.1'
        self.host,self.port=endpoint.hostname,endpoint.port
        self.connection=None;self.opened=0

    def close(self):
        """Never consume a later response from a timed-out prior request."""
        if self.connection:self.connection.close();self.connection=None

    def get(self):
        """Read one complete bounded response before issuing the next probe."""
        if self.connection is None:
            self.connection=HTTPConnection(self.host,self.port,timeout=10);self.opened+=1
        try:
            self.connection.request('GET','/getclocktype')
            response=self.connection.getresponse();body=response.read(8193)
            assert len(body)<=8192
            status=response.status
            if response.will_close:self.close()
            return status,body
        except Exception:
            self.close();raise


def multipart(url,slot,index,chunks,data):
    """Use actual HTTP/MIME framing, separate from the C parser being tested."""
    boundary=b'SmallTVPhotoOwnerFixture'
    fields=[('file_number',str(slot).encode()),('chunk_index',str(index).encode()),
            ('total_chunks',str(chunks).encode()),('chunk',data)]
    body=b''.join(b'--'+boundary+b'\r\nContent-Disposition: form-data; name="'+name.encode()+b'"\r\n\r\n'+value+b'\r\n' for name,value in fields)
    body+=b'--'+boundary+b'--\r\n'
    endpoint=urlsplit(url);assert endpoint.hostname=='127.0.0.1'
    connection=HTTPConnection(endpoint.hostname,endpoint.port,timeout=20)
    try:
        connection.request('POST','/upload_chunk',body,{'Content-Type':'multipart/form-data; boundary='+boundary.decode(),'Origin':url,'Connection':'close'})
        response=connection.getresponse();return response.status,response.read(262144)
    finally:connection.close()


def process_handle(pid):
    """Pin the owned process identity, so completion cannot mean a reused PID."""
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    handle=kernel.OpenProcess(0x100000,False,pid)
    if not handle:raise ctypes.WinError(ctypes.get_last_error())
    return kernel,handle


def main():
    """Two owned cold processes, real requests, and exact persistent flash bytes."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--control',action='store_true',help='Same network/UI, no upload or foreground decode')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    os.environ['PYTHONDONTWRITEBYTECODE']='1'
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    sys.path.insert(0,str(args.qemu_root/'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    from qemu_storage import direct_flash_backing
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest=json.loads((archive/'manifest.json').read_text())
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    assert sha(elf)==manifest['elf_sha256']
    fixtures=ROOT/'Small_TV/src/tests/fixtures/jpeg_extended'
    vectors=json.loads((fixtures/'manifest.json').read_text())
    for name,digest in vectors['files'].items():assert sha(fixtures/name)==digest
    inputs={str(p.resolve()):sha(p) for p in [Path(__file__),elf,*[archive/name for name in ('app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json')],fixtures/'manifest.json']}
    report=dict(passed=False,control=args.control,all_functionality_verified=False,lcd_tested=False,rf_tested=False,
        hardware_tested=False,app_sha256=next(x['sha256'] for x in manifest['images'] if x['file']=='app.bin'),
        elf_sha256=sha(elf),source_sha256=manifest['source_sha256'],qemu_sha256=sha(args.qemu_root/'bin/qemu-system-riscv32.exe'),inputs_sha256=inputs,boots=[],cases=[])
    server=ThreadingHTTPServer(('127.0.0.1',0),Weather);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
        persistent=True,paused=True,gdb_port=0,http_base_port=0,service_port=server.server_port)
    session=None;handle=None;kernel=None;probe=None;executor=ThreadPoolExecutor(max_workers=1);before=None
    state=args.output/'vm'
    try:
        for boot in range(2):
            session,prepared=vm.launch(options,state);kernel,handle=process_handle(session['pid'])
            initial=(state/'flash.bin').read_bytes()
            if boot==0:before=initial
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                assert direct_flash_backing(qmp,state);qmp.execute('cont')
            url=session['web_urls']['station'];wait_http(url,'/getclocktype')
            probe=Probe(url)
            print('HTTP ready, cold boot',boot,flush=True)
            if args.control:
                row=dict(name='network-without-upload',probes=[]);report['cases'].append(row)
                for index in range(80):
                    start=time.monotonic()
                    try:
                        status,body=probe.get()
                        row['probes'].append(dict(status=status,seconds=time.monotonic()-start))
                        assert status==200 and body
                    except OSError as error:
                        row['probes'].append(dict(error=type(error).__name__,seconds=time.monotonic()-start))
                        print('Control HTTP failure',index,flush=True)
                    time.sleep(.25)
                assert all('error' not in probe for probe in row['probes']),'Control HTTP timeout; see probes'
            elif boot==0:
                for name in ('full-cmyk12.jpg','flat-sampling44-8.jpg','flat-sampling44-12.jpg','rich-progressive420-8.jpg','flat-gray-progressive-8.jpg'):
                    data=(fixtures/name).read_bytes();chunks=(len(data)+4095)//4096
                    status,body=http(url,'/start_upload',{'file_number':5,'file_size':len(data),'total_chunks':chunks},origin=url,timeout=30)
                    assert status==200 and body==b'OK',(status,body)
                    for index in range(chunks):assert multipart(url,5,index,chunks,data[index*4096:(index+1)*4096])==(200,b'OK')
                    row=dict(name=name,source_sha256=sha(fixtures/name),probes=[]);report['cases'].append(row)
                    print('Starting finish:',name,flush=True)
                    pending=executor.submit(http,url,'/finish_upload',{'file_number':5,'file_name':'file5.jpg'},240,url)
                    responsive=0;started=time.monotonic()
                    while not pending.done():
                        probe_at=time.monotonic()
                        try:
                            probe_status,probe_body=probe.get()
                        except (OSError,TimeoutError) as error:
                            # Preserve a live observation instead of terminating the
                            # decoder at the first symptom and losing its stop cause.
                            observation=dict(error=type(error).__name__,seconds=time.monotonic()-probe_at)
                            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                                observation['registers']=qmp.execute('human-monitor-command',**{'command-line':'info registers'})
                                observation['vm_status']=qmp.execute('query-status')
                                observation['guest_counter']=qmp.execute('human-monitor-command',**{'command-line':'xp /1wx 0x6004d000'})
                                if not any('ram_snapshot' in probe for probe in row['probes']):
                                    snapshot=args.output/('ram-case-'+str(len(report['cases']))+'.bin')
                                    qmp.execute('pmemsave',val=0x3fca0000,size=0x40000,filename=str(snapshot.resolve()))
                                    observation['ram_snapshot']=snapshot.name
                            row['probes'].append(observation)
                            print('HTTP probe failed:',observation['error'],flush=True)
                            if time.monotonic()-started>240:raise TimeoutError('Photo worker finish did not complete')
                            continue
                        unfinished=not pending.done()
                        row['probes'].append(dict(status=probe_status,seconds=time.monotonic()-probe_at,finish_pending=unfinished))
                        assert probe_status==200 and probe_body
                        responsive+=int(unfinished)
                        if time.monotonic()-started>240:raise TimeoutError('Photo worker finish did not complete')
                        time.sleep(.25)
                    status,body=pending.result();row.update(status=status,body=body.decode(),responsive_during_finish=responsive,seconds=time.monotonic()-started)
                    print('Finished:',name,status,body.decode(),row['seconds'],flush=True)
                    assert all('error' not in probe for probe in row['probes']),'HTTP timeout during decode; see probes'
                    # Heavy inputs may be refused by the measured runtime RAM
                    # policy; accepting only that precise resource reason does
                    # not waive malformed input, I/O or arbitrary decode errors.
                    valid=status==200
                    if name=='flat-gray-progressive-8.jpg':assert valid and body==b'OK' and responsive>0,row
                    elif name in ('full-cmyk12.jpg','rich-progressive420-8.jpg'):
                        assert valid and body==b'OK' or status==400 and body.startswith((b'heap-headroom;',b'service-heap-reserve;')),row
                    elif name.endswith('8.jpg'):
                        assert status==400 and body.startswith((b'backing-capacity;',b'heap-headroom;',b'service-heap-reserve;')),row
                    else:
                        assert status==400,row
                        assert body.startswith((b'library-pool-limit;',b'heap-headroom;',b'service-heap-reserve;')),row
                    if not valid:
                        assert b'available=' in body and b'required=' in body,row
                        amounts=re.search(rb'required=(\d+) available=(\d+)',body)
                        assert amounts and int(amounts[1])>int(amounts[2]),row
                    status,body=http(url,'/get_Photo_File?file=5&chunk=0&size=0')
                    info=json.loads(body);assert status==200 and info['exists']==valid and info['size']==(len(data) if valid else 0)
            else:
                status,body=http(url,'/get_Photo_File?file=5&chunk=0&size=0');assert status==200
                assert json.loads(body)=={'exists':True,'size':(fixtures/'flat-gray-progressive-8.jpg').stat().st_size}
                saved=bytearray();size=4096;length=(fixtures/'flat-gray-progressive-8.jpg').stat().st_size
                for index in range((length+size-1)//size):
                    status,body=http(url,f'/get_Photo_File?file=5&chunk={index}&size={size}');assert status==200;saved+=body
                assert bytes(saved)==(fixtures/'flat-gray-progressive-8.jpg').read_bytes()
                report['cold_source_exact']=True
            assert clean_uart(state)
            uart=(state/'uart.log').read_bytes();assert uart.count(b'ESP-ROM:esp32c2')==1
            (args.output/f'uart-{boot}.log').write_bytes(uart)
            report['boots'].append(dict(pid=session['pid'],name=session['name'],rom_boots=1,owners_stopped=False,probe_connections=probe.opened))
            probe.close();probe=None
            vm.control(state,'stop');assert kernel.WaitForSingleObject(handle,10000)==0
            kernel.CloseHandle(handle);handle=None;session=None
            report['boots'][-1]['owners_stopped']=True
            after=(state/'flash.bin').read_bytes()
            (args.output/f'flash-after-{boot}.bin').write_bytes(after)
        # NVS/preferences, selected source and explicitly owned cache/scratch may
        # change. Preserve all other physical bytes, including other four photos.
        plan=json.loads((archive/'jpeg-cache-plan.json').read_text())
        mutable=[(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]
        mutable += [(x['offset'],x['offset']+x['bytes']) for x in plan['candidate_extents']]
        changed=[i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
        assert all(any(start<=i<end for start,end in mutable) for i in changed)
        report['protected_bytes_unchanged']=True
        assert all(sha(Path(p))==digest for p,digest in inputs.items())
        report['passed']=True
    except Exception as error:
        report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if probe:probe.close()
        if session:
            for name in ('uart.log','qemu.log','flash.bin','session.json'):
                source=state/name
                if source.exists():(args.output/('failure-'+name)).write_bytes(source.read_bytes())
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(state,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
        executor.shutdown(wait=True,cancel_futures=True)
        server.shutdown();server.server_close();thread.join(5)
        vm.save_json(args.output/'report.json',report)
    print('PASS actual async photo owner:',len(report['cases']),'HTTP workflows, two owned processes stopped')


if __name__=='__main__':main()
