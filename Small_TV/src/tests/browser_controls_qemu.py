"""Real desktop/mobile controls and cold persistence on one owned raw QEMU image."""
import argparse
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]
RAW=0x3e7000


def digest(path):
    """Identify the exact firmware, observers and browser inputs used by this run."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition,message):
    """Retain the failed requirement instead of substituting a weaker observation."""
    if not condition:raise AssertionError(message)


def matches_raw(raw,expected):
    """Check the independently documented factory sector ABI against public API state."""
    state=expected['state']
    word=lambda offset:struct.unpack_from('<I',raw,offset)[0]
    string=lambda offset,size:raw[offset:offset+size].split(b'\0')[0].decode('ascii',errors='replace')
    if (string(0x86,65)!=expected['ntp'] or string(0xc7,20)!=expected['country'] or
        string(0xdb,65)!=expected['city'] or string(0x11c,65)!='SYNTHETIC_BROWSER_KEY'):return False
    fields={0x160:1,0x164:state['animation'],0x168:state['theme'],0x16c:state['flags']['tempUnit'],
        0x170:state['flags']['hourFormat'],0x174:state['flags']['mileDisplay'],0x178:state['flags']['timeSync'],
        0x17c:state['date'],0x180:1000-10*state['day'],0x190:state['flags']['nightmode'],
        0x194:state['start'],0x198:state['stop'],0x19c:1000-10*state['night'],0x1a0:state['interval'],
        0x1a4:sum(1<<(i-1) for i in range(1,6) if state['photos'][f'file{i}_switch'])}
    for i in range(3):
        color=int(state['colors']['color'+str(i)][1:],16)
        fields[0x184+4*i]=((color>>8)&0xf800)|((color>>5)&0x7e0)|((color>>3)&31)
    return all(word(offset)==value for offset,value in fields.items())


def main():
    """Run UI actions, wait for actual persistence, then verify a new VM process."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('qemu-root','node','playwright-modules','browser-executable','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=ROOT)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'))
    from esp_elf import object_symbols
    import small_tv_vm as vm
    from small_tv_http_test import wait_http,wait_for,clean_uart
    from qemu_storage import direct_flash_backing
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    require((archive/'app.bin').read_bytes()[176:208]==bytes.fromhex(digest(elf)),'ELF/app mismatch')
    dirty=object_symbols(elf.read_bytes(),('dirty',))['dirty']
    require(dirty['size']==1,'Expected a one-byte compiled dirty flag')
    files=[Path(__file__),Path(__file__).with_name('browser_controls_flow.mjs'),
        Path(__file__).with_name('qemu_storage.py'),elf,ROOT/'Small_TV/qemu/profiles/small-tv-c2.json',
        args.qemu_root/'bin/qemu-system-riscv32.exe',args.node,args.browser_executable,
        args.playwright_modules/'playwright/package.json']
    files += [archive/name for name in ('app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json')]
    files += [ROOT/'Small_TV/local_site/pages'/name for name in ('settings.html','photo.html')]
    files += [args.qemu_root/'tools'/name for name in ('small_tv_vm.py','small_tv_web.py','small_tv_network.py',
        'small_tv_http_test.py','small_tv_display.py','esp_elf.py','esp_board.py','esp_services.py')]
    inputs={str(path.resolve()):digest(path) for path in files}
    state=args.output/'vm'
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',
        qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),
        network='clock',display='none',persistent=True,paused=False,gdb_port=0,http_base_port=0)
    report=dict(passed=False,all_functionality_verified=False,inputs_sha256=inputs,stages={},checks={},
        app_sha256=digest(archive/'app.bin'),native_elf_sha256=digest(elf),
        qemu_sha256=digest(args.qemu_root/'bin/qemu-system-riscv32.exe'),dirty_symbol=dirty,
        scope='Real Chrome desktop/mobile settings, advanced editor and photo controls; raw ABI and cold persistence. Separate from display pixels, network/SNTP acceptance, crop/upload gates, physical hardware and H10.')
    session=None
    protected=lambda data:[hashlib.sha256(data[a:b]).hexdigest() for a,b in ((0,0x9000),(0xf000,RAW),(RAW+0x1000,0x400000))]
    try:
        vm.prepare(options,state);before=(state/'flash.bin').read_bytes()
        for stage in ('mutate','cold'):
            session,_=vm.launch(options,state)
            wait_http(session['web_urls']['station'],'/getclocktype')
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                require(direct_flash_backing(qmp,state),'Guest does not use its writable raw flash')
            report['stages'][stage]=dict(vm_name=session['name'],pid=session['pid'],direct_raw_backing=True)
            if stage=='cold':require(session['name']!=report['stages']['mutate']['vm_name'],'Cold process reused the VM')
            command=[str(args.node),str(Path(__file__).with_name('browser_controls_flow.mjs')),
                '--url',session['web_urls']['station'],'--stage',stage,'--output',str(args.output),
                '--modules',str(args.playwright_modules),'--browser',str(args.browser_executable)]
            with (args.output/('node-controls-'+stage+'.log')).open('w',encoding='utf-8') as log:
                process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=600)
            browser=json.loads((args.output/('browser-controls-'+stage+'.json')).read_text())
            report['stages'][stage]['browser']=browser
            require(process.returncode==0 and browser['passed'],'Browser '+stage+': '+str(browser.get('error')))
            for page in browser['pages']:
                if page['route'] not in ('/','/settings','/photo'):continue
                source=ROOT/'Small_TV/local_site/pages'/('photo.html' if page['route']=='/photo' else 'settings.html')
                require(page['sha256']==hashlib.sha256(source.read_text(encoding='utf-8').encode()).hexdigest(),'Guest HTML differs from source')
            expected=json.loads((args.output/'expected-controls.json').read_text())
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                def persisted():
                    """Observe idle before and after reading raw data, excluding partial page writes."""
                    def dirty_value():
                        text=qmp.execute('human-monitor-command',**{'command-line':f'xp /1bx 0x{dirty["address"]:x}'})
                        values=re.findall(r'0x([0-9a-fA-F]{2})\b',text)
                        require(len(values)==1,'Short dirty-flag observation')
                        return int(values[0],16)
                    if dirty_value()!=0:return False
                    raw=(state/'flash.bin').read_bytes()[RAW:RAW+444]
                    return matches_raw(raw,expected) and dirty_value()==0
                wait_for(persisted,'UI settings did not finish persistence')
            report['checks'][stage+'_raw_matches_all_controls']=True
            vm.control(state,'stop');vm.ensure_stopped(state);session=None
            uart=(state/'uart.log').read_bytes()
            require(clean_uart(state) and uart.count(b'ESP-ROM:esp32c2')==1,'Panic or unexpected reset during '+stage)
            report['stages'][stage]['rom_boots']=1
            (args.output/('uart-controls-'+stage+'.log.gz')).write_bytes(gzip.compress(uart,mtime=0))
            print('PASS browser controls:',stage,flush=True)
        report['checks']['protected_flash_and_photos_unchanged']=protected(before)==protected((state/'flash.bin').read_bytes())
        report['checks']['inputs_unchanged']=all(digest(Path(path))==value for path,value in inputs.items())
        report['checks']['cold_read_only']=report['stages']['cold']['browser']['posts']==[]
        require(all(report['checks'].values()),'Storage, source integrity or cold read-only check failed')
        report['passed']=True
    except Exception as error:
        report['error']=str(error);raise
    finally:
        if session:vm.control(state,'stop');vm.ensure_stopped(state)
        report['captured_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        vm.save_json(args.output/'report.json',report)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
