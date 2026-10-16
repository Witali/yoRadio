"""Compare completed real QEMU frames with immutable RV32 instruction replay.

Hardware breakpoints observe renderer entry/return. No guest instruction,
register, flag or RAM value is written. Real decoded media and all 57,600 pixels
are compared; time/animation differences and declared factory fixes stay explicit.
"""
from array import array
import argparse
from dataclasses import asdict,replace
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

from classic_oracle import Inputs
from control_oracle import verify_inputs
from frame_replay import SceneMachine,panel_rgb,normalized_checks,write_rgb_png
from gdb_observer import Observer
from machine_oracle import Machine,Panel,ROOT,SCRATCH,ELFFile,layout
from weather_qemu import virtual_seconds
import weather_qemu as weather


def native_symbols():
    """Locate the real native function/static addresses from this exact compiled ELF."""
    path=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf=ELFFile(stream)
        symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s['st_value']}
        previous=None
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name=die.attributes.get('DW_AT_name')
                if die.tag!='DW_TAG_subprogram' or not name or name.value!=b'factory_draw_dial':continue
                for child in die.iter_children():
                    name=child.attributes.get('DW_AT_name'); location=child.attributes.get('DW_AT_location')
                    if child.tag=='DW_TAG_variable' and name and name.value==b'previous' and location:
                        expression=bytes(location.value)
                        if len(expression)==5 and expression[0]==3:
                            previous=int.from_bytes(expression[1:],'little')
        if previous is None:raise AssertionError('Missing compiled dial history location')
        return symbols,previous


