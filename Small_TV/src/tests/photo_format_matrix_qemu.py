"""Exercise the production HTTP/JPEG owner with archived, independently checked formats."""
from array import array
from concurrent.futures import ThreadPoolExecutor
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import socket
import struct
import sys
import tarfile
import time
from types import SimpleNamespace

from control_oracle import verify_inputs
from gdb_observer import Observer
from jpeg_oracle import JpegMachine
from machine_oracle import ROOT,ELFFile
from photo_flash_evidence import ready_frame,journal
from photo_owner_qemu import multipart,process_handle
import photo_runtime_metrics as metrics
from photo_target_state import describe as state_description
from photo_write_budget_qemu import descriptions,running_http,stop_at
from qemu_storage import direct_flash_backing
from verify_jpeg_clock_evidence import protected
import weather_qemu as weather


def sha(data):
    """Identify physical bytes, source fixtures, reports and runtime inputs."""
    return hashlib.sha256(data).hexdigest()


def fixtures(extra_manifest=None):
    """Read the committed corpus without extracting paths or regenerating entropy."""
    parity=ROOT/'Small_TV/qemu/parity'
    proof_path=parity/'jpeg-cache-pipeline-validation-20261020.json'
    proof=json.loads(proof_path.read_text());assert proof['passed']
    selected={}
    for suffix in ('/fixtures.tar.gz','/contract-closure/report.json.gz'):
        rows=[r for r in proof['raw_artifacts'] if r['file'].endswith(suffix)];assert len(rows)==1
        row=rows[0];file=(parity/row['file']).resolve();assert file.is_relative_to(parity.resolve())
        data=file.read_bytes();assert sha(data)==row['sha256'] and len(data)==row['bytes']
        unpacked=gzip.decompress(data);assert sha(unpacked)==row['uncompressed_sha256']
        selected[suffix]=(file,unpacked)
    expected={r['name']:r for r in proof['fixtures']};images={}
    with tarfile.open(fileobj=io.BytesIO(selected['/fixtures.tar.gz'][1]),mode='r:') as archive:
        for member in archive.getmembers():
            assert member.isfile() and member.name in expected and member.name not in images
            data=archive.extractfile(member).read();row=expected[member.name]
            assert len(data)==row['bytes'] and sha(data)==row['sha256'];images[member.name]=data
    assert images.keys()==expected.keys()
    contract=json.loads(selected['/contract-closure/report.json.gz'][1]);assert contract['passed']
    rows=[dict(name=r['name'],expected='valid',rgb565_sha256=r['rgb565_sha256']) for r in contract['positive']]
    rows += [dict(name=r['name'],expected='source-slot') for r in contract['limits']]
    rows += [dict(name=r['name'],expected=r['status']) for r in contract['negative']]
    assert len(rows)==len(images)==70
    pins={str(p.resolve()):sha(p.read_bytes()) for p in [proof_path,*[r[0] for r in selected.values()]]}
    if extra_manifest is not None:
        from jpeg_lossless_fixtures import load
        additional,extra_rows,extra_pins=load(extra_manifest)
        assert not images.keys()&additional.keys(),'Additional corpus cannot replace archived vectors'
        images.update(additional);rows.extend(extra_rows);pins.update(extra_pins)
    return images,rows,pins


def diagnostic(observer,address,layout):
    """Capture nested target fields from the actual caller-owned diagnostic."""
    data=observer.memory(address,layout['bytes'])
    def fields(base,description):
        result={}
        for name,field in description['fields'].items():
            at=base+field['offset']
            if field.get('fields'):result[name]=fields(at,field)
            elif field['bytes'] in (1,2,4,8):result[name]=int.from_bytes(data[at:at+field['bytes']],'little')
        return result
    return fields(0,layout)


def finish(observer,entry,layout,executor,http,url,vm,session,folder,metric_layout):
    """Observe ordinary async execution; never write code, RAM, registers or PC."""
    observer.breakpoint(entry)
    pending=executor.submit(http,url,'/finish_upload',dict(file_number=5,file_name='file5.jpg'),900,url)
    observer.continue_to(entry);observer.breakpoint(entry,False)
    returned=observer.register(1);address=observer.register(11);code=observer.memory(entry,4)
    with vm.QMP(session['qmp_port'],session['name']) as qmp:
        entered=weather.virtual_seconds(qmp)
        before=metrics.snapshot(qmp,folder,'entry',metric_layout)
    observer.breakpoint(returned);observer.continue_to(returned);observer.breakpoint(returned,False)
    result=dict(return_status=observer.register(10),diagnostic_address=address,
        diagnostic=diagnostic(observer,address,layout),entry_resources=before)
    with vm.QMP(session['qmp_port'],session['name']) as qmp:
        result['guest_seconds']=weather.virtual_seconds(qmp)-entered
        nested=address+layout['fields']['decode']['offset']
        result['exit_resources']=metrics.snapshot(qmp,folder,'exit',metric_layout,before['worker']['tcb_address'],nested)
        result['decode_diagnostic_address']=nested
    assert observer.memory(entry,4)==code
    observer.resume();status,body=pending.result(timeout=90);observer.interrupt()
    result.update(status=status,body=body.decode());return result


