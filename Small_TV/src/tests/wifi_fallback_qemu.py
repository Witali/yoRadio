"""Compare real station DHCP waiting without replacing Wi-Fi, TCP/IP or firmware.

The built-in QEMU filter buffers external Ethernet replies while the radio still
associates normally. Only disposable synthetic settings and network delivery are
changed; guest RAM, registers, instructions and archived images stay untouched.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[3]


def digest(path):
    """Bind executable, observer and source identities to the bytes actually used."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def observe(qmp,folder,variant,settings,application):
    """Read only station state, public mode and boot count from the real guest."""
    qmp.execute('stop')
    try:
        seconds=int.from_bytes(read_bytes(qmp,0x6004d000,4),'little')/1e6
        with (folder/'flash.bin').open('rb') as stream:
            stream.seek(0x3e7000+0x160)
            raw_mode=int.from_bytes(stream.read(4),'little')
        boots=(folder/'uart.log').read_text(errors='replace').count('ESP-ROM:esp32c2')
        if variant=='original':
            mode=int.from_bytes(read_bytes(qmp,0x3fcb7b9c+352,4),'little')
            station_state=read_bytes(qmp,0x3fcc3a74,1)[0]
            connected=station_state==2
            # The restart/mode write precedes Wi-Fi initialization. Factory
            # d1c4 writes 5 only after esp_wifi_start, DHCP inspection and scan;
            # HTTP is checked separately through a real associated AP client.
            active_ap=mode==2 and station_state==5
            # The APSTA handler latches GOT_IP in its event group, without
            # changing state byte 5 to 2. Read that positive event separately;
            # it does not establish live connectivity after a later disconnect.
            apsta_got_ip=None
            if active_ap:
                group=int.from_bytes(read_bytes(qmp,0x3fcc3a7c,4),'little')
                if 0x3fcb0000<=group<=0x3fce0000-4:
                    apsta_got_ip=bool(int.from_bytes(read_bytes(qmp,group,4),'little')&1)
        else:
            mode=read_bytes(qmp,settings['address']+settings['fields']['wifi_mode'],1)[0]
            state=vm.application_state(qmp,application)
            connected,active_ap=state['connected'],state['ap_active']
            station_state=None
            apsta_got_ip=None
        return {'guest_seconds':seconds,'rom_boots':boots,'mode_ram':mode,'mode_raw':raw_mode,
                'connected':connected,'ap_active':active_ap,'factory_station_state':station_state,
                'factory_apsta_got_ip_event':apsta_got_ip}
    finally:qmp.execute('cont')


def hold_external_replies(qmp):
    """Attach the existing virtual-time packet buffer to the observed user backend."""
    network=qmp.execute('human-monitor-command',**{'command-line':'info network'})
    backends=[line.split(':',1)[0].split()[-1] for line in network.splitlines()
              if 'type=user' in line]
    if len(backends)!=1:raise AssertionError('Expected one isolated user-network backend')
    qmp.execute('object-add',**{'qom-type':'filter-buffer','id':'dhcp-delay',
        'netdev':backends[0],'queue':'tx','interval':120000000})
    properties={key:qmp.execute('qom-get',path='/objects/dhcp-delay',property=key)
                for key in ['status','queue','interval','netdev']}
    if properties!={'status':'on','queue':'tx','interval':120000000,'netdev':backends[0]}:
        raise AssertionError('External packet delay was not enabled')
    return properties


def wait_observation(qmp,folder,variant,settings,application,predicate,observations,host_seconds):
    """Wait for real state with a host stall bound, preserving every sampled transition."""
    deadline=time.monotonic()+host_seconds
    while True:
        sample=observe(qmp,folder,variant,settings,application)
        observations.append(sample)
        if predicate(sample):return sample
        if time.monotonic()>=deadline:raise TimeoutError('Station observation timed out: '+str(sample))
        time.sleep(.5)