def rgb_panel(pixels):
    """Invert only the known RGB565 surface mapping and require lossless round trip."""
    if len(pixels)!=240*240*3:raise AssertionError('Unexpected scene size')
    values=[]
    for i in range(0,len(pixels),3):
        r,g,b=pixels[i:i+3]
        values.append((((r*31+127)//255)<<11)|(((g*63+127)//255)<<5)|((b*31+127)//255))
    panel=Panel(); panel.pixels=array('H',values)
    if panel_rgb(panel)!=pixels:raise AssertionError('QEMU image is not an exact RGB565 surface')
    return panel


def picture(qmp,folder,name):
    """Read the display while GDB has stopped the CPU at an instruction boundary."""
    path=folder/(name+'.png')
    vm.capture_png(qmp,path)
    pixels=vm.ppm_pixels(path.with_suffix('.ppm'))
    path.with_suffix('.ppm').unlink()
    return pixels


def cstring(observer,address,capacity):
    """Read a bounded synthetic string, never an arbitrary settings-sector dump."""
    raw=observer.memory(address,capacity)
    if b'\0' not in raw:raise AssertionError('Unterminated observed string')
    return raw.split(b'\0')[0].decode('ascii')


def inputs(observer,variant,theme,registers):
    """Translate the two actual ABIs into the same explicit rendering semantics."""
    if variant=='original':
        year,month,day,hour,minute,second,weekday=struct.unpack('<I6B',observer.memory(0x3fcbffc8,10))
        data=Inputs(year=year,month=month,day=day,hour=hour,minute=minute,second=second,weekday=weekday)
        if theme=='simple':
            data=replace(data,hour12=int.from_bytes(observer.memory(0x3fcb7b9c+0x170,4),'little'),
                         date_format=int.from_bytes(observer.memory(0x3fcb7b9c+0x17c,4),'little'))
        if theme=='classic':
            raw=0x3fcb7b9c
            integer=lambda offset:int.from_bytes(observer.memory(raw+offset,4),'little')
            numbers=struct.unpack('<3d2i',observer.memory(0x3fcc3a30,32))
            data=replace(data,city=cstring(observer,0x3fcb7c77,65),animation=integer(0x164),
                         fahrenheit=integer(0x16c),hour12=integer(0x170),miles=integer(0x174),
                         date_format=integer(0x17c),valid=bool(observer.memory(0x3fcc39d7,1)[0]),
                         minimum=numbers[0],maximum=numbers[1],wind=numbers[2],humidity=numbers[3],temperature=numbers[4],
                         main=cstring(observer,0x3fcbff6c,20),description=cstring(observer,0x3fcbff80,20),
                         direction=cstring(observer,0x3fcbff94,20),step=observer.memory(0x3fcc3a25,1)[0])
            if data.valid and not observer.memory(0x3fcc39f7,1)[0]:
                # The factory counter points to the NEXT label between events.
                # Translate it to the displayed semantic step without changing
                # either running program or inferring text from screenshot pixels.
                data=replace(data,step=(data.step-1)%10)
            if [integer(offset) for offset in (0x184,0x188,0x18c)] != [0xf800,0xffe0,0xffff]:
                raise AssertionError('Unexpected synthetic colors')
            pointer=int.from_bytes(observer.memory(0x3fcc3aa8,4),'little')
            if pointer:
                manifest=json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
                code=next(row['code'] for row in manifest['weather'] if int(row['flash_offset'],16)==pointer)
                data=replace(data,icon=code,retained_icon=not data.valid)
    else:
        tm_address=registers['a0'] if theme=='dial' else registers['a1']
        second,minute,hour,day,month,year,weekday,_,_=struct.unpack('<9i',observer.memory(tm_address,36))
        data=Inputs(year=year+1900,month=month+1,day=day,hour=hour,minute=minute,second=second,weekday=weekday)
        if theme=='simple':
            size,fields=layout('tv_settings_t'); raw=observer.memory(registers['a0'],size)
            data=replace(data,hour12=raw[fields['hour12']],date_format=raw[fields['date_format']])
        if theme=='classic':
            size,fields=layout('tv_settings_t'); raw=observer.memory(registers['a0'],size)
            text=lambda name:raw[fields[name]:].split(b'\0')[0].decode('ascii')
            weather_size,weather_fields=layout('weather_snapshot_t')
            cache=observer.memory(registers['a2'],weather_size)
            weather_text=lambda name:cache[weather_fields[name]:].split(b'\0')[0].decode('ascii')
            number=lambda name:struct.unpack_from('<d',cache,weather_fields[name])[0]
            temperature=number('temperature_c')
            if temperature!=int(temperature):
                raise AssertionError('Observed temperature violates the factory integer-Celsius contract')
            data=replace(data,city=text('city'),animation=raw[fields['animation']],
                         fahrenheit=raw[fields['fahrenheit']],hour12=raw[fields['hour12']],miles=raw[fields['miles']],
                         date_format=raw[fields['date_format']],valid=bool(cache[weather_fields['valid']]),
                         minimum=number('temperature_min_c'),maximum=number('temperature_max_c'),wind=number('wind_mps'),
                         temperature=int(temperature),humidity=struct.unpack_from('<i',cache,weather_fields['humidity'])[0],
                         main=weather_text('main'),description=weather_text('description'),direction=weather_text('wind_direction'),
                         generation=struct.unpack_from('<I',cache,weather_fields['generation'])[0],step=registers['a3'])
            data=replace(data,icon=weather_text('icon') or '01d')
            if struct.unpack_from('<3H',raw,fields['colors'])!=(0xf800,0xffe0,0xffff):
                raise AssertionError('Unexpected synthetic colors')
    return data


def seed_time(machine,data):
    """Supply the recorded semantic clock to the isolated instruction replay only."""
    machine.seed(data.hour,data.minute,data.second,data.weekday,data.date_format,data.hour12)
    if machine.is_factory:
        machine.cpu.mem_write(0x3fcbffc8,struct.pack('<I6B',data.year,data.month,data.day,data.hour,data.minute,data.second,data.weekday))
    else:
        yday=dt.date(data.year,data.month,data.day).timetuple().tm_yday-1
        machine.cpu.mem_write(SCRATCH+0x200,struct.pack('<9i',data.second,data.minute,data.hour,data.day,
                              data.month-1,data.year-1900,data.weekday,yday,0)+bytes(8))


def backlight(observer):
    """Read the actual LEDC channel/timer and GPIO18 routing, matching QEMU's device math."""
    registers=observer.memory(0x60019000,0xc0)
    conf,duty=struct.unpack_from('<I',registers,0)[0],struct.unpack_from('<I',registers,8)[0]>>4
    bits=struct.unpack_from('<I',registers,0xa0+(conf&3)*8)[0]&15
    period=1<<bits
    level=min(duty,period)*1000//period if conf&4 else 1000 if conf&8 else 0
    routing=int.from_bytes(observer.memory(0x60004000+0x554+18*4,4),'little')
    if not int.from_bytes(observer.memory(0x60004020,4),'little')&(1<<18):
        raise AssertionError('Backlight GPIO output is disabled')
    if routing&255!=45:raise AssertionError('Unexpected backlight GPIO signal')
    if routing&256:level=1000-level
    return {'brightness':1000-level,'high_duty':duty,'resolution_bits':bits,'gpio_routing':routing}


def capture(options,output,theme,variant,symbols,previous,samples):
    """Compare initial and incremental completed frames; always shut down the owned VM."""
    from compare import seed_settings
    import compare
    scene=theme
    theme='classic' if scene.startswith('classic') else 'dial'
    compare.CURRENT_THEME=theme
    previous_seed=vm.seed_clock_network
    vm.seed_clock_network=seed_settings
    fixture=None
    if scene=='classic-weather':
        weather.vm=vm
        fixture=weather.WeatherFixture(['Shenzhen,CN'])
        fixture.set_response(200)
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1',0)); port=reservation.getsockname()[1]
    options=SimpleNamespace(**{**vars(options),'firmware':variant,'network':'clock','persistent':False,
                                'paused':True,'gdb_port':port,'service_port':fixture.port if fixture else None})
    session=observer=None
    immutable_before=None
    output.mkdir(parents=True,exist_ok=True)
    result={'passed':False,'sources':{},'samples':[],'checks':{}}
    try:
        session,prepared=vm.launch(options,output)
        result['sources']=prepared['sources']
        flash=(output/'flash.bin').read_bytes()
        immutable_ranges=((0,0x9000),(0x10000,0x3e7000))
        immutable_before=[hashlib.sha256(flash[a:b]).hexdigest() for a,b in immutable_ranges]
        dump=(ROOT/'Small_TV/full-flash.bin').read_bytes()
        assets=json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
        machine=SceneMachine('factory' if variant=='original' else 'native',dump,assets) if theme=='classic' else Machine('factory' if variant=='original' else 'native')
        observer=Observer(port)
        entry=({'classic':0x4200b738,'dial':0x4200a156}[theme] if variant=='original' else symbols['factory_draw_'+theme])
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            qmp.execute('qom-set',path='/machine/wifi',property='ntp-unix-seconds',
                        value=int(dt.datetime(2026,10,13,12,34,30,tzinfo=dt.timezone.utc).timestamp()))
            for index in range(samples+1):
                mature=index==samples
                if mature:
                    observer.resume()
                    deadline=time.monotonic()+180
                    while virtual_seconds(qmp)<40:
                        if time.monotonic()>deadline:raise TimeoutError('Mature scene did not reach 40 guest seconds')
                        time.sleep(.2)
                    observer.interrupt()
                observer.breakpoint(entry)
                observer.continue_to(entry)
                code=observer.memory(entry,4)
                registers={name:observer.register(number) for name,number in
                           [('ra',1),('a0',10),('a1',11),('a2',12),('a3',13),('a4',14),('a5',15),('a6',16)]}
                data=inputs(observer,variant,theme,registers)
                if fixture and not data.valid:
                    raise AssertionError('Weather scene did not receive its real HTTP fixture')
                observed_virtual_seconds=virtual_seconds(qmp)
                before=picture(qmp,output,f'{index}-before')
                old_state={}
                if theme=='dial' and index:
                    addresses=[(0x3fcb7d78,48),(0x3fcc3a00,24)] if variant=='original' else [(previous,12)]
                    old_state={address:observer.memory(address,length) for address,length in addresses}
                cursor=(observer.memory(0x3fcc3a24,1)[0] if variant=='original' else registers['a4']) if theme=='classic' else 0
                observer.breakpoint(entry,False)
                if observer.memory(entry,4)!=code:raise AssertionError('Hardware breakpoint changed code bytes')
                observer.breakpoint(registers['ra'])
                return_code=observer.memory(registers['ra'],4)
                observer.continue_to(registers['ra'])
                observer.breakpoint(registers['ra'],False)
                if observer.memory(registers['ra'],4)!=return_code:
                    raise AssertionError('Return breakpoint changed code bytes')
                actual=picture(qmp,output,f'{index}-complete')
                light=backlight(observer)
                if observer.register(32)!=registers['ra']:raise AssertionError('Capture advanced the stopped CPU')
                if mature:
                    machine=(SceneMachine('factory' if variant=='original' else 'native',dump,assets)
                             if theme=='classic' else Machine('factory' if variant=='original' else 'native'))
                    machine.panel=Panel()
                else:
                    machine.panel=rgb_panel(before)
                if theme=='classic':
                    reset=index==0 or mature
                    if variant=='reconstructed' and bool(registers['a5'])!=(index==0):
                        raise AssertionError('Unexpected native reset state')
                    machine.render(data,reset=reset,cursor=cursor,force_status=bool(registers['a6']) if variant=='reconstructed' else False)
                else:
                    seed_time(machine,data)
                    if mature:
                        machine.dial(reset=True)
                        machine.dial(reset=False) # A completed steady frame includes the center cap.
                    else:
                        for address,raw in old_state.items():machine.cpu.mem_write(address,raw)
                        machine.dial(reset=index==0)
                expected=panel_rgb(machine.panel,light['brightness'])
                different=[i for i in range(57600) if actual[i*3:i*3+3]!=expected[i*3:i*3+3]]
                row={'inputs':asdict(data),'frame_cursor':cursor,'initial':index==0,'different_pixels':len(different),
                     'qemu_rgb_sha256':hashlib.sha256(actual).hexdigest(),'replayed_rgb_sha256':hashlib.sha256(expected).hexdigest(),
                     'entry':hex(entry),'return':hex(registers['ra']),'code_unchanged':True,'passed':not different}
                row['backlight']=light
                row['mature']=mature
                row['virtual_seconds']=observed_virtual_seconds
                row['reference']='clean-full-frame' if mature else 'recorded-entry-state'
                row['digital_requested_brightness_applied']=theme!='classic' or light['brightness']==1000
                if different:
                    row['first_differences']=[[i%240,i//240] for i in different[:20]]
                    write_rgb_png(output/f'{index}-replayed.png',expected)
                result['samples'].append(row)
                print('Completed frame:',scene,variant,index,'different pixels',len(different),flush=True)
                if different:raise AssertionError('Completed QEMU frame differs from actual instruction replay')
                if not row['digital_requested_brightness_applied']:
                    raise AssertionError('First digital frame still uses startup brightness')
                if variant=='original' and theme=='dial':entry=0x42009cf4
            result['checks']={'all_pixels_checked':True,'hardware_breakpoints_only':True,'no_guest_state_writes':True}
            if fixture:
                rows=fixture.rows()
                if not rows or any(not row['synthetic_location'] or not row['synthetic_key'] for row in rows):
                    raise AssertionError('Weather scene used unexpected service inputs')
                result['checks']['real_weather_http']=True
        result['passed']=all(row['passed'] for row in result['samples'])
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        try:
            if observer:observer.close()
            if (output/'session.json').exists():
                vm.control(output,'stop');vm.ensure_stopped(output)
        finally:
            if fixture:fixture.close()
            vm.seed_clock_network=previous_seed
            if immutable_before is not None:
                flash=(output/'flash.bin').read_bytes()
                result['checks']['executable_media_unchanged']=all(
                    hashlib.sha256(flash[a:b]).hexdigest()==digest
                    for (a,b),digest in zip(immutable_ranges,immutable_before))
                from small_tv_http_test import clean_uart
                result['checks']['no_panic']=clean_uart(output)
                result['passed'] &= all(result['checks'].values())
            vm.save_json(output/'scene-report.json',result)
    if not result['passed']:raise AssertionError('Completed scene integrity/panic check failed')
    return result


def run_suite(options,output,samples=3,themes=('classic','classic-weather','dial'),variants=('original','reconstructed')):
    """Require every completed frame to match this exact compiled app and original image."""
    global vm
    import small_tv_vm as vm
    sys.path.insert(0,str(ROOT/'Small_TV/qemu/parity'))
    app_sha=verify_inputs()
    symbols,previous=native_symbols()
    output.mkdir(parents=True,exist_ok=True)
    report={'passed':False,'app_sha256':app_sha,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'native_elf_sha256':hashlib.sha256((ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()).hexdigest(),
            'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),'scenes':{},'scope':__doc__}
    paths=[ROOT/'Small_TV/src/tests'/name for name in
           ('scene_qemu.py','gdb_observer.py','frame_replay.py','machine_oracle.py','classic_oracle.py',
            'jpeg_oracle.py','weather_render_oracle.py','weather_qemu.py')]
    paths.append(ROOT/'Small_TV/qemu/parity/compare.py')
    report['test_inputs']=[{'file':str(path.relative_to(ROOT)).replace('\\','/'),
                           'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
    run=output/('vms-'+uuid.uuid4().hex[:12])
    try:
        for theme in themes:
            report['scenes'][theme]={}
            for variant in variants:
                report['scenes'][theme][variant]=capture(options,run/f'{theme}-{variant}',theme,variant,symbols,previous,samples)
                if not report['scenes'][theme][variant]['passed']:
                    raise AssertionError('Completed scene flow did not pass')
        report['normalized']=normalized_checks((ROOT/'Small_TV/full-flash.bin').read_bytes(),
                    json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8')))
        if not report['normalized']['passed']:raise AssertionError('Normalized full-scene comparison failed')
        for row in report['test_inputs']:
            if hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()!=row['sha256']:
                raise AssertionError('Scene test input changed during execution')
        if verify_inputs()!=app_sha or vm.digest(Path(options.qemu).read_bytes())!=report['qemu_sha256']:
            raise AssertionError('Firmware or emulator changed during scene execution')
        report['passed']=True
    except Exception as error:
        report['error']=str(error)
        failed=run/f'{theme}-{variant}'/'scene-report.json'
        if failed.exists():report['scenes'][theme][variant]=json.loads(failed.read_text(encoding='utf-8'))
        raise
    finally:vm.save_json(output/'report.json',report)
    return report


def main():
    """Use isolated loopback ports, disposable flash and immutable production programs."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--samples',type=int,default=3)
    parser.add_argument('--themes',nargs='+',choices=('classic','classic-weather','dial'),default=['classic','classic-weather','dial'])
    parser.add_argument('--variants',nargs='+',choices=('original','reconstructed'),default=['original','reconstructed'])
    args=parser.parse_args()
    if not 2<=args.samples<=8:parser.error('Use 2..8 completed frames per scene')
    sys.path.insert(0,str(args.qemu_root/'tools'))
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),display='none',http_base_port=0)
    run_suite(options,args.output,args.samples,args.themes,args.variants)


if __name__=='__main__':main()
