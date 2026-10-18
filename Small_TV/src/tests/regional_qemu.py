"""Verify regional keys through actual HTTP, raw flash, weather and clock rendering.

Only synthetic settings and external HTTP/NTP responses are supplied. All guest
code is immutable; QMP observes identified fields and never patches guest memory.
The unchanged factory raw ABI and the native NVS ABI are deliberately separate.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
from types import SimpleNamespace
import uuid
from zoneinfo import ZoneInfo

import time_qemu as clock
import weather_qemu as weather
from weather_qemu import ROOT, ELFFile, read_bytes
from machine_oracle import layout
from raw_flash_observer import read_stored_key, persistence_complete

RAW = 0x3e7000
COUNTRY = 0xc7
EPOCH = int(dt.datetime(2026, 1, 1, 6, 14, 7, tzinfo=dt.timezone.utc).timestamp())
ZONES = ROOT/'Small_TV/src/resources/timezones'
MANIFEST = json.loads((ZONES/'manifest.json').read_text())


def zone(key):
    """Use pinned independent TZif data, including the documented unknown-key fallback."""
    name = next((row['zone'] for row in MANIFEST['countries'] if row['country'] == key), 'Europe/London')
    row = next(row for row in MANIFEST['files'] if row['zone'] == name)
    with (ZONES/row['file']).open('rb') as stream:
        return ZoneInfo.from_file(stream)


def settings_layout():
    """Read only the compiled current-settings symbol and its real DWARF field offsets."""
    path = ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
        symbol = next(s for s in symbols if s.name == 'current_settings')
        dirty_symbols = [s for s in symbols if s.name == 'dirty' and s['st_size'] == 1]
        if len(dirty_symbols) != 1:
            raise AssertionError('Missing or ambiguous compiled settings dirty flag')
        size, fields = layout('tv_settings_t')
        if size != symbol['st_size']:
            raise AssertionError('Compiled settings symbol/type disagree')
        return {'address': symbol['st_value'], 'size': size, 'fields': fields,
                'dirty_address': dirty_symbols[0]['st_value'],
                'elf_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def current_key(qmp, variant, settings):
    """Observe the entire factory/native key, not just the first two country letters."""
    address = 0x3fcb7c63 if variant == 'original' else settings['address']+settings['fields']['country']
    return read_bytes(qmp, address, 20).split(b'\0')[0].decode('ascii')


def stored_key(folder):
    """Read the public synthetic key from the disposable VM's original raw sector."""
    return read_stored_key(folder/'flash.bin',RAW+COUNTRY)


def stored_key_complete(qmp, folder, variant, settings, key):
    """Do not cold-stop a native VM between erase and its final page program."""
    return persistence_complete(
        lambda: stored_key(folder), key,
        (lambda: read_bytes(qmp,settings['dirty_address'],1))
        if variant == 'reconstructed' else None)



def calendar_observation(qmp, folder, variant, clocks, key):
    """Require the displayed calendar to match NTP packets and independent regional rules.

    A renderer may lag the emulated timer by a few seconds. Compare complete
    calendars in that bounded interval instead of ignoring minutes or dates.
    """
    qmp.execute('stop')
    try:
        state = clock.snapshot(qmp, variant, clocks)
        virtual = int.from_bytes(read_bytes(qmp, 0x6004d000, 4), 'little')
        traces = clock.ntp_trace(folder)['times']
        if not traces:
            return None
        latest = traces[-1]
        utc = int(latest['epoch']+(virtual-latest['virtual_us'])/1e6)
        actual = tuple(state[name] for name in ('year','month','day','hour','minute','second','weekday'))
        candidates,iana_candidates = [],[]
        # Pinned January fixture: stock Newlib supplies US DST recurrence to
        # these rule-less Australian strings, so it incorrectly uses standard
        # time in southern summer. Preserve only these already proven literal
        # differences; the reconstructed image must match actual IANA rules.
        literal_offsets = {'AU-C':34200,'AU-E':36000}
        local_zone = (dt.timezone(dt.timedelta(seconds=literal_offsets[key]))
                      if variant=='original' and key in literal_offsets else zone(key))
        for lag in range(-1, 4):
            local = dt.datetime.fromtimestamp(utc-lag, local_zone)
            candidates.append((local.year,local.month,local.day,local.hour,local.minute,local.second,
                               (local.weekday()+1)%7))
            reference = dt.datetime.fromtimestamp(utc-lag,zone(key))
            iana_candidates.append((reference.year,reference.month,reference.day,reference.hour,
                                    reference.minute,reference.second,(reference.weekday()+1)%7))
        return {'passed': state['synced'] and actual in candidates, 'key': key,
                'state': state, 'packet_utc_seconds': utc, 'expected_calendars': candidates,
                'iana_calendars':iana_candidates,'matches_iana':actual in iana_candidates,
                'declared_factory_implicit_dst':variant=='original' and key in literal_offsets}
    finally:
        qmp.execute('cont')