def prepare_station(options,folder):
    """Seed only a synthetic saved station in an owned persistent flash copy."""
    prepared=vm.prepare(options,folder)
    data=bytearray((folder/'flash.bin').read_bytes())
    data[0x3e7000+4:0x3e7000+4+65]=b'yoRadio-QEMU'.ljust(65,b'\0')
    struct.pack_into('<I',data,0x3e7000+0x160,1)
    (folder/'flash.bin').write_bytes(data)
    before=[hashlib.sha256(data[a:b]).hexdigest() for a,b in [(0,0x9000),(0x10000,0x3e7000)]]
    return prepared,before


def stop_and_verify(folder,session,before):
    """Close only the owned VM and verify every executable/media byte stayed unchanged."""
    if session:vm.control(folder,'stop')
    after=(folder/'flash.bin').read_bytes()
    return all(hashlib.sha256(after[a:b]).hexdigest()==value
               for (a,b),value in zip([(0,0x9000),(0x10000,0x3e7000)],before))


def exercise(options,folder,variant,settings,application):
    """Hold DHCP past eighteen seconds, then require the original saved STA to recover."""
    options=SimpleNamespace(**vars(options),firmware=variant)
    prepared,before=prepare_station(options,folder)
    result={'passed':False,'sources':prepared['sources'],'observations':[]}
    session=None
    try:
        session,_=vm.launch(options,folder)
        result['session']={key:session[key] for key in ['name','pid','web_urls']}
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            if not direct_flash_backing(qmp,folder):raise AssertionError('Flash is not direct writable raw')
            result['filter']=hold_external_replies(qmp)
            qmp.execute('cont')
            held=wait_observation(qmp,folder,variant,settings,application,
                lambda row:row['guest_seconds']>=30,result['observations'],180)
            result['before_release']=held
            vm.capture_png(qmp,folder/'before-release.png')
            qmp.execute('qom-set',path='/objects/dhcp-delay',property='status',value='off')
            recovered=wait_observation(qmp,folder,variant,settings,application,
                lambda row:row['connected'] or row['ap_active'],result['observations'],90)
            result['after_release']=recovered
            vm.capture_png(qmp,folder/'after-release.png')
            result['checks']={
                'held_station_mode':held['mode_ram']==1 and held['mode_raw']==1,
                'no_premature_restart':held['rom_boots']==1,
                'no_ip_before_release':not held['connected'],
                'recovered_station':recovered['connected'] and not recovered['ap_active'],
                'saved_station_mode':recovered['mode_ram']==1 and recovered['mode_raw']==1,
                'same_boot_after_release':recovered['rom_boots']==1,
                'no_panic':clean_uart(folder)}
            if recovered['connected']:
                wait_http(session['web_urls']['station'],expected=b'/setclocktype')
                result['checks']['station_http']=True
            else:result['checks']['station_http']=False
            result['passed']=all(result['checks'].values())
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        result['executable_media_unchanged']=stop_and_verify(folder,session,before)
        result['passed'] &= result['executable_media_unchanged']
        vm.save_json(folder/'report.json',result)
    return result


def exercise_unavailable(options,folder,variant,settings,application):
    """Let real SDK retries fail, then verify setup with the retained station SSID."""
    options=SimpleNamespace(**vars(options),firmware=variant)
    prepared,before=prepare_station(options,folder)
    result={'passed':False,'sources':prepared['sources'],'observations':[]}
    session=None
    try:
        session,_=vm.launch(options,folder)
        result['session']={key:session[key] for key in ['name','pid','web_urls']}
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            if not direct_flash_backing(qmp,folder):raise AssertionError('Flash is not direct writable raw')
            qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=False)
            qmp.execute('cont')
            failed=wait_observation(qmp,folder,variant,settings,application,
                lambda row:row['rom_boots']>=2 and row['mode_raw']==2 and row['mode_ram']==2,
                result['observations'],300)
            result['before_restore']=failed
            result['external_ap_was_offline']=not qmp.execute('qom-get',path='/machine/wifi',property='station-ap-online')
            qmp.execute('qom-set',path='/machine/wifi',property='station-ap-online',value=True)
            wait_http(session['web_urls']['setup'],expected=b'/configure')
            setup=wait_observation(qmp,folder,variant,settings,application,
                lambda row:row['ap_active'],result['observations'],90)
            result['after_restore']=setup
            result['checks']={'setup_saved':failed['mode_raw']==2 and failed['mode_ram']==2,
                'restart_once':failed['rom_boots']==2 and setup['rom_boots']==2,
                'external_ap_offline':result['external_ap_was_offline'],'setup_http':True,
                'no_station_after_restore':not setup['connected'] and
                    (variant!='original' or setup['factory_apsta_got_ip_event'] is False),
                'setup_active':setup['ap_active'],
                'no_panic':clean_uart(folder)}
            vm.capture_png(qmp,folder/'setup.png')
            result['passed']=all(result['checks'].values())
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        result['executable_media_unchanged']=stop_and_verify(folder,session,before)
        result['passed'] &= result['executable_media_unchanged']
        vm.save_json(folder/'report.json',result)
    return result


