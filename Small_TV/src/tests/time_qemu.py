"""Exercise actual UDP SNTP fallback, clock updates and displayed dates in QEMU.

QMP changes only the opt-in service's responses. Guest registers, RAM, clocks and
executable bytes are never patched. Initial flash changes are synthetic settings
in disposable copies; both production applications and source images stay intact.
"""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import time
from types import SimpleNamespace
import uuid

from weather_qemu import ROOT,ELFFile,read_bytes,region
from field_qemu import text_pixels


def clock_layout():
    """Locate the compiled sync latch and simple renderer's real struct tm cache."""
    path=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf=ELFFile(stream)
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                if die.tag!='DW_TAG_subprogram' or die.attributes.get('DW_AT_name',None) is None:
                    continue
                if die.attributes['DW_AT_name'].value!=b'factory_draw_simple':continue
                for child in die.iter_children():
                    if child.tag=='DW_TAG_variable' and child.attributes.get('DW_AT_name') and child.attributes['DW_AT_name'].value==b'previous_time':
                        location=child.attributes.get('DW_AT_location')
                        if location and len(location.value)==5 and location.value[0]==3:
                            address=int.from_bytes(bytes(location.value[1:]),'little')
                            return {'sync_address':symbols['time_synced'],'calendar_address':address,
                                    'microseconds_offset_address':symbols['s_microseconds_offset'],
                                    'system_correction_address':symbols['s_correction_us'],
                                    'elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    raise AssertionError('Missing compiled simple-clock cache location')


def snapshot(qmp,variant,layout):
    """Observe identified time fields only; do not synthesize a successful notification."""
    if variant=='original':
        raw=read_bytes(qmp,0x3fcbffc8,10)
        year,month,day,hour,minute,second,weekday=struct.unpack('<I6B',raw)
        synced=bool(read_bytes(qmp,0x3fcc3ab8,1)[0])
    else:
        second,minute,hour,day,month,year,weekday,_,_=struct.unpack('<9i',read_bytes(qmp,layout['calendar_address'],36))
        year+=1900; month+=1
        synced=bool(read_bytes(qmp,layout['sync_address'],1)[0])
    return {'synced':synced,'year':year,'month':month,'day':day,'hour':hour,
            'minute':minute,'second':second,'weekday':weekday}


def ntp_trace(folder):
    """Parse only service indices/times; never publish arbitrary hostnames or UART text."""
    text=(folder/'qemu.log').read_text(encoding='utf-8',errors='replace')
    return {'requests':[{'server':int(a),'virtual_us':int(b)} for a,b in
                        re.findall(r'C2 NTP request server=(\d+) virtual_us=(\d+)',text)],
            'drops':[int(s) for s in re.findall(r'C2 NTP drop server=(\d+)',text)],
            'responses':[int(s) for s in re.findall(r'C2 NTP response server=(\d+)',text)],
            'times':[{'epoch':int(a),'virtual_us':int(b)} for a,b in
                     re.findall(r'C2 NTP reply unix_seconds=(\d+) virtual_us=(\d+)',text)]}


def service(qmp,epoch=None,mask=None,separate=None):
    """Configure only external NTP packet responses through the Wi-Fi device's QOM API."""
    for name,value in (('ntp-unix-seconds',epoch),('ntp-drop-mask',mask),('ntp-separate-servers',separate)):
        if value is not None:
            qmp.execute('qom-set',path='/machine/wifi',property=name,value=value)


def date_capture(qmp,folder,variant,layout,expected_text,seconds=30,previous_text=None):
    """Compare every date-band pixel with independently decoded immutable factory glyphs."""
    deadline=time.monotonic()+seconds
    clean=text_pixels(expected_text,240,0,0xffff)
    expected=clean
    if previous_text is not None:
        # Literal stock text writes clear only the new glyph rectangles. Keep
        # the old outer columns in an independently constructed full-band model;
        # compare every byte, including the visible residues, without masking.
        retained=bytearray(text_pixels(previous_text,240,0,0xffff))
        begin=(240-len(expected_text)*12)//2
        end=begin+len(expected_text)*12
        for y in range(24):
            a,b=(y*240+begin)*3,(y*240+end)*3
            retained[a:b]=clean[a:b]
        expected=bytes(retained)
    last=None
    while time.monotonic()<deadline:
        qmp.execute('stop')
        try:
            state=snapshot(qmp,variant,layout)
            path=folder/'time-frame.png'
            vm.capture_png(qmp,path)
            pixels=region(vm.ppm_pixels(path.with_suffix('.ppm')),[0,180,240,24])
            path.with_suffix('.ppm').unlink()
            last={'state':state,'date':expected_text,'different_bytes':sum(a!=b for a,b in zip(pixels,expected)),
                  'clean_different_bytes':sum(a!=b for a,b in zip(pixels,clean)),
                  'boot_time_seconds':int.from_bytes(read_bytes(qmp,0x60008050,8),'little')/1e6}
        finally:qmp.execute('cont')
        if not last['different_bytes']:return last
        time.sleep(.2)
    vm.save_json(folder/'failed-date-observation.json',last)
    raise AssertionError('Displayed date never matched '+expected_text+': '+str(last))


def clock_updated(qmp,folder,layout=None):
    """Read SDK timekeeping components, accounting for its reset-relative timer origin."""
    qmp.execute('stop')
    try:
        latest=ntp_trace(folder)['times'][-1]
        virtual=int.from_bytes(read_bytes(qmp,0x6004d000,4),'little')
        boot=int.from_bytes(read_bytes(qmp,0x60008050,8),'little')
        since_boot=virtual
        details={}
        if layout is not None:
            # Pinned C2/26-MHz SDK: ticks_to_us = ticks*5/52. The read-only
            # UNIT0 snapshot was latched by the guest's own timer reads. Newlib
            # adds the RTC/HRT offset and esp_system_get_time correction; these
            # change at reset and must not be replaced with QEMU lifetime time.
            high,low=struct.unpack('<II',read_bytes(qmp,0x60023040,8))
            offset=int.from_bytes(read_bytes(qmp,layout['microseconds_offset_address'],8),'little',signed=True)
            correction=int.from_bytes(read_bytes(qmp,layout['system_correction_address'],8),'little',signed=True)
            ticks=(high<<32)|low
            since_boot=ticks*5//52+offset+correction
            details={'systimer_ticks':ticks,'rtc_hrt_offset_us':offset,'system_correction_us':correction}
        expected=latest['epoch']+(virtual-latest['virtual_us'])/1e6
        actual=(boot+since_boot)/1e6
        observation={'actual_utc_seconds':actual,'expected_utc_seconds':expected,
                     'difference_seconds':actual-expected,'boot_time_us':boot,
                     'since_boot_us':since_boot,'virtual_us':virtual,**details}
        vm.save_json(folder/'latest-clock-observation.json',observation)
        return abs(actual-expected)<=1
    finally:qmp.execute('cont')


def ntp_control_contract(qmp):
    """Validate inert defaults and rejected QOM inputs before enabling service fixtures."""
    defaults={'ntp-unix-seconds':-1,'ntp-drop-mask':0,'ntp-separate-servers':False}
    for name,value in defaults.items():
        if qmp.execute('qom-get',path='/machine/wifi',property=name)!=value:
            raise AssertionError('NTP control default changed: '+name)
    for name,value in [('ntp-unix-seconds',-2),('ntp-drop-mask',8),('ntp-drop-mask',-1),
                       ('ntp-separate-servers','invalid')]:
        try:qmp.execute('qom-set',path='/machine/wifi',property=name,value=value)
        except RuntimeError:pass
        else:raise AssertionError('Invalid NTP control accepted: '+name)
        if qmp.execute('qom-get',path='/machine/wifi',property=name)!=defaults[name]:
            raise AssertionError('Rejected NTP control changed its previous value')
    return {'defaults_unchanged':True,'invalid_inputs_rejected':4}


def reconfigure(url,server):
    """Use the real advanced-settings HTTP endpoint to restart/reconfigure the client."""
    status,_=http(url,'/advancedset',{'ntp':server,'openweathermapKey':'disabled','clickCount':10})
    if status!=200:raise AssertionError('NTP settings HTTP request failed')


def exercise(options,folder,layout):
    """Drop servers 1/2, accept server 3, then test actual date corrections over UDP."""
    options=SimpleNamespace(**{**vars(options),'network':'clock','persistent':True,'paused':True})
    prepared=vm.prepare(options,folder)
    flash=folder/'flash.bin'
    data=bytearray(flash.read_bytes())
    data[0x3e7000+0x86:0x3e7000+0x86+65]=b'10.0.2.4'.ljust(65,b'\0')
    struct.pack_into('<I',data,0x3e7000+0x168,1) # Simple theme, recovered raw settings ABI.
    flash.write_bytes(data)
    # HTTP settings are expected to change NVS/raw preferences in this disposable
    # persistent image. Verify executable/media regions separately from settings.
    immutable=[(0,0x9000),(0x10000,0x3e7000)]
    before=[hashlib.sha256(data[a:b]).hexdigest() for a,b in immutable]
    session=None
    result={'passed':False,'sources':prepared['sources'],'stages':{},'checks':{},'clock_observations':{}}
    try:
        session,_=vm.launch(options,folder)
        url=session['web_urls']['station']
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            result['ntp_control_contract']=ntp_control_contract(qmp)
            epoch=1709179420 # 2024-02-29 04:03:40 UTC, CN 12:03:40.
            service(qmp,epoch,7,True)
            qmp.execute('cont')
            wait_http(url,'/getclocktype',expected=b'1')
            if options.firmware=='original':
                wait_for(lambda:len(ntp_trace(folder)['requests'])>=3,'Factory repeated restart pattern missing')
                # Observe beyond the normal server timeout; three early requests
                # alone would not prove that a later fallback was starved.
                first=ntp_trace(folder)['requests'][0]['virtual_us']
                wait_for(lambda:int.from_bytes(read_bytes(qmp,0x6004d000,4),'little')>=first+35000000,
                         'Factory fallback observation did not reach its timeout window')
            else:
                wait_for(lambda:2 in ntp_trace(folder)['drops'],'Second NTP server was never tried')
            result['stages']['before_first_reply']=date_capture(qmp,folder,options.firmware,layout,'2025/9/19')
            if result['stages']['before_first_reply']['state']['synced']:
                raise AssertionError('SNTP was reported successful before any service reply')
            if options.firmware=='original':
                # 0x42010c3e is esp_sntp_restart, not an enabled/status query.
                # While the year is still below 2025 its 21-loop restarts starve
                # the third-server timeout. Retain this literal failure explicitly.
                stuck=ntp_trace(folder)
                if stuck['responses'] or 3 in [r['server'] for r in stuck['requests']]:
                    raise AssertionError('Factory did not reproduce the observed fallback starvation')
                result['stages']['factory_fallback_starvation']=stuck
                service(qmp,mask=0) # Release the active server through a real packet.
                wait_for(lambda:bool(ntp_trace(folder)['responses']),'Released factory server never replied')
            else:
                service(qmp,mask=3)
                wait_for(lambda:3 in ntp_trace(folder)['responses'],'Third NTP fallback never replied')
            wait_for(lambda:snapshot(qmp,options.firmware,layout)['synced'],'Actual SNTP notification missing')
            trace=ntp_trace(folder)
            if options.firmware=='reconstructed' and ([r['server'] for r in trace['requests'][:3]]!=[1,2,3] or trace['drops'][:2]!=[1,2]):
                raise AssertionError('SNTP did not try three distinct servers in order')
            native_layout=layout if options.firmware=='reconstructed' else None
            wait_for(lambda:clock_updated(qmp,folder,native_layout),'SNTP reply did not actually set the guest clock')
            result['clock_observations']['first_notification']=json.loads((folder/'latest-clock-observation.json').read_text())
            displayed='2024/2/29' if options.firmware=='reconstructed' else '2025/9/19'
            result['stages']['synchronized_2024']=date_capture(qmp,folder,options.firmware,layout,displayed)
            result['stages']['initial_trace']=trace
            # The pinned SDK retains its current server index across stop/init.
            # Drop servers 1 and 3 so reconfiguration must reach the configured
            # second server, even if the previous success was at server 3.
            epoch=1735726447
            service(qmp,epoch,0 if options.firmware=='original' else 5)
            count=len(ntp_trace(folder)['responses'])
            reconfigure(url,'cn.pool.ntp.org')
            wait_for(lambda:len(ntp_trace(folder)['responses'])>count,'Changed NTP settings never synchronized')
            wait_for(lambda:clock_updated(qmp,folder,native_layout),'Changed NTP server reply was not accepted by the SDK')
            result['clock_observations']['server_2_2025']=json.loads((folder/'latest-clock-observation.json').read_text())
            if options.firmware=='original':
                wait_for(lambda:snapshot(qmp,'original',layout)['year']==2025 and
                         snapshot(qmp,'original',layout)['month']==1,
                         'Factory calendar cache did not accept the 2025 correction')
                stale=date_capture(qmp,folder,'original',layout,'2025/9/19')
                if stale['state']['day']!=1 or stale['state']['month']!=1:
                    raise AssertionError('Factory stale-panel observation preceded the calendar update')
                result['stages']['factory_date_waits_for_minute']=stale
            result['stages']['server_2_2025']=date_capture(qmp,folder,options.firmware,layout,'2025/1/1',
                                                        seconds=90 if options.firmware=='original' else 30,
                                                        previous_text='2025/9/19' if options.firmware=='original' else None)
            if options.firmware=='reconstructed' and ntp_trace(folder)['responses'][-1]!=2:
                raise AssertionError('Configured second server did not answer')
            if options.firmware=='reconstructed':
                for name,epoch,label,server in [('year-jump',1767262447,'2026/1/1','10.0.2.4'),
                                              ('backward-leap-day',1709179420,'2024/2/29','cn.pool.ntp.org'),
                                              ('post-2038',2147483648,'2038/1/19','10.0.2.4')]:
                    count=len(ntp_trace(folder)['responses'])
                    service(qmp,epoch,5)
                    reconfigure(url,server)
                    wait_for(lambda:len(ntp_trace(folder)['responses'])>count,'NTP correction did not arrive: '+name)
                    wait_for(lambda:clock_updated(qmp,folder,native_layout),'NTP correction not accepted: '+name)
                    result['clock_observations'][name]=json.loads((folder/'latest-clock-observation.json').read_text())
                    result['stages'][name]=date_capture(qmp,folder,options.firmware,layout,label)
                # A retained RTC epoch is not a fresh SNTP notification after reset.
                service(qmp,mask=7)
                qmp.execute('system_reset')
                wait_http(url,'/getclocktype',expected=b'1')
                wait_for(lambda:not snapshot(qmp,'reconstructed',layout)['synced'],
                         'Reset retained the previous successful-sync latch')
                result['stages']['reset_before_notification']=date_capture(qmp,folder,'reconstructed',layout,'2025/9/19')
                count=len(ntp_trace(folder)['responses'])
                service(qmp,mask=5)
                wait_for(lambda:len(ntp_trace(folder)['responses'])>count,'Reset client never recovered after service returned')
                wait_for(lambda:snapshot(qmp,'reconstructed',layout)['synced'] and clock_updated(qmp,folder,native_layout),
                         'Reset did not receive a new real SNTP notification')
                result['clock_observations']['reset_recovered']=json.loads((folder/'latest-clock-observation.json').read_text())
                result['stages']['reset_recovered']=date_capture(qmp,folder,'reconstructed',layout,'2038/1/19')
            result['checks']={'literal_factory_failure_or_corrected_three_server_fallback':True,'actual_sntp_clock_update':True,
                              'first_notification_required':True,'date_pixels_checked':True,
                              'no_panic':clean_uart(folder)}
            result['trace']=ntp_trace(folder)
        result['passed']=all(result['checks'].values())
    except Exception as error:
        result['error']=str(error)
        result['trace']=ntp_trace(folder)
        if (folder/'latest-clock-observation.json').exists():
            result['last_clock_observation']=json.loads((folder/'latest-clock-observation.json').read_text())
        raise
    finally:
        if session:
            try:vm.control(folder,'stop')
            except OSError:pass
        after=flash.read_bytes()
        result['checks']['executable_media_unchanged']=all(hashlib.sha256(after[a:b]).hexdigest()==sha
                                                         for (a,b),sha in zip(immutable,before))
        result['passed'] &= result['checks']['executable_media_unchanged']
        vm.save_json(folder/'time-report.json',result)
    if not result['passed']:raise AssertionError('NTP flow failed')
    return result


def run_suite(options,output):
    """Run both immutable applications and retain only synthetic, hash-bound observations."""
    global vm,http,wait_http,wait_for,clean_uart
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    output.mkdir(parents=True,exist_ok=True)
    layout=clock_layout()
    report={'passed':False,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'flows':{},'layout':layout,'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),'scope':__doc__}
    run=output/('vms-'+uuid.uuid4().hex[:12])
    try:
        for variant in ('original','reconstructed'):
            options.firmware=variant
            report['flows'][variant]=exercise(options,run/variant,layout)
            print('PASS real SNTP fallback/time/LCD:',variant,flush=True)
        report['passed']=all(row['passed'] for row in report['flows'].values())
    except Exception as error:
        report['error']=str(error)
        if (run/options.firmware/'time-report.json').exists():
            report['flows'][options.firmware]=json.loads((run/options.firmware/'time-report.json').read_text())
        raise
    finally:vm.save_json(output/'report.json',report)
    return report


def main():
    """Use the built emulator and archived firmware; always close owned virtual machines."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    sys.path.insert(0,str(args.qemu_root/'tools'))
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),
        display='none',paused=True,gdb_port=0,http_base_port=0)
    run_suite(options,args.output)


if __name__=='__main__':main()
