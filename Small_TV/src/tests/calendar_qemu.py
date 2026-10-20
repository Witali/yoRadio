"""Follow natural calendar/DST transitions from real NTP packets to complete LCD frames.

Only synthetic HTTP settings and external NTP/weather responses are supplied.
Hardware breakpoints and bounded reads observe immutable running programs.
Independent pinned IANA TZif and real factory RV32 renderers form the references.
"""
import argparse
from dataclasses import asdict
import datetime as dt
import hashlib
import json
from pathlib import Path
import socket
import struct
import sys
import time
from types import SimpleNamespace
import uuid

from calendar_oracle import SimpleReference,simple_time
from control_oracle import verify_inputs
from frame_replay import SceneMachine,panel_rgb,write_rgb_png
from gdb_observer import Observer
from machine_oracle import Machine,ROOT,UC_HOOK_CODE
import regional_qemu as regional
import scene_qemu as scene
import time_qemu as clock
from timezone_oracle import TimeMachine
import weather_qemu as weather

THEMES={'classic':0,'simple':1,'dial':3}
CASES=[
    ('sunday','CN','2026-10-17T16:00:00','weekday'),
    ('new-year','CN','2025-12-31T16:00:00','year'),
    ('month-end','CN','2026-04-30T16:00:00','month'),
    ('leap-day-start','CN','2028-02-28T16:00:00','leap'),
    ('leap-day-end','CN','2028-02-29T16:00:00','leap'),
    ('noon','CN','2026-01-01T04:00:00','noon'),
    ('gb-spring','GB','2026-03-29T01:00:00','dst-forward'),
    ('gb-autumn','GB','2026-10-25T01:00:00','dst-backward'),
    ('us-spring','US-E','2026-03-08T07:00:00','dst-forward'),
    ('us-autumn','US-E','2026-11-01T06:00:00','dst-backward'),
    ('au-spring','AU-E','2026-10-03T16:00:00','dst-forward'),
    ('au-autumn','AU-E','2026-04-04T16:00:00','dst-backward'),
    ('fractional-midnight','NP','2026-01-01T18:15:00','fractional'),
    ('post-2038-midnight','IN','2038-01-19T18:30:00','post-2038'),
]