def factory_pixels(data,dependency_root):
    """Keep the original baseline IDCT/byte-clipping policy as the comparison oracle."""
    dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
    machine=JpegMachine('factory',dump,dependency_root=dependency_root)
    machine.dump=dump[:0x200000]+data+b'\xff'*512+dump[0x200000+len(data)+512:]
    asset=dict(width=240,height=240,source_length=len(data),flash_offset='0x200000')
    machine.draw(asset)
    pixels=array('H',machine.panel.pixels)
    if sys.byteorder!='little':pixels.byteswap()
    return dict(rgb565_sha256=sha(pixels.tobytes()),factory_elf_sha256=machine.source_sha,
        reference='literal factory RV32 baseline IDCT and RGB565 byte clipping; synthetic SDK input only')


def check_result(row,data,image,plan):
    """Require exact pixels or a specific resource/format reason, never arbitrary failure."""
    result=row['finish'];d=result['diagnostic'];expected=row['expected'];body=result['body']
    assert d['program_bytes']<=204800
    if result['status']==200:
        assert expected=='valid' and body=='OK' and result['return_status']==0
        row['cache']=ready_frame(image,plan,4,sha(data),row['rgb565_sha256'])
    else:
        assert result['status']==400 and result['return_status']!=0
        assert not journal(image,plan)['entries'][4]['ready']
        if expected=='valid':
            assert body.startswith(('flash-write-limit;','heap-headroom;','service-heap-reserve;',
                'library-pool-limit;','backing-capacity;')),row
        elif expected=='truncated-jpeg':assert d['privacy']['status']==3 or d['decode']['status']==3,row
        elif expected=='invalid-jpeg':assert d['privacy']['status']==2 or d['decode']['status']==2,row
        elif expected=='unsupported-jpeg':assert d['decode']['status']==4,row
        elif expected=='backing-capacity':assert body.startswith(('backing-capacity;','heap-headroom;','service-heap-reserve;')),row
        elif expected=='library-pool-limit':assert body.startswith(('library-pool-limit;','heap-headroom;','service-heap-reserve;')),row
        else:raise AssertionError(expected)
        if expected=='valid' or expected in ('backing-capacity','library-pool-limit'):
            values=re.search(r'required=(\d+) available=(\d+)',body)
            assert values and int(values[1])>int(values[2]),row