def main():
    """Compare both applications and retain hash-bound observations with owned-VM cleanup."""
    global vm,read_bytes,direct_flash_backing,wait_http,clean_uart
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--dependency-root',type=Path,default=ROOT)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    sys.path.insert(0,str(args.qemu_root/'tools'))
    sys.path.insert(0,str(args.dependency_root/'.build/small-tv-parity/oracle-deps'))
    import small_tv_vm as vm
    from small_tv_http_test import wait_http,clean_uart
    from weather_qemu import read_bytes
    from regional_qemu import settings_layout
    from qemu_storage import direct_flash_backing
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='setup',
        display='none',persistent=True,paused=True,gdb_port=0)
    args.output.mkdir(parents=True,exist_ok=False)
    pins={str(path):digest(path) for path in [Path(__file__),Path(options.qemu),Path(options.hardware_profile),
        Path(options.rom_elf),ROOT/'Small_TV/full-flash.bin',
        ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf']}
    pins.update({str(args.qemu_root/'tools'/name):digest(args.qemu_root/'tools'/name) for name in
        ['small_tv_vm.py','small_tv_http_test.py','small_tv_network.py','small_tv_web.py',
         'small_tv_display.py', 'esp_elf.py','esp_board.py','esp_services.py']})
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    pins.update({str(archive/name):digest(archive/name) for name in
        ['app.bin','bootloader.bin','partition-table.bin','assets.bin','manifest.json','source-manifest.json']})
    for name in ['weather_qemu.py','regional_qemu.py','qemu_storage.py','machine_oracle.py']:
        path=Path(__file__).with_name(name);pins[str(path)]=digest(path)
    settings=settings_layout();application=vm.application_state_layout(options)
    report={'passed':False,'all_functionality_verified':False,'scope':__doc__,
        'tested_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'inputs_sha256':pins,
        'app_sha256':digest(archive/'app.bin'),'native_elf_sha256':settings['elf_sha256'],
        'qemu_sha256':digest(Path(options.qemu)),'flows':{},'failure_flows':{}}
    try:
        for variant in ['original','reconstructed']:
            active_flows='flows';active_folder=args.output/variant
            result=exercise(options,active_folder,variant,settings,application)
            report['flows'][variant]=result
            if not result['passed']:raise AssertionError('Delayed DHCP changed station mode: '+variant)
            print('PASS real station/DHCP delay:',variant,flush=True)
        for variant in ['original','reconstructed']:
            active_flows='failure_flows';active_folder=args.output/('missing-'+variant)
            result=exercise_unavailable(options,active_folder,variant,settings,application)
            report['failure_flows'][variant]=result
            if not result['passed']:raise AssertionError('SDK failure did not reach setup: '+variant)
            print('PASS real unavailable AP/setup:',variant,flush=True)
        report['passed']=True
    except Exception as error:
        report['error']=str(error)
        saved=active_folder/'report.json'
        if saved.exists():report[active_flows][variant]=json.loads(saved.read_text())
        raise
    finally:
        report['inputs_unchanged']=all(digest(Path(path))==value for path,value in pins.items())
        report['passed'] &= report['inputs_unchanged']
        vm.save_json(args.output/'report.json',report)
    if not report['passed']:raise AssertionError('Station waiting regression failed')


if __name__=='__main__':main()
