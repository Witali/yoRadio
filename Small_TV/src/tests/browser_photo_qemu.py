"""Verify actual browser Canvas/crop/upload and cold persistence on an owned VM."""
import argparse
import hashlib
import gzip
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]


def main():
    """Bind a real headless Chrome flow to firmware/ELF and raw flash evidence."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=ROOT)
    parser.add_argument('--node',type=Path,required=True)
    parser.add_argument('--playwright-modules',type=Path,required=True)
    parser.add_argument('--browser-executable',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_http,clean_uart
    from qemu_storage import direct_flash_backing
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    app=archive/'app.bin'
    if app.read_bytes()[176:208]!=bytes.fromhex(digest(elf)):
        raise ValueError('App/ELF identities differ')
    files=[Path(__file__),Path(__file__).with_name('browser_photo_flow.mjs'),
           Path(__file__).with_name('qemu_storage.py'),elf,ROOT/'Small_TV/qemu/profiles/small-tv-c2.json',
           args.qemu_root/'bin/qemu-system-riscv32.exe',args.node,args.browser_executable]
    files += [archive/name for name in ('app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json')]
    files += [ROOT/'Small_TV/local_site'/name for name in ('pages/photo.html','photo_crop.js','photo_crop.html','jpeg_metadata.js','photo_upload.js')]
    files += [args.qemu_root/'tools'/name for name in ('small_tv_vm.py','small_tv_web.py','small_tv_http_test.py','small_tv_network.py','esp_board.py','esp_services.py','esp_elf.py')]
    inputs={str(path.resolve()):digest(path) for path in files}
    state=args.output/'vm'
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',
        qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),
        network='clock',display='none',persistent=True,paused=False,gdb_port=0,http_base_port=0)
    report=dict(passed=False,all_functionality_verified=False,inputs_sha256=inputs,
        app_sha256=digest(app),native_elf_sha256=digest(elf),qemu_sha256=digest(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        source_sha256=json.loads((archive/'manifest.json').read_text())['source_sha256'],stages={},
        scope='Actual Chrome controls/Canvas/metadata/multipart and persistent guest flash, with synthetic fixture images; not LCD frame equivalence, RF, physical or H10 acceptance.',checks={})
    session=None
    photo_base,slot_size=0x200000,0x19000
    protected=[(0,0x9000),(0xf000,photo_base),(photo_base+5*slot_size,0x3e7000),(0x3e8000,0x400000)]

    def checkpoint(condition,message):
        """Reject an incomplete observation instead of weakening the requirement."""
        if not condition:
            raise AssertionError(message)

    def image_digests(data,ranges):
        """Compare immutable flash intervals independently of photo HTTP state."""
        return [hashlib.sha256(data[a:b]).hexdigest() for a,b in ranges]

    try:
        vm.prepare(options,state)
        before=(state/'flash.bin').read_bytes()
        protected_before=image_digests(before,protected)
        untouched_before=image_digests(before,[(photo_base+i*slot_size,photo_base+(i+1)*slot_size) for i in range(3)])
        for stage in ('upload','cold'):
            session,_=vm.launch(options,state)
            url=session['web_urls']['station']
            wait_http(url,'/getclocktype')
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                checkpoint(direct_flash_backing(qmp,state),'Guest does not use its writable raw backing image')
                status=qmp.execute('query-status')
                checkpoint(status['running'],'Browser guest is not running')
            report['stages'][stage]={'vm_name':session['name'],'pid':session['pid'],'direct_raw_backing':True}
            if stage=='cold':
                checkpoint(session['name']!=report['stages']['upload']['vm_name'],'Cold stage reused the original VM')
            command=[str(args.node),str(Path(__file__).with_name('browser_photo_flow.mjs')),
                     '--url',url,'--stage',stage,'--output',str(args.output),
                     '--modules',str(args.playwright_modules),'--browser',str(args.browser_executable)]
            with (args.output/('node-'+stage+'.log')).open('w',encoding='utf-8') as log:
                result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=240)
            browser=json.loads((args.output/('browser-'+stage+'.json')).read_text())
            report[stage]=browser
            checkpoint(result.returncode==0 and browser['passed'],'Browser '+stage+' failed: '+str(browser.get('error')))
            expected=hashlib.sha256((ROOT/'Small_TV/local_site/pages/photo.html').read_text(encoding='utf-8').encode()).hexdigest()
            checkpoint(browser['served_html_sha256']==expected,'Guest served a different photo page')
            vm.control(state,'stop');vm.ensure_stopped(state);session=None
            for slot in (4,5):
                data=(args.output/f'final-slot{slot}.jpg').read_bytes()
                flash=(state/'flash.bin').read_bytes()
                start=photo_base+(slot-1)*slot_size
                checkpoint(flash[start:start+len(data)]==data,'Raw photo bytes do not match browser HTTP readback')
            report['checks'][stage+'_raw_photos_match']=True
            checkpoint(clean_uart(state),'Panic during browser '+stage)
            uart=(state/'uart.log').read_bytes()
            # Each cold process owns a fresh capture; an unnoticed warm reset
            # must not be hidden by the deliberate later VM restart.
            checkpoint(uart.count(b'ESP-ROM:esp32c2')==1,'Unexpected reset during browser '+stage)
            (args.output/('uart-'+stage+'.log.gz')).write_bytes(gzip.compress(uart,mtime=0))
            report['stages'][stage]['rom_boots']=1
        after=(state/'flash.bin').read_bytes()
        report['checks']['protected_flash_unchanged']=image_digests(after,protected)==protected_before
        report['checks']['slots_1_to_3_unchanged']=image_digests(after,[(photo_base+i*slot_size,photo_base+(i+1)*slot_size) for i in range(3)])==untouched_before
        report['checks']['source_inputs_unchanged']=all(digest(Path(path))==sha for path,sha in inputs.items())
        report['checks']['cold_boot_exact_photos']=True
        report['passed']=all(report['checks'].values())
    except Exception as error:
        report['error']=str(error)
        raise
    finally:
        if session:
            vm.control(state,'stop');vm.ensure_stopped(state)
        vm.save_json(args.output/'report.json',report)
    print(json.dumps(dict(passed=report['passed'],checks=report['checks'])))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