def observe(qmp, folder, variant, clocks, settings, key):
    """Wait for the actual renderer and require exact independent date-band pixels."""
    deadline = time.monotonic()+45
    last = None
    while time.monotonic() < deadline:
        last = calendar_observation(qmp,folder,variant,clocks,key)
        if current_key(qmp,variant,settings) == key and last and last['passed']:
            date = last['state']
            label = f"{date['year']}/{date['month']}/{date['day']}"
            last['pixels'] = clock.date_capture(qmp,folder,variant,clocks,label)
            return last
        time.sleep(.2)
    vm.save_json(folder/'failed-regional-observation.json',last)
    raise AssertionError('Regional key/calendar not applied: '+key+'; '+str(last))


def exercise(options, folder, settings, clocks, cache):
    """Run raw import, every recovered regional suffix, HTTP persistence and a cold boot."""
    variant = options.firmware
    fixture = weather.WeatherFixture(['Perth,AU-W']+['Fixture,'+row['country'] for row in MANIFEST['countries']])
    fixture.set_response(200)
    options = SimpleNamespace(**{**vars(options),'network':'clock','service_port':fixture.port,
                                 'persistent':True,'paused':True})
    prepared = vm.prepare(options,folder)
    flash = folder/'flash.bin'
    data = bytearray(flash.read_bytes())
    data[RAW+COUNTRY:RAW+COUNTRY+20] = b'AU-W'.ljust(20,b'\0')
    data[RAW+0xdb:RAW+0xdb+65] = b'Perth'.ljust(65,b'\0')
    struct.pack_into('<I',data,RAW+0x168,1)
    struct.pack_into('<I',data,RAW+0x17c,2)
    flash.write_bytes(data)
    immutable = [(0,0x9000),(0x10000,RAW)]
    before = [hashlib.sha256(data[a:b]).hexdigest() for a,b in immutable]
    session = None
    result = {'passed':False,'sources':prepared['sources'],'cases':[],'checks':{}}
    try:
        session,_ = vm.launch(options,folder)
        url = session['web_urls']['station']
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            clock.service(qmp,EPOCH,0,False)
            qmp.execute('cont')
            wait_http(url,'/getclocktype',expected=b'1')
            weather.wait_display(qmp)
            result['raw_import'] = observe(qmp,folder,variant,clocks,settings,'AU-W')
            regional = [row['country'] for row in MANIFEST['countries'] if '-' in row['country']]
            # End with US-H so cold boot also proves the previous day's date.
            regional = [key for key in regional if key != 'US-H']+['US-H']
            for key in regional:
                status,_ = http(url,'/updateCity',{'city':'Fixture,'+key},origin=url)
                if status != 200:
                    raise AssertionError('Regional HTTP rejected '+key+': '+str(status))
                if variant == 'original':
                    # Stock's periodic minute flag is independent of SNTP jumps.
                    # Earlier failed same-minute observations retain that defect.
                    # Re-enter through the actual theme API to verify the stock
                    # regional pixels without patching its flags or program.
                    status,_ = http(url,'/setclocktype',{'clocktype':'3'},origin=url)
                    if status != 200:
                        raise AssertionError('Factory dial theme rejected')
                    weather.wait_display(qmp)
                    status,_ = http(url,'/setclocktype',{'clocktype':'1'},origin=url)
                    if status != 200:
                        raise AssertionError('Factory simple theme rejected')
                row = observe(qmp,folder,variant,clocks,settings,key)
                row['factory_theme_reentry'] = variant == 'original'
                if variant == 'reconstructed':
                    offset = cache['fields']['country']
                    wait_for(lambda: read_bytes(qmp,cache['address']+offset,20).split(b'\0')[0] == key.encode(),
                             'Weather cache lost regional suffix')
                    row['weather_key_preserved'] = True
                wait_for(lambda:stored_key_complete(qmp,folder,variant,settings,key),'Raw persistence lost regional suffix')
                row['raw_persistence'] = True
                result['cases'].append(row)
                print('PASS regional key:',variant,key,flush=True)
            if variant == 'reconstructed':
                # Both buffers reach their legal byte limit; the full-width comma
                # must be decoded as three UTF-8 bytes, never six JSON escape bytes.
                city, key = 'C'*64, 'ZZ-ABCDEFGHIJKLMNOP'
                fixture.locations.add(city+','+key)
                status,_ = http(url,'/updateCity',{'city':city+'\uff0c'+key},origin=url,ensure_ascii=False)
                if status != 200:
                    raise AssertionError('Maximum-length regional HTTP input rejected')
                result['maximum_input'] = observe(qmp,folder,variant,clocks,settings,key)
                wait_for(lambda:stored_key_complete(qmp,folder,variant,settings,key),'Maximum-length key was not persisted')
                with flash.open('rb') as stream:
                    stream.seek(RAW+0xdb)
                    if stream.read(65) != city.encode()+b'\0':
                        raise AssertionError('Maximum key damaged the adjacent raw city field')
                for invalid in ('US-','US-H&x','US-ABCDEFGHIJKLMNOPQ'):
                    status,_ = http(url,'/updateCity',{'city':'Fixture,'+invalid},origin=url)
                    if status != 400 or current_key(qmp,variant,settings) != key:
                        raise AssertionError('Invalid region modified the previous setting')
                result['invalid_inputs_rejected'] = 3
                status,_ = http(url,'/updateCity',{'city':'Fixture,US-H'},origin=url)
                if status != 200:
                    raise AssertionError('Region restoration before cold boot failed')
                observe(qmp,folder,variant,clocks,settings,'US-H')
                wait_for(lambda:stored_key_complete(qmp,folder,variant,settings,'US-H'),'Cold-boot key was not persisted')
        vm.control(folder,'stop')
        vm.ensure_stopped(folder)
        session,_ = vm.launch(options,folder)
        url = session['web_urls']['station']
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            clock.service(qmp,EPOCH,0,False)
            qmp.execute('cont')
            wait_http(url,'/getclocktype',expected=b'1')
            weather.wait_display(qmp)
            result['cold_boot'] = observe(qmp,folder,variant,clocks,settings,'US-H')
        result['checks'] = {'all_regional_keys':len(result['cases'])==len(regional),
                            'raw_import':True,'cold_boot_persistence':True,'no_panic':clean_uart(folder)}
        result['passed'] = all(result['checks'].values())
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        try:
            if session:
                vm.control(folder,'stop')
                vm.ensure_stopped(folder)
        finally:
            fixture.close()
        after = flash.read_bytes()
        result['checks']['executable_media_unchanged'] = all(hashlib.sha256(after[a:b]).hexdigest()==sha
                                                            for (a,b),sha in zip(immutable,before))
        result['passed'] &= result['checks']['executable_media_unchanged']
        vm.save_json(folder/'regional-report.json',result)
    if not result['passed']:
        raise AssertionError('Regional flow failed')
    return result