def requirements():
    """Bind each transition to independent TZif and rotate all six display styles per theme."""
    result=[]
    for index,(name,key,stamp,kind) in enumerate(CASES):
        boundary=int(dt.datetime.fromisoformat(stamp).replace(tzinfo=dt.timezone.utc).timestamp())
        zone=regional.zone(key)
        before=dt.datetime.fromtimestamp(boundary-1,zone)
        after=dt.datetime.fromtimestamp(boundary,zone)
        if kind.startswith('dst-') and before.utcoffset()==after.utcoffset():
            raise AssertionError('The declared DST input does not cross an IANA transition')
        if kind!='noon' and not kind.startswith('dst-') and before.date()==after.date():
            raise AssertionError('The declared calendar input does not cross local midnight')
        if kind=='weekday' and (before.weekday(),after.weekday())!=(5,6):
            raise AssertionError('The Sunday fixture is not Saturday to Sunday')
        result.append({'name':name,'country':key,'kind':kind,'boundary_utc':boundary,
                       'date_format':index%3,'hour12':(index//3)%2,
                       'iana_before':before.isoformat(),'iana_after':after.isoformat()})
    return result


def calendar_tuple(data):
    """Use standard calendar values, keeping DST metadata outside the display ABI."""
    return [data.year,data.month,data.day,data.hour,data.minute,data.second,data.weekday]


def packet_utc(qmp,folder):
    """Derive UTC from the last real NTP reply and elapsed emulated microseconds."""
    latest=clock.ntp_trace(folder)['times'][-1]
    virtual=int.from_bytes(weather.read_bytes(qmp,0x6004d000,4),'little')
    return latest['epoch']+(virtual-latest['virtual_us'])/1e6


def expected_calendars(utc,key,factory):
    """Evaluate an explicit one-second observation bound with IANA and literal Newlib."""
    iana=[];literal=[]
    for epoch in range(int(utc)-1,int(utc)+2):
        local=dt.datetime.fromtimestamp(epoch,regional.zone(key))
        iana.append([local.year,local.month,local.day,local.hour,local.minute,local.second,(local.weekday()+1)%7])
        tm=factory.local(epoch)
        literal.append([tm[5]+1900,tm[4]+1,tm[3],tm[2],tm[1],tm[0],tm[6]])
    return iana,literal


def settings_match(observer,variant,settings,theme,case):
    """Require the requested country/style/theme in actual guest settings before sampling."""
    if variant=='original':
        raw=observer.memory(0x3fcb7b9c,444)
        key=raw[0xc7:0xc7+20].split(b'\0')[0].decode('ascii')
        values=[int.from_bytes(raw[offset:offset+4],'little') for offset in (0x168,0x170,0x17c)]
    else:
        raw=observer.memory(settings['address'],settings['size']);fields=settings['fields']
        key=raw[fields['country']:fields['country']+20].split(b'\0')[0].decode('ascii')
        values=[raw[fields[field]] for field in ('theme','hour12','date_format')]
    return key==case['country'] and values==[THEMES[theme],case['hour12'],case['date_format']]


def corrected_frame(theme,data,dump,assets,cursor):
    """Execute a clean factory scene with only previously declared rendering corrections."""
    if theme=='classic':
        reference=SceneMachine('factory-weather-corrected',dump,assets)
        reference.render(data,reset=True,cursor=cursor)
    elif theme=='simple':
        reference=SimpleReference()
        simple_time(reference,data,True,minute_event=True,corrected=True)
    else:
        reference=Machine('factory-corrected')
        scene.seed_time(reference,data)
        reference.dial(reset=True);reference.dial(reset=False)
    return reference


def capture(qmp,observer,folder,variant,theme,case,settings,symbols,dump,assets,factory,stage,log_folder):
    """Observe one completed native frame, or literal factory call plus its known differences."""
    entry=(symbols['factory_draw_'+theme] if variant=='reconstructed' else
           {'classic':0x4200b738,'simple':0x4200bd8c,'dial':0x42009cf4}[theme])
    deadline=time.monotonic()+60
    observer.interrupt()
    while True:
        observer.breakpoint(entry);observer.continue_to(entry)
        registers={f'a{i}':observer.register(10+i) for i in range(7)}
        registers['ra']=observer.register(1)
        data=scene.inputs(observer,variant,theme,registers)
        utc=packet_utc(qmp,log_folder)
        iana,literal=expected_calendars(utc,case['country'],factory)
        actual=calendar_tuple(data)
        expected=iana if variant=='reconstructed' else literal
        # A complete simple reference needs a real colon event; the timer phase
        # intentionally differs from wall seconds. Do not force that guest flag.
        ready=settings_match(observer,variant,settings,theme,case) and actual in expected
        if theme=='simple' and variant=='reconstructed':ready &= bool(registers['a4']) and not registers['a3']
        if theme=='dial' and variant=='reconstructed':ready &= not registers['a2']
        if ready:break
        observer.breakpoint(entry,False)
        # Finish this real call before looking for another entry. Reinserting
        # a breakpoint at the current PC would stop the same instruction again.
        target=registers['ra']
        observer.breakpoint(target);observer.continue_to(target);observer.breakpoint(target,False)
        if time.monotonic()>deadline:raise AssertionError('No current renderer input: '+str((actual,expected)))
    code=observer.memory(entry,4)
    vm.save_json(folder/(stage+'-entry.json'),{'inputs':asdict(data),'packet_utc':utc,'registers':registers})
    sync_address=0x3fcc3ab8 if variant=='original' else symbols['time_synced']
    if not observer.memory(sync_address,1)[0]:raise AssertionError('No actual SNTP synchronization notification')
    before=scene.picture(qmp,folder,stage+'-before')
    flags=observer.memory(0x3fcc39f5,2) if variant=='original' and theme=='simple' else None
    classic_state=([(address,observer.memory(address,size)) for address,size in
                    ((0x3fcc39f5,8),(0x3fcc3a24,12))]
                   if variant=='original' and theme=='classic' else None)
    history=None
    if variant=='original' and theme=='dial':
        history=[(address,observer.memory(address,size)) for address,size in ((0x3fcb7d78,48),(0x3fcc3a00,24))]
    cursor=(observer.memory(0x3fcc3a24,1)[0] if variant=='original' else registers['a4']) if theme=='classic' else 0
    observer.breakpoint(entry,False)
    if observer.memory(entry,4)!=code:raise AssertionError('Hardware breakpoint modified entry code')
    target=registers['ra'];return_code=observer.memory(target,4)
    observer.breakpoint(target);observer.continue_to(target);observer.breakpoint(target,False)
    if observer.memory(target,4)!=return_code:raise AssertionError('Hardware breakpoint modified return code')
    pixels=scene.picture(qmp,folder,stage+'-complete')
    if scene.backlight(observer)['brightness']!=1000:raise AssertionError('Unexpected calendar-fixture backlight')
    reference=corrected_frame(theme,data,dump,assets,cursor)
    clean=panel_rgb(reference.panel)
    corrected=sum(pixels[i:i+3]!=clean[i:i+3] for i in range(0,len(pixels),3))
    replay_different=0
    if variant=='original':
        # Literal replay retains the recorded entry background and flags. It
        # proves the observed stock draw independently of its known stale fields.
        replay=SceneMachine('factory',dump,assets) if theme=='classic' else Machine('factory')
        replay.panel=scene.rgb_panel(before)
        if theme=='classic':
            def restore_entry(cpu,pc,size,context):
                """Restore only the observed flags/cache in the isolated literal model."""
                for address,raw in classic_state:cpu.mem_write(address,raw)
            replay.cpu.hook_add(UC_HOOK_CODE,restore_entry,begin=entry,end=entry)
            replay.render(data,reset=False,cursor=cursor)
        elif theme=='simple':
            scene.seed_time(replay,data)
            replay.simple(reset=False,minute_update=bool(flags[0]),second_update=bool(flags[1]))
        else:
            scene.seed_time(replay,data)
            for address,raw in history:replay.cpu.mem_write(address,raw)
            replay.dial(reset=False)
        literal_pixels=panel_rgb(replay.panel)
        replay_different=sum(a!=b for a,b in zip(pixels,literal_pixels))
        if replay_different:write_rgb_png(folder/(stage+'-literal-expected.png'),literal_pixels)
    if corrected and variant=='reconstructed':write_rgb_png(folder/(stage+'-expected.png'),clean)
    result={'passed':not replay_different and (variant=='original' or not corrected),
            'inputs':asdict(data),'packet_utc':utc,'matches_iana':actual in iana,
            'matches_literal_factory_calendar':actual in literal,
            'corrected_different_pixels':corrected,'literal_replay_different_bytes':replay_different,
            'rgb_sha256':hashlib.sha256(pixels).hexdigest(),'expected_rgb_sha256':hashlib.sha256(clean).hexdigest(),
            'entry':hex(entry),'code_unchanged':True,'compared_pixels':57600,
            'factory_flags':list(flags) if flags is not None else None}
    vm.save_json(folder/(stage+'-observation.json'),result)
    observer.resume()
    if not result['passed']:raise AssertionError('Calendar/frame comparison failed: '+str(result))
    return result


def exercise(options,folder,variant,themes,cases):
    """Reuse one isolated VM while naturally crossing each declared UTC boundary."""
    fixture=weather.WeatherFixture(['Shenzhen,CN']+['Fixture,'+row['country'] for row in cases])
    fixture.set_response(200)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
    options=SimpleNamespace(**{**vars(options),'firmware':variant,'network':'clock','paused':True,
                               'persistent':False,'gdb_port':port,'service_port':fixture.port})
    folder.mkdir(parents=True,exist_ok=True)
    observer=None;session=None;immutable=None
    result={'passed':False,'cases':[],'checks':{},'http_observations':[]}
    try:
        session,prepared=vm.launch(options,folder);result['sources']=prepared['sources']
        flash=(folder/'flash.bin').read_bytes();ranges=((0,0x9000),(0x10000,0x3e7000))
        immutable=[hashlib.sha256(flash[a:b]).hexdigest() for a,b in ranges]
        dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
        assets=json.loads((ROOT/'Small_TV/assets/manifest.json').read_text())
        symbols,_=scene.native_symbols();settings=regional.settings_layout()
        factory=TimeMachine('factory')
        observer=Observer(port)
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            clock.service(qmp,1781265600,0,False)
            observer.resume()
            url=session['web_urls']['station']
            def change(path,payload):
                """Measure guest latency while allowing the slower emulator a bounded host wait."""
                started=weather.virtual_seconds(qmp);host=time.monotonic()
                result['current_action'].update(http_path=path,virtual_seconds=started)
                try:status,_=http(url,path,payload,origin=url,timeout=20)
                except Exception:
                    result['current_action']['qemu_status']=qmp.execute('query-status')
                    result['current_action']['failed_virtual_seconds']=weather.virtual_seconds(qmp)
                    raise
                elapsed=weather.virtual_seconds(qmp)-started
                result['http_observations'].append({'path':path,'status':status,'guest_seconds':elapsed,
                                                    'host_seconds':time.monotonic()-host})
                if status!=200:
                    raise AssertionError('Settings response failed: '+str(result['http_observations'][-1]))
            wait_http(url,'/getclocktype')
            weather.wait_display(qmp)
            sequence=0
            for theme in themes:
                for case in cases:
                    target=folder/(theme+'-'+case['name']);target.mkdir()
                    result['current_action']={'theme':theme,'case':case['name']}
                    for path,payload in [('/updateCity',{'city':'Fixture,'+case['country']}),
                         ('/SetTimeModeValue',{'timemode':str(case['date_format'])}),
                         ('/settings',{'tempUnit':0,'hourFormat':case['hour12'],'mileDisplay':0,'timeSync':0,'nightmode':0}),
                         ('/setclocktype',{'clocktype':str(THEMES[theme])})]:
                        change(path,payload)
                    weather.wait_display(qmp)
                    if variant=='original':
                        # Finish the earlier city-triggered reinitialization.
                        # A late reply from it must not be attributed to ADV.
                        wait_for(lambda:weather.read_bytes(qmp,0x3fcc3ab9,1)[0] and
                                 weather.read_bytes(qmp,0x3fcc3ab8,1)[0],
                                 'Factory city-triggered synchronization did not finish')
                    country=next(row for row in regional.MANIFEST['countries'] if row['country']==case['country'])
                    factory.set_zone(country['legacy_tz'])
                    count=len(clock.ntp_trace(folder)['times'])
                    clock.service(qmp,case['boundary_utc']-10)
                    sequence+=1
                    server='cn.pool.ntp.org' if sequence%2 else '10.0.2.2'
                    change('/advancedset',{'ntp':server,'openweathermapKey':'disabled','clickCount':10})
                    if variant=='original':
                        # 0x4200e9ea saves the server but never clears 0x3fcc3ab9.
                        # After a valid year, only the separate city handler
                        # (0x4200f2c0) requests the timezone/SNTP reinitialization.
                        if sequence==1:
                            start=weather.virtual_seconds(qmp)
                            wait_for(lambda:weather.virtual_seconds(qmp)>=start+3,'Factory observation stalled')
                            saved=weather.read_bytes(qmp,0x3fcb7c22,65).split(b'\0')[0].decode('ascii')
                            initialized=bool(weather.read_bytes(qmp,0x3fcc3ab9,1)[0])
                            unchanged=len(clock.ntp_trace(folder)['times'])==count
                            result['factory_advanced_observation']={'saved_server':saved,'client_initialized':initialized,
                                'no_new_reply':unchanged,'observed_virtual_seconds':weather.virtual_seconds(qmp)-start}
                            if saved!=server or not initialized or not unchanged:
                                raise AssertionError('Factory advanced-settings behavior differs from its instructions')
                        change('/updateCity',{'city':'Fixture,'+case['country']})
                    wait_for(lambda:len(clock.ntp_trace(folder)['times'])>count,'No real NTP correction')
                    row={'theme':theme,**case,'samples':[]}
                    result['cases'].append(row)
                    before=capture(qmp,observer,target,variant,theme,case,settings,symbols,dump,assets,factory,'before',folder)
                    if not case['boundary_utc']-10<=before['packet_utc']<case['boundary_utc']:
                        raise AssertionError('Missed the pre-transition observation')
                    row['samples'].append(before)
                    reply_count=len(clock.ntp_trace(folder)['times'])
                    wait_for(lambda:packet_utc(qmp,folder)>=case['boundary_utc']+2,'Natural transition did not arrive')
                    after=capture(qmp,observer,target,variant,theme,case,settings,symbols,dump,assets,factory,'after',folder)
                    row['samples'].append(after)
                    if not case['boundary_utc']+2<=after['packet_utc']<=case['boundary_utc']+6:
                        raise AssertionError('Calendar/render update exceeded the declared observation bound')
                    if len(clock.ntp_trace(folder)['times'])!=reply_count:
                        raise AssertionError('Another NTP response intervened during the natural transition')
                    row['passed']=all(item['passed'] for item in row['samples'])
                    row['natural_transition_without_resync']=True
                    print('PASS natural calendar:',variant,theme,case['name'],flush=True)
            result['checks']={'all_pixels_checked':True,'natural_transitions':True,'hardware_breakpoints_only':True,
                              'real_ntp_packets':True,'no_guest_state_writes':True,
                              'settings_http_latency_bounded':all(row['guest_seconds']<=6
                                                                  for row in result['http_observations'])}
        result['passed']=all(row['passed'] for row in result['cases']) and all(result['checks'].values())
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        if observer:observer.close()
        try:
            if (folder/'session.json').exists():vm.control(folder,'stop');vm.ensure_stopped(folder)
        finally:
            fixture.close()
            if immutable is not None:
                flash=(folder/'flash.bin').read_bytes()
                result['checks']['executable_media_unchanged']=all(hashlib.sha256(flash[a:b]).hexdigest()==digest
                                                                 for (a,b),digest in zip(ranges,immutable))
                result['checks']['no_panic']=clean_uart(folder)
                result['passed'] &= all(result['checks'].values())
            vm.save_json(folder/'calendar-report.json',result)
    if not result['passed']:raise AssertionError('Calendar fixture checks failed: '+str(result['checks']))
    return result


def run_suite(options,output,themes=('classic','simple','dial'),names=None,variants=('original','reconstructed')):
    """Bind complete transition evidence to immutable code, TZif, helpers and test inputs."""
    global vm,http,wait_http,wait_for,clean_uart
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    weather.vm=vm;weather.wait_for=wait_for;scene.vm=vm
    sys.path.insert(0,str(ROOT/'Small_TV/qemu/parity'))
    from compare import seed_settings
    import compare
    previous_theme=compare.CURRENT_THEME
    previous_seed=vm.seed_clock_network
    output.mkdir(parents=True,exist_ok=True)
    app=verify_inputs()
    cases=requirements()
    if names:cases=[row for row in cases if row['name'] in names]
    if not cases:raise ValueError('No selected calendar cases')
    paths=[ROOT/'Small_TV/src/tests'/name for name in ('calendar_qemu.py','scene_qemu.py','gdb_observer.py',
        'frame_replay.py','calendar_oracle.py','machine_oracle.py','classic_oracle.py','weather_render_oracle.py',
        'jpeg_oracle.py','timezone_oracle.py','regional_qemu.py','time_qemu.py','weather_qemu.py','control_oracle.py','oracle-requirements.txt')]
    paths+=[ROOT/'Small_TV/qemu/parity/compare.py',regional.ZONES/'manifest.json',
            ROOT/'Small_TV/src/tools/prepare_timezones.py',Path(options.hardware_profile)]
    paths += [regional.ZONES/item['file'] for item in regional.MANIFEST['files']
              if item['zone'] in {row['zone'] for row in regional.MANIFEST['countries']
                                  if row['country'] in {case['country'] for case in cases}}]
    fingerprints=[{'file':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                  for path in paths]
    helper_folder=Path(vm.__file__).parent
    helpers={name:hashlib.sha256((helper_folder/name).read_bytes()).hexdigest() for name in
             ('small_tv_vm.py','small_tv_network.py','small_tv_web.py','small_tv_http_test.py','esp_board.py','esp_services.py', 'esp_elf.py', 'small_tv_display.py')}
    report={'passed':False,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'app_sha256':app,'source_sha256':json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())['source_sha256'],
            'native_elf_sha256':regional.settings_layout()['elf_sha256'],'flows':{},'requirements':cases,
            'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),'helper_sha256':helpers,
            'profile_sha256':vm.digest(Path(options.hardware_profile).read_bytes()),'test_inputs':fingerprints,'scope':__doc__}
    run=output/('vms-'+uuid.uuid4().hex[:12])
    vm.seed_clock_network=seed_settings;compare.CURRENT_THEME='simple'
    try:
        for variant in variants:report['flows'][variant]=exercise(options,run/variant,variant,themes,cases)
        if any(hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()!=row['sha256'] for row in fingerprints):
            raise AssertionError('Calendar test/reference input changed during execution')
        if verify_inputs()!=app or vm.digest(Path(options.qemu).read_bytes())!=report['qemu_sha256']:
            raise AssertionError('Calendar app/emulator changed during execution')
        if any(hashlib.sha256((helper_folder/name).read_bytes()).hexdigest()!=digest for name,digest in helpers.items()):
            raise AssertionError('Calendar VM helper changed during execution')
        report['passed']=True
    except Exception as error:
        report['error']=str(error)
        path=run/variant/'calendar-report.json'
        if path.exists():report['flows'][variant]=json.loads(path.read_text())
        raise
    finally:
        vm.seed_clock_network=previous_seed
        compare.CURRENT_THEME=previous_theme
        vm.save_json(output/'report.json',report)
    return report


def main():
    """Run selected preflights or the complete three-theme transport matrix, headless."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--themes',nargs='+',choices=tuple(THEMES),default=list(THEMES))
    parser.add_argument('--cases',nargs='+',choices=[row[0] for row in CASES])
    parser.add_argument('--variants',nargs='+',choices=('original','reconstructed'),default=['original','reconstructed'])
    args=parser.parse_args();sys.path.insert(0,str(args.qemu_root/'tools'))
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),display='none',http_base_port=0)
    run_suite(options,args.output,tuple(args.themes),args.cases,tuple(args.variants))


if __name__=='__main__':main()
