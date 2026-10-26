"""Repeated cold VM starts with independent boot, exact LCD and integrity results.

The reference is the actual factory AP instruction frame. No HTTP request,
association/DHCP/SNTP state, network callback, or UART marker can pass the LCD
check. These are QEMU process cycles, not physical power/RF/PWM acceptance.
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from display_boot_observer import observe_frame

ROOT=Path(__file__).resolve().parents[3]
FACTORY='5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'
FRAME='acc588ab852b81d9e034b64eb489c0f6a8057a3bf49477046c17071e414fffcd'


def digest(path):
    """Identify the actual input bytes and saved framebuffer witnesses."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected(data):
    """Exclude only writable NVS/raw settings, retaining executable and photo banks."""
    return [hashlib.sha256(data[a:b]).hexdigest() for a,b in
        ((0,0x9000),(0xf000,0x3e7000),(0x3e8000,0x400000))]


def main():
    """Start and stop a new owned VM per cycle while retaining per-subsystem failures."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cycles',type=int,default=20)
    parser.add_argument('--elf',type=Path,help='Explicit matching native ELF for an isolated production build')
    parser.add_argument('--qemu',type=Path,help='Explicit QEMU candidate; the frozen helper bundle remains unchanged')
    args=parser.parse_args()
    if not 1<=args.cycles<=100:raise ValueError('Expected 1..100 cycles per firmware')
    args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'))
    import small_tv_vm as vm
    from small_tv_display import ppm_pixels
    from qemu_storage import direct_flash_backing
    reference=ROOT/'Small_TV/src/tests/fixtures/display/factory-setup.ppm.gz'
    provenance=reference.with_name('factory-setup-provenance.json')
    meta=json.loads(provenance.read_text())
    expected_file=args.output/'factory-reference.ppm'
    expected_file.write_bytes(gzip.decompress(reference.read_bytes()))
    expected=ppm_pixels(expected_file)
    if (digest(reference)!=meta['gzip_sha256'] or digest(expected_file)!=meta['frame_file_sha256'] or
        hashlib.sha256(expected).hexdigest()!=FRAME or meta['full_flash_sha256']!=FACTORY):
        raise ValueError('Untrusted factory display reference')
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    elf=args.elf or ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    qemu=args.qemu or args.qemu_root/'bin/qemu-system-riscv32.exe'
    if (archive/'app.bin').read_bytes()[176:208]!=bytes.fromhex(digest(elf)):
        raise ValueError('Archived app and ELF mismatch')
    if digest(ROOT/'Small_TV/full-flash.bin')!=FACTORY:raise ValueError('Unknown factory firmware')
    rom=args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    snapshot=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    files=[Path(__file__),Path(__file__).with_name('display_boot_observer.py'),
        Path(__file__).with_name('qemu_storage.py'),reference,provenance,rom,elf,qemu,
        ROOT/'Small_TV/full-flash.bin',ROOT/'Small_TV/qemu/profiles/small-tv-c2.json',
        args.qemu_root/'frozen-inputs.json']
    files += [args.qemu_root/row['file'] for row in snapshot['files']]
    files += [archive/name for name in ('app.bin','bootloader.bin','partition-table.bin',
        'assets.bin','manifest.json','source-manifest.json')]
    inputs={str(path.resolve()):digest(path) for path in files}
    report=dict(passed=False,all_functionality_verified=False,scope=__doc__,inputs_sha256=inputs,
        requested_cycles_per_variant=args.cycles,variants=['original','reconstructed'],cycles=[],
        factory_flash_sha256=FACTORY,app_sha256=digest(archive/'app.bin'),native_elf_sha256=digest(elf),
        qemu_sha256=digest(qemu),expected_rgb_sha256=FRAME,
        network=dict(executed=False,passed=None,reason='No HTTP or SDK network-state observation'),
        started_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    active=None
    try:
        names=set()
        for variant in report['variants']:
            folder=args.output/variant
            options=SimpleNamespace(yoradio=str(ROOT),firmware=variant,
                qemu=str(qemu),rom_elf=str(rom),
                hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),
                network='setup',display='none',persistent=True,paused=False,gdb_port=0,http_base_port=-1)
            prepared=vm.prepare(options,folder)
            before=protected((folder/'flash.bin').read_bytes())
            for index in range(1,args.cycles+1):
                row=dict(variant=variant,cycle=index,passed=False,
                    boot=dict(passed=False),display=dict(passed=False),source_integrity=dict(passed=False),
                    network=dict(report['network']))
                report['cycles'].append(row)
                frame_folder=folder/f'cycle-{index:02d}';frame_folder.mkdir()
                # Each process owns a new UART capture; old markers cannot pass boot.
                (folder/'uart.log').unlink(missing_ok=True)
                session,launch=vm.launch(options,folder);active=folder
                row['session']={key:session[key] for key in ('name','pid','started_utc')}
                if session['name'] in names:raise AssertionError('Cold cycle reused a VM name')
                names.add(session['name'])
                row['prepared_flash_sha256']=launch['prepared_flash_sha256']
                try:
                    with vm.QMP(session['qmp_port'],session['name']) as qmp:
                        try:row['source_integrity']['direct_raw_backing']=direct_flash_backing(qmp,folder)
                        except Exception as error:row['source_integrity']['error']=str(error)
                        try:
                            row['display']=observe_frame(qmp,frame_folder,
                                lambda:vm.radio_virtual_us(qmp),ppm_pixels,expected)
                        except Exception as error:row['display']=dict(passed=False,error=str(error))
                        try:row['boot']['vm_running']=qmp.execute('query-status')['running']
                        except Exception as error:row['boot']['error']=str(error)
                finally:
                    vm.control(folder,'stop');vm.ensure_stopped(folder);active=None
                uart=(folder/'uart.log').read_bytes()
                row['boot'].update(rom_boots=uart.count(b'ESP-ROM:esp32c2'),
                    bootloader_entry=b'load:0x' in uart and b'entry 0x' in uart,
                    no_panic=not any(marker in uart for marker in (b'Guru Meditation',b'assert failed',
                        b'abort() was called',b'watchdog got triggered')))
                row['boot']['passed']=bool(row['boot'].get('vm_running') and row['boot']['rom_boots']==1 and
                    row['boot']['bootloader_entry'] and row['boot']['no_panic'])
                uart_path=frame_folder/'uart.log.gz';uart_path.write_bytes(gzip.compress(uart,mtime=0))
                row['uart']=dict(file=uart_path.relative_to(args.output).as_posix(),sha256=digest(uart_path))
                image=frame_folder/'display.ppm'
                if image.exists():
                    image_gz=image.with_suffix('.ppm.gz');image_gz.write_bytes(gzip.compress(image.read_bytes(),mtime=0))
                    row['frame']=dict(file=image_gz.relative_to(args.output).as_posix(),sha256=digest(image_gz))
                row['source_integrity']['protected_flash_unchanged']=protected((folder/'flash.bin').read_bytes())==before
                row['source_integrity']['passed']=bool(row['source_integrity'].get('direct_raw_backing') and
                    row['source_integrity']['protected_flash_unchanged'])
                row['passed']=all(row[k]['passed'] for k in ('boot','display','source_integrity'))
                vm.save_json(args.output/'report.json',report)
                print('Cold display:',variant,index,'boot',row['boot']['passed'],'display',row['display']['passed'],flush=True)
                if not row['passed']:raise AssertionError(f'Cold cycle failed: {variant}/{index}; see separate subsystem results')
        report['passed']=len(report['cycles'])==args.cycles*2 and all(row['passed'] for row in report['cycles'])
    except Exception as error:
        report['error']=str(error);raise
    finally:
        if active:vm.control(active,'stop');vm.ensure_stopped(active)
        report['inputs_unchanged']=all(digest(Path(path))==value for path,value in inputs.items())
        report['passed'] &= report['inputs_unchanged']
        report['ended_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        vm.save_json(args.output/'report.json',report)
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