def main():
    """Own one real application VM; qualify formats separately from LCD/network gates."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--fixture-manifest',type=Path,help='Additional independently qualified fixtures; archived corpus stays intact')
    parser.add_argument('--names',nargs='+',help='Explicit pilot selection; not a complete corpus gate')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    images,cases,pins=fixtures(args.fixture_manifest)
    if args.names:
        assert set(args.names)<=set(images);cases=[r for r in cases if r['name'] in args.names]
        assert len(cases)==len(set(args.names))
    baseline=next((r for r in cases if r['name']=='rich-baseline-8.jpg'),None)
    if baseline:baseline.update(factory_pixels(images[baseline['name']],args.dependency_root))
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    weather.vm=vm
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for r in frozen['files']:assert sha((args.qemu_root/r['file']).read_bytes())==r['sha256']
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest=json.loads((archive/'manifest.json').read_text());plan=json.loads((archive/'jpeg-cache-plan.json').read_text())
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf';entries,layout=descriptions(elf)
    assert sha(elf.read_bytes())==manifest['elf_sha256']
    resources=metrics.describe(elf,state_description(elf),args.dependency_root)
    vm.save_json(args.output/'resource-layout.json',resources);vm.save_json(args.output/'diagnostic-layout.json',layout)
    files=[Path(__file__),elf,*[archive/n for n in ('app.bin','bootloader.bin','assets.bin','manifest.json','source-manifest.json','jpeg-cache-plan.json')]]
    files += [Path(__file__).with_name(n) for n in ('photo_runtime_metrics.py','photo_target_state.py','jpeg_oracle.py',
        'photo_write_budget_qemu.py','photo_flash_evidence.py','gdb_observer.py','photo_owner_qemu.py','weather_qemu.py',
        'control_oracle.py','qemu_storage.py','verify_jpeg_clock_evidence.py','machine_oracle.py','classic_oracle.py')]
    pins.update({str(p.resolve()):sha(p.read_bytes()) for p in files});pins.update(resources['sdk_sources'])
    report=dict(passed=False,all_functionality_verified=False,lcd_acceptance=False,network_acceptance=False,
        rf_tested=False,hardware_tested=False,physical_power_cut_tested=False,complete_corpus=args.names is None,
        app_sha256=verify_inputs(ROOT,args.dependency_root),elf_sha256=manifest['elf_sha256'],
        source_sha256=manifest['source_sha256'],qemu_sha256=sha((args.qemu_root/'bin/qemu-system-riscv32.exe').read_bytes()),
        program_limit_kib=200,inputs_sha256=pins,cases=[],owners_stopped=False,
        interpretation='Returned transport ledger plus physical source/frame/journal; not an independent raw callback trace or network/LCD acceptance')
    if args.fixture_manifest:report['fixture_manifest']=str(args.fixture_manifest.resolve())
    server=weather.WeatherFixture();server.set_response(200)
    executor=ThreadPoolExecutor(max_workers=1);session=observer=kernel=handle=None;folder=args.output/'vm'
    try:
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
        options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
            rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
            hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
            persistent=True,paused=True,gdb_port=port,http_base_port=0,service_port=server.port)
        session,prepared=vm.launch(options,folder);kernel,handle=process_handle(session['pid'])
        report.update(pid=session['pid'],name=session['name'])
        before=(folder/'flash.bin').read_bytes();(args.output/'before.bin').write_bytes(before)
        observer=Observer(port);observer.socket.settimeout(900)
        with vm.QMP(session['qmp_port'],session['name']) as qmp:assert direct_flash_backing(qmp,folder)
        observer.resume();url=session['web_urls']['station'];wait_http(url,'/getclocktype');observer.interrupt()
        status,body=running_http(observer,http,url,'/get_jpeg_write_limit');assert status==200 and json.loads(body)==dict(limit_kib=200)
        for selected in cases:
            work=[dict(selected)]
            for row in work:
                index=len(report['cases']);output=args.output/f'case-{index:03d}';output.mkdir()
                row['directory']=output.name;report['cases'].append(row)
                data=images[row['name']];row.update(source_sha256=sha(data),source_bytes=len(data))
                initial=(folder/'flash.bin').read_bytes();chunks=(len(data)+4095)//4096
                (output/'before.bin').write_bytes(initial);row['before_sha256']=sha(initial)
                status,body=running_http(observer,http,url,'/start_upload',dict(file_number=5,file_size=len(data),total_chunks=chunks))
                row['start']=dict(status=status,body=body.decode())
                if row['expected']=='source-slot':
                    assert len(data)>102400 and status==400
                    assert initial==(folder/'flash.bin').read_bytes(),'Rejected source admission mutated flash'
                    row['flash_unchanged']=True
                    (output/'after.bin').write_bytes(initial);row['after_sha256']=sha(initial)
                else:
                    assert status==200 and body==b'OK',row
                    observer.resume()
                    for chunk in range(chunks):assert multipart(url,5,chunk,chunks,data[chunk*4096:(chunk+1)*4096])==(200,b'OK')
                    observer.interrupt();row['finish']=finish(observer,entries['photo_upload_finish_detailed'],layout,
                        executor,http,url,vm,session,output,resources)
                    physical=(folder/'flash.bin').read_bytes();check_result(row,data,physical,plan)
                    accepted=row['finish']['status']==200
                    status,body=running_http(observer,http,url,'/get_Photo_File?file=5&chunk=0&size=0')
                    row['published']=json.loads(body)
                    assert status==200 and row['published']==dict(exists=accepted,size=len(data) if accepted else 0)
                    protected(initial,physical,[(0x9000,0xf000),(0x3e7000,0x3e8000),(0x264000,0x27d000)]+
                        [(r['offset'],r['offset']+r['bytes']) for r in plan['candidate_extents']])
                    (output/'after.bin').write_bytes(physical);row['after_sha256']=sha(physical)
                failed=row['start']['status']!=200 or row.get('finish',{}).get('status')!=200
                if failed:
                    assert 'recovery_for' not in row,'Known good recovery input failed'
                    work.append(dict(name='flat-gray-progressive-8.jpg',expected='valid',
                        rgb565_sha256='a3ec07b094d96c0fc6b420ba1a8666639a108c9e925c5f199c3e8f6f8ee10745',recovery_for=index))
                row['passed']=True;vm.save_json(args.output/'report.json',report)
                print('Case',index,row['name'],row['start']['status'],row.get('finish',{}).get('status'),
                    row.get('finish',{}).get('body','source admission rejected'),flush=True)
        assert clean_uart(folder)
        observer.close();observer=None;vm.control(folder,'stop');assert kernel.WaitForSingleObject(handle,10000)==0
        kernel.CloseHandle(handle);handle=None;session=None;report['owners_stopped']=True
        assert all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
        report['passed']=True
    except Exception as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if observer:observer.close()
        if session:
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(folder,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
            report['owners_stopped']=True
        executor.shutdown(wait=True,cancel_futures=True);server.close();vm.save_json(args.output/'report.json',report)
    print('PASS production C2 format matrix:',len(cases),'corpus vectors,',len(report['cases']),'actual workflows',flush=True)


if __name__=='__main__':main()
