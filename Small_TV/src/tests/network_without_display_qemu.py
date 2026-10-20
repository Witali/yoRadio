"""Test guest HTTP/SNTP before and after reset with no LCD device in the VM.

This is a network-only software gate. It never captures or waits for a display.
The normal display/profile and all frozen full/H10 inputs remain untouched.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]


def digest(path):
    """Bind the network observations to exact unchanged executable inputs."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NetworkQmp:
    """Reject any accidental display observation while retaining a command audit."""
    def __init__(self,target):
        self.target=target
        self.commands=[]

    def execute(self,command,**arguments):
        """Forward only network/boot/source observation commands, never screendump."""
        allowed={'qom-list','qom-get','query-status','human-monitor-command','stop','cont','system_reset'}
        if command not in allowed:raise AssertionError('Non-network observation: '+command)
        self.commands.append(command)
        return self.target.execute(command,**arguments)


def require(condition,message):
    """Fail without converting an unobserved subsystem into a passing result."""
    if not condition:raise AssertionError(message)


def main():
    """Remove the LCD only from a copied profile and execute both real firmwares."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.qemu_root/'tools'))
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http
    source_profile=ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'
    profile=json.loads(source_profile.read_text())
    require([node['id'] for node in profile['devices']]==['lcd'],'Unexpected original device profile')
    profile['name']='small-tv-network-without-lcd';profile['devices']=[]
    target=args.output/'network-only-profile.json'
    target.write_text(json.dumps(profile,indent=2)+'\n',newline='\n')
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    rom=args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'
    files=[Path(__file__),source_profile,target,elf,rom,ROOT/'Small_TV/full-flash.bin']
    files += [archive/name for name in ('app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json')]
    snapshot=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    files += [args.qemu_root/row['file'] for row in snapshot['files']]
    files.append(args.qemu_root/'frozen-inputs.json')
    inputs={str(path.resolve()):digest(path) for path in files}
    report=dict(passed=False,all_functionality_verified=False,scope=__doc__,flows={},inputs_sha256=inputs,
        app_sha256=digest(archive/'app.bin'),native_elf_sha256=digest(elf),qemu_sha256=digest(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        display=dict(executed=False,passed=None,reason='No LCD device and no screenshot/readiness observation'),
        copied_profile_sha256=digest(target),started_utc=dt.datetime.now(dt.timezone.utc).isoformat())
    active=None
    try:
        for variant in ('original','reconstructed'):
            folder=args.output/variant;folder.mkdir()
            options=SimpleNamespace(yoradio=str(ROOT),firmware=variant,
                qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),rom_elf=str(rom),
                hardware_profile=str(target),network='clock',display='none',persistent=False,paused=False,gdb_port=0,http_base_port=0)
            layout=vm.application_state_layout(options) if variant=='reconstructed' else vm.factory_clock_layout(options)
            session,prepared=vm.launch(options,folder);active=folder
            row=dict(passed=False,session=session,clock_layout=layout,phases={},boot={},source_integrity={})
            report['flows'][variant]=row
            require(session['hardware_profile']['machine']=='esp32c2,default-peripherals=off' and
                session['hardware_profile']['arguments']==[],'VM still requested external modules')
            before=digest(folder/'flash.bin')
            with vm.QMP(session['qmp_port'],session['name']) as target_qmp:
                qmp=NetworkQmp(target_qmp)
                children=qmp.execute('qom-list',path='/machine/peripheral')
                require(all(node['name']!='lcd' for node in children),'LCD device still exists')
                row['lcd_absent_qom']=True
                properties=qmp.execute('qom-list',path='/machine/wifi')
                require(any(node['name']=='last-ntp-reply' for node in properties),'Missing exact NTP packet metadata')
                diagnostics=qmp.execute('qom-get',path='/machine/wifi',property='debug-logging')
                previous=0
                for phase in ('boot','reset'):
                    if phase=='reset':qmp.execute('system_reset')
                    network=vm.wait_for_clock_recovery(qmp,folder,layout,previous,True,diagnostics)
                    require(network['passed'],'SDK clock/network did not recover')
                    previous=network['ntp']['response_count']
                    wait_http(session['web_urls']['station'],'/getclocktype')
                    status,body=http(session['web_urls']['station'],'/getclocktype',timeout=10)
                    require(status==200 and body.strip() in (b'0',b'1',b'2',b'3'),'Real guest HTTP getter failed')
                    row['phases'][phase]=dict(passed=True,network=network,http_status=status,clocktype=int(body.strip()))
                row['qmp_commands']=qmp.commands
                require('screendump' not in qmp.commands,'Network gate used LCD readiness')
            vm.control(folder,'stop');vm.ensure_stopped(folder);active=None
            uart=(folder/'uart.log').read_bytes()
            row['boot']=dict(rom_boots=uart.count(b'ESP-ROM:esp32c2'),no_panic=not any(marker in uart for marker in
                (b'Guru Meditation',b'assert failed',b'abort() was called',b'watchdog got triggered')))
            row['boot']['passed']=row['boot']['rom_boots']==2 and row['boot']['no_panic']
            row['source_integrity']=dict(passed=digest(folder/'flash.bin')==before)
            require(row['boot']['passed'] and row['source_integrity']['passed'],'Boot or immutable snapshot source check failed')
            row['passed']=True
            vm.save_json(args.output/'report.json',report)
            print('PASS network without LCD:',variant,flush=True)
        require(not any(path.suffix in ('.ppm','.png') for path in args.output.rglob('*')),'Network gate created display captures')
        report['passed']=all(row['passed'] for row in report['flows'].values())
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