def legacy_nvs(options, folder, settings):
    """Migrate a real SDK-generated version 1 NVS blob, then boot using only version 2 NVS."""
    options = SimpleNamespace(**{**vars(options),'firmware':'reconstructed','network':'clock',
                                 'persistent':True,'paused':False})
    prepared = vm.prepare(options,folder)
    profile = json.loads(Path(options.hardware_profile).read_text())
    ssid = profile['network']['station_ssid']
    blob = bytearray(344)
    struct.pack_into('<I',blob,0,1)
    strings = {4:ssid,37:'',102:'LegacyFixture',167:'GB',170:'10.0.2.4',235:''}
    for offset,value in strings.items():
        blob[offset:offset+len(value)+1] = value.encode()+b'\0'
    struct.pack_into('<5H',blob,300,730,180,0x1234,0x4567,0x89ab)
    blob[310:324] = bytes([1,4,1,21,7,19,1,1,0,1,1,9,0,0])
    struct.pack_into('<5I',blob,324,111,222,333,444,555)
    (folder/'legacy-configuration.bin').write_bytes(blob)
    csv_path = folder/'legacy-nvs.csv'
    with csv_path.open('w',newline='',encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerows([['key','type','encoding','value'],['small_tv','namespace','',''],
                          ['configuration','file','binary',str((folder/'legacy-configuration.bin').resolve())]])
    generator = ROOT/'.idf/v6.1-9a97f6c54ec6/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py'
    subprocess.run([sys.executable,str(generator),'generate',str(csv_path),str(folder/'legacy-nvs.bin'),'0x6000'],
                   check=True,capture_output=True,text=True)
    data = bytearray((folder/'flash.bin').read_bytes())
    partition = (folder/'legacy-nvs.bin').read_bytes()
    if len(partition) != 0x6000:
        raise AssertionError('Generated NVS partition has a different size')
    data[0x9000:0xf000] = partition
    data[RAW:RAW+4096] = b'\xff'*4096
    (folder/'flash.bin').write_bytes(data)
    immutable = [(0,0x9000),(0x10000,RAW)]
    before = [vm.digest(data[a:b]) for a,b in immutable]
    expected = {'version':2,'ssid':ssid,'password':'','city':'LegacyFixture','country':'GB',
                'ntp':'10.0.2.4','weather_key':'','day_level':730,'night_level':180,
                'colors':[0x1234,0x4567,0x89ab],'theme':1,'animation':4,'date_format':1,
                'night_start':21,'night_stop':7,'photo_seconds':19,'fahrenheit':1,'hour12':1,
                'miles':0,'browser_time':1,'night_mode':1,'click_count':9,'photo_mask':0,
                'wifi_mode':1,'photo_size':[111,222,333,444,555]}
    result = {'passed':False,'sources':prepared['sources'],'legacy_blob_bytes':len(blob),
              'legacy_blob_sha256':vm.digest(blob),'nvs_generator_sha256':vm.digest(generator.read_bytes()),
              'stages':{},'checks':{}}
    session = None
    try:
        for stage in ('migrate_v1','load_v2_without_raw'):
            session,_ = vm.launch(options,folder)
            wait_http(session['web_urls']['station'],'/getclocktype',expected=b'1')
            with vm.QMP(session['qmp_port'],session['name']) as qmp:
                raw = read_bytes(qmp,settings['address'],settings['size'])
                actual = {}
                for name,value in expected.items():
                    offset = settings['fields'][name]
                    if isinstance(value,str):
                        actual[name] = raw[offset:].split(b'\0')[0].decode('ascii')
                    elif isinstance(value,list):
                        fmt = '<3H' if name=='colors' else '<5I'
                        actual[name] = list(struct.unpack_from(fmt,raw,offset))
                    else:
                        fmt = '<I' if name=='version' else '<H' if name.endswith('_level') else '<B'
                        actual[name] = struct.unpack_from(fmt,raw,offset)[0]
                if actual != expected:
                    raise AssertionError('NVS migration changed fields: '+str(actual))
                result['stages'][stage] = {'all_fields_equal':True,'settings_version':actual['version']}
                if stage == 'migrate_v1':
                    wait_for(lambda:stored_key_complete(qmp,folder,'reconstructed',settings,'GB'),'Migrated settings were not persisted')
                else:
                    # A repeated v1 migration would dirty settings and recreate
                    # this raw sector. A clean v2 read leaves erased bytes intact.
                    weather.wait_display(qmp)
                    with (folder/'flash.bin').open('rb') as stream:
                        stream.seek(RAW)
                        if stream.read(4096) != b'\xff'*4096:
                            raise AssertionError('Version 2 NVS was unnecessarily migrated again')
            vm.control(folder,'stop'); vm.ensure_stopped(folder); session = None
            if not clean_uart(folder):
                raise AssertionError('Panic during NVS '+stage)
            result['stages'][stage]['no_panic'] = True
            if stage == 'migrate_v1':
                data = bytearray((folder/'flash.bin').read_bytes())
                data[RAW:RAW+4096] = b'\xff'*4096
                (folder/'flash.bin').write_bytes(data)
        result['checks'] = {'all_old_fields_preserved':True,'old_padding_mode_normalized':True,
                            'new_nvs_cold_boot_without_raw':True,'no_panic':clean_uart(folder)}
        result['passed'] = all(result['checks'].values())
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        if session:
            vm.control(folder,'stop'); vm.ensure_stopped(folder)
        after = (folder/'flash.bin').read_bytes()
        result['checks']['executable_media_unchanged'] = all(vm.digest(after[a:b])==sha
                                                            for (a,b),sha in zip(immutable,before))
        result['passed'] &= result['checks']['executable_media_unchanged']
        vm.save_json(folder/'nvs-migration-report.json',result)
    if not result['passed']:
        raise AssertionError('NVS migration/fallback boot failed')
    return result


def run_suite(options, output, variants=('original','reconstructed')):
    """Bind regional transport/persistence/calendar observations to actual image hashes."""
    global vm,http,wait_http,wait_for,clean_uart
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    clock.vm = weather.vm = vm
    clock.http = weather.http = http
    clock.wait_for = weather.wait_for = wait_for
    output.mkdir(parents=True,exist_ok=True)
    settings,clocks,cache = settings_layout(),clock.clock_layout(),weather.native_layout()
    report = {'passed':False,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'flows':{},'settings_layout':settings,'clock_layout':clocks,'weather_layout':cache,
              'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),'variants':list(variants),'scope':__doc__}
    run = output/('vms-'+uuid.uuid4().hex[:12])
    try:
        for variant in variants:
            options.firmware = variant
            report['flows'][variant] = exercise(options,run/variant,settings,clocks,cache)
            print('PASS real regional HTTP/raw/calendar/cold boot:',variant,flush=True)
        if not variants or 'reconstructed' in variants:
            report['nvs_migration'] = legacy_nvs(options,run/'native-nvs',settings)
            print('PASS real NVS v1 migration and v2 fallback boot',flush=True)
        report['passed'] = (all(row['passed'] for row in report['flows'].values()) and
                            report.get('nvs_migration',{'passed':True})['passed'])
    except Exception as error:
        report['error'] = str(error)
        path = run/getattr(options,'firmware','reconstructed')/'regional-report.json'
        if path.exists():
            report['flows'][options.firmware] = json.loads(path.read_text())
        if (run/'native-nvs/nvs-migration-report.json').exists():
            report['nvs_migration'] = json.loads((run/'native-nvs/nvs-migration-report.json').read_text())
        raise
    finally:
        vm.save_json(output/'report.json',report)
    return report


def main():
    """Run against the archived images; never use a physical serial or flash tool."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--firmware',choices=('original','reconstructed'))
    parser.add_argument('--nvs-only',action='store_true',help='Run only the actual SDK NVS migration/fallback boots')
    args = parser.parse_args()
    sys.path.insert(0,str(args.qemu_root/'tools'))
    options = SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),
        display='none',paused=True,gdb_port=0,http_base_port=0)
    variants = () if args.nvs_only else (args.firmware,) if args.firmware else ('original','reconstructed')
    run_suite(options,args.output,variants)


if __name__ == '__main__':
    main()
