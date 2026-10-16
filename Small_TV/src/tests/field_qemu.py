"""Check actual HTTP field updates, clipped scrolling and icon recovery in QEMU."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
from types import SimpleNamespace
import uuid

import weather_qemu as weather
from weather_qemu import ROOT, ELFFile, read_bytes, region

LONG_CITY = 'ABCDEFGHIJKLMNOPQRS'
FONT_FOLDER = ROOT / 'Small_TV/src/resources/factory'
FONT_META = next(row for row in json.loads((FONT_FOLDER/'manifest.json').read_text(encoding='utf-8'))['tables'] if row['name']=='ascii24')
FONT = (FONT_FOLDER/'ascii24.bin').read_bytes()
if hashlib.sha256(FONT).hexdigest()!=FONT_META['sha256']:
    raise AssertionError('Factory font changed')
ASSETS = json.loads((ROOT/'Small_TV/assets/manifest.json').read_text(encoding='utf-8'))
PACK = (ROOT/'firmware/development/small-tv-esp32c2-reconstructed/assets.bin').read_bytes()
GUARDS = [[0,34,180,1],[0,64,180,1],[160,82,80,1],[160,107,80,1]]


def rgb(color):
    """Use the installed QEMU ST7789 surface's integer RGB565 expansion."""
    r,g,b = (color>>11)&31,(color>>5)&63,color&31
    return bytes([r*255//31,g*255//63,b*255//31])


def text_pixels(text,width,offset,color):
    """Build an independent clipped ASCII window from immutable factory font rows."""
    start = (width-len(text)*12)//2 if len(text)*12<=width else -offset
    result=bytearray(width*24*3)
    ink=rgb(color)
    for y in range(24):
        for x in range(width):
            source=x-start
            if source<0 or source>=len(text)*12:continue
            character=ord(text[source//12])
            if not 32<=character<128:raise AssertionError('Only synthetic ASCII labels are allowed')
            byte=FONT[(character-32)*48+y*2+(source%12)//8]
            if byte&(1<<(source%12%8)):
                result[(y*width+x)*3:(y*width+x+1)*3]=ink
    return bytes(result)


def icon_pixels(code):
    """Decode the public archived BMP independently, including panel RGB565 narrowing."""
    row=next((row for row in ASSETS['weather'] if row['code']==code),None)
    if row is None:return bytes(60*60*3)
    offset=int(row['flash_offset'],16)-0x200000
    data=PACK[offset:offset+0x3c00]
    pixel_offset=struct.unpack_from('<I',data,10)[0]
    width,height=struct.unpack_from('<ii',data,18)
    if data[:2]!=b'BM' or (width,height)!=(60,60) or struct.unpack_from('<H',data,28)[0]!=24:
        raise AssertionError('Unexpected weather BMP format')
    pixels=bytearray()
    for y in range(60):
        for x in range(60):
            b,g,r=data[pixel_offset+(59-y)*180+x*3:pixel_offset+(59-y)*180+x*3+3]
            pixels+=rgb(((r>>3)<<11)|((g>>2)<<5)|(b>>3))
    return bytes(pixels)


def different_pixels(actual,expected):
    """Count differing RGB pixels without masking any part of the selected field."""
    if len(actual)!=len(expected):raise AssertionError('Pixel-buffer lengths differ')
    return sum(actual[index:index+3]!=expected[index:index+3] for index in range(0,len(actual),3))


def scroll_layout():
    """Obtain private scroll-state structure offsets from actual compiled DWARF."""
    path=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf=ELFFile(stream)
        symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
        symbol=next(symbol for symbol in symbols if symbol.name=='scrolling_labels')
        rendered=[item for item in symbols if item.name.split('.')[0]=='previous_weather' and item['st_size']==4]
        if len(rendered)!=1:raise AssertionError('Missing unique rendered-weather generation')
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name=die.attributes.get('DW_AT_name')
                if die.tag!='DW_TAG_variable' or not name or name.value!=b'scrolling_labels':continue
                structure=die.get_DIE_from_attribute('DW_AT_type')
                while structure.tag!='DW_TAG_structure_type':
                    structure=structure.get_DIE_from_attribute('DW_AT_type')
                stride=structure.attributes['DW_AT_byte_size'].value
                fields={child.attributes['DW_AT_name'].value.decode():child.attributes['DW_AT_data_member_location'].value
                        for child in structure.iter_children() if child.tag=='DW_TAG_member'}
                if symbol['st_size']!=3*stride:raise AssertionError('Unexpected scroll-state array')
                return {'address':symbol['st_value'],'size':symbol['st_size'],'stride':stride,'fields':fields,
                        'rendered_weather_address':rendered[0]['st_value']}
    raise AssertionError('Missing native scroll DWARF')


def scroll_snapshot(qmp,layout):
    """Read only identified synthetic label states; no guest memory is written."""
    data=read_bytes(qmp,layout['address'],layout['size'])
    result=[]
    for index in range(3):
        raw=data[index*layout['stride']:(index+1)*layout['stride']]
        fields=layout['fields']
        # Description rotation also contains the factory's two-byte unit codes.
        row={'text':raw[fields['text']:fields['text']+65].split(b'\0')[0].decode('latin-1')}
        for name in ('x','y','width','length','offset','pause'):
            row[name]=struct.unpack_from('<I',raw,fields[name])[0]
        row['color']=struct.unpack_from('<H',raw,fields['color'])[0]
        for name in ('returning','completed'):row[name]=bool(raw[fields[name]])
        result.append(row)
    return result


def capture(qmp,folder,layout=None):
    """Briefly pause observation for coherent state/pixels, then resume every guest."""
    qmp.execute('stop')
    try:
        labels=scroll_snapshot(qmp,layout) if layout else None
        generation=int.from_bytes(read_bytes(qmp,layout['rendered_weather_address'],4),'little') if layout else None
        virtual_time=weather.virtual_seconds(qmp)
        path=folder/'observation.png'
        vm.capture_png(qmp,path)
        pixels=vm.ppm_pixels(path.with_suffix('.ppm'))
        path.with_suffix('.ppm').unlink()
        return labels,pixels,virtual_time,generation
    finally:qmp.execute('cont')


def native_frame(qmp,folder,layout,city,title,icon):
    """Require known response text, bounded offsets, exact field pixels and border strips."""
    labels,pixels,seconds,generation=capture(qmp,folder,layout)
    differences={}
    expected=[(0,city,[0,10,180,24],0x07e0),(2,title,[160,83,80,24],0xffe0)]
    for index,text,rect,color in expected:
        label=labels[index]
        if (label['text'],label['x'],label['y'],label['width'],label['length'],label['color']) != \
                (text,rect[0],rect[1],rect[2],len(text)*12,color):
            differences['state-'+str(index)]=1
            continue
        if label['offset']>max(0,len(text)*12-rect[2]):raise AssertionError('Scroll offset exceeds field overflow')
        differences['field-'+str(index)]=different_pixels(region(pixels,rect),text_pixels(text,rect[2],label['offset'],color))
    differences['icon']=different_pixels(region(pixels,[180,10,60,60]),icon_pixels(icon))
    for index,rect in enumerate(GUARDS):
        differences['guard-'+str(index)]=different_pixels(region(pixels,rect),bytes(rect[2]*rect[3]*3))
    return {'labels':labels,'virtual_seconds':seconds,'different_pixels':differences,
            'rendered_weather_generation':generation,
            'passed':not any(differences.values())}


def wait_frame(qmp,folder,layout,city,title,icon,predicate=None,seconds=90):
    """Retry transient in-progress SPI frames, retaining the final failure and sample count."""
    deadline=time.monotonic()+seconds
    attempts=0
    last=None
    while time.monotonic()<deadline:
        attempts+=1
        last=native_frame(qmp,folder,layout,city,title,icon)
        if last['passed'] and (predicate is None or predicate(last)):
            last['attempts']=attempts
            return last
        time.sleep(.08)
    raise AssertionError(f'No complete expected field frame after {attempts} observations: {last}')


def post_city(url,city):
    """Change location through the real firmware handler, using only whitelisted ASCII fixtures."""
    status,_=http(url,'/updateCity',{'city':city+',CN'},origin=url)
    if status!=200:raise AssertionError('City POST failed')


def response(main,icon):
    """Keep all weather numbers valid while controlling only title and icon."""
    data=weather.payload()
    data['weather'][0].update(main=main,description='clear',icon=icon)
    return data


def await_response(qmp,variant,layout,main,icon):
    """Require the actual cache to contain the served title/icon and finish its worker."""
    expected_offset=next((int(row['flash_offset'],16) for row in ASSETS['weather'] if row['code']==icon),0)
    def parsed(row):
        selected=row.get('icon')==icon if variant=='reconstructed' else row['icon_offset']==expected_offset
        return row['valid'] and row['main']==main and selected
    row=weather.wait_snapshot(qmp,variant,layout,parsed,'HTTP fixture was not published by the guest')
    if variant=='reconstructed':
        wait_for(lambda:int.from_bytes(read_bytes(qmp,layout['request_state_address'],4),'little')==0,
                 'Native weather worker did not finish')
    return row


def scroll_trace(qmp,folder,layout):
    """Observe both directions, endpoints and endpoint pauses of both long fields."""
    deadline=time.monotonic()+120
    trace=[]
    evidence={index:{'left':False,'right':False,'start':False,'end':False,'pause':False} for index in (0,2)}
    while time.monotonic()<deadline:
        row=wait_frame(qmp,folder,layout,LONG_CITY,'Thunderstorm','11d',seconds=30)
        for index in (0,2):
            label=row['labels'][index]
            limit=label['length']-label['width']
            evidence[index]['start']|=label['offset']==0
            evidence[index]['end']|=label['offset']==limit
            evidence[index]['pause']|=label['offset'] in (0,limit) and label['pause']>0
            if trace:
                before=trace[-1]['labels'][index]['offset']
                evidence[index]['left']|=label['offset']>before
                evidence[index]['right']|=label['offset']<before
        trace.append(row)
        if all(all(values.values()) for values in evidence.values()):
            return {'passed':True,'evidence':evidence,'frames':trace}
        time.sleep(.1)
    raise AssertionError(f'Scroll did not show both complete directions/endpoints: {evidence}')


def refresh_during_motion(qmp,folder,url,fixture,cache_layout,label_layout):
    """Keep a real reply withheld while exact field pixels advance, then preserve their phase."""
    before=wait_frame(qmp,folder,label_layout,LONG_CITY,'Thunderstorm','11d',
        predicate=lambda row:4<=row['labels'][0]['offset']<=8 and
            not row['labels'][0]['pause'] and not row['labels'][0]['returning'])
    fixture.set_response(200,data=response('Thunderstorm','11d'))
    fixture.hold_response()
    held=[]
    try:
        post_city(url,LONG_CITY)
        wait_for(fixture.response_held.is_set,'Held refresh never reached the service')
        deadline=time.monotonic()+12
        while time.monotonic()<deadline:
            frame=wait_frame(qmp,folder,label_layout,LONG_CITY,'Thunderstorm','11d',seconds=10)
            frame['request_state']=int.from_bytes(read_bytes(qmp,cache_layout['request_state_address'],4),'little')
            city=frame['labels'][0]
            if (not frame['request_state'] or city['returning'] or city['pause'] or
                    frame['rendered_weather_generation']!=before['rendered_weather_generation']):
                raise AssertionError('Refresh changed the cached text or its outward scroll phase')
            if held and city['offset']<held[-1]['labels'][0]['offset']:
                raise AssertionError('Held refresh restarted the city scroll')
            held.append(frame)
            if len(held)>=2 and city['offset']>=held[0]['labels'][0]['offset']+6:
                break
            time.sleep(.08)
        else:
            raise AssertionError('City scroll froze while the real HTTP response was held')
    finally:
        fixture.release_response()
    await_response(qmp,'reconstructed',cache_layout,'Thunderstorm','11d')
    published=int.from_bytes(read_bytes(qmp,cache_layout['address']+cache_layout['fields']['generation'],4),'little')
    if published<=held[-1]['rendered_weather_generation']:
        raise AssertionError('Refresh did not publish a new generation')
    resumed=wait_frame(qmp,folder,label_layout,LONG_CITY,'Thunderstorm','11d',
        predicate=lambda row:row['rendered_weather_generation']==published)
    old,after=held[-1]['labels'][0],resumed['labels'][0]
    # The normal loop can advance at most 20 pixels per virtual second, plus
    # one partially observed loop at either boundary. Publishing identical text
    # must not jump to zero or create a new endpoint pause.
    advance=int(20*(resumed['virtual_seconds']-held[-1]['virtual_seconds']))+6
    if not(old['offset']<=after['offset']<=old['offset']+advance and
           not after['returning'] and not after['pause']):
        raise AssertionError('Applied refresh restarted or jumped the scroll phase')
    return {'passed':True,'before':before,'held':held,'resumed':resumed,'published_generation':published}


def exercise(options,folder,cache_layout,label_layout):
    """Run real location/title/icon transitions, distinguishing literal factory observations."""
    fixture=weather.WeatherFixture(['Shenzhen,CN',LONG_CITY+',CN','A,CN','B,CN'])
    fixture.set_response(200)
    options=SimpleNamespace(**{**vars(options),'network':'clock','service_port':fixture.port,'persistent':False})
    session=None
    native=options.firmware=='reconstructed'
    result={'passed':False,'sources':{},'stages':{},'checks':{}}
    try:
        session,prepared=vm.launch(options,folder)
        result['sources']=prepared['sources']
        url=session['web_urls']['station']
        wait_http(url,'/getclocktype',expected=b'0')
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            await_response(qmp,options.firmware,cache_layout,'Clouds','02d')
            weather.wait_display(qmp)
            fixture.set_response(200,data=response('Thunderstorm','11d'))
            post_city(url,LONG_CITY)
            result['stages']['long_cache']=await_response(qmp,options.firmware,cache_layout,'Thunderstorm','11d')
            if native:
                result['scroll']=scroll_trace(qmp,folder,label_layout)
                result['refresh']=refresh_during_motion(qmp,folder,url,fixture,cache_layout,label_layout)
                fixture.set_response(200,data=response('Thunderstorm','11d'))
                status,_=http(url,'/setclocktype',{'clocktype':'1'},origin=url)
                if status!=200:raise AssertionError('Simple theme POST failed')
                time.sleep(.3)
                status,_=http(url,'/setclocktype',{'clocktype':'0'},origin=url)
                if status!=200:raise AssertionError('Classic theme POST failed')
                result['theme_reset']=wait_frame(qmp,folder,label_layout,LONG_CITY,'Thunderstorm','11d',
                    predicate=lambda row:row['labels'][0]['offset']==0 and row['labels'][0]['pause']>0)
            else:
                weather.wait_display(qmp)
                _,pixels,_,_=capture(qmp,folder)
                result['literal_long']={'city_ideal_differences':different_pixels(region(pixels,[0,10,180,24]),text_pixels(LONG_CITY,180,0,0x07e0)),
                    'title_ideal_differences':different_pixels(region(pixels,[160,83,80,24]),text_pixels('Thunderstorm',80,0,0xffe0))}
            for stage,city,title,icon,status in [('short','A','Fog','50d',200),
                                               ('unavailable','B','',None,503),
                                               ('recovery','B','Rain','10n',200),
                                               ('unknown_icon','B','Clear','99x',200)]:
                fixture.set_response(status,data=response(title,icon) if status==200 else b'Synthetic offline')
                count=len(fixture.rows())
                post_city(url,city)
                wait_for(lambda:len(fixture.rows())>count,'New city did not request weather')
                if status==200:
                    state=await_response(qmp,options.firmware,cache_layout,title,icon)
                else:
                    state=weather.wait_snapshot(qmp,options.firmware,cache_layout,lambda row:not row['valid'],'New-city failure retained valid weather')
                    if native:
                        wait_for(lambda:int.from_bytes(read_bytes(qmp,cache_layout['request_state_address'],4),'little')==0,'Failed request did not finish')
                if native:
                    frame=wait_frame(qmp,folder,label_layout,city,title,icon)
                else:
                    weather.wait_display(qmp)
                    _,pixels,seconds,_=capture(qmp,folder)
                    frame={'virtual_seconds':seconds,'literal_ideal_differences':{
                        'city':different_pixels(region(pixels,[0,10,180,24]),text_pixels(city,180,0,0x07e0)),
                        'title':different_pixels(region(pixels,[160,83,80,24]),text_pixels(title,80,0,0xffe0)),
                        'icon':different_pixels(region(pixels,[180,10,60,60]),icon_pixels(icon))}}
                result['stages'][stage]={'state':state,'frame':frame}
        result['requests']=fixture.rows()
        if not all(row['synthetic_key'] and row['synthetic_location'] and row['resource']=='/data/2.5/weather' for row in result['requests']):
            raise AssertionError('Unexpected service URL/query')
        if not clean_uart(folder):raise AssertionError('Panic during field transition')
        result['checks']={'actual_city_http':True,'known_response_cache':True,'no_panic':True}
        if native:
            result['checks'].update(clipped_live_scroll=True,responsive_refresh_phase=True,theme_reset=True,
                                    short_and_missing_fields=True,unknown_icon_cleanup=True,recovery=True)
        else:
            result['not_applicable_factory']=['requested scroll/phase/reset extension','corrected cleanup expectations; literal pixels recorded']
        result['passed']=True
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        try:
            if session is not None:vm.control(folder,'stop');vm.ensure_stopped(folder)
        finally:fixture.close()
        vm.save_json(folder/'field-report.json',result)
    return result


def run_suite(options,output):
    """Keep actual firmware/SDK behavior and declare requested differences explicitly."""
    sys.path.insert(0,str(Path(options.qemu).resolve().parents[1]/'tools'))
    global vm,http,wait_http,wait_for,clean_uart
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    weather.vm,weather.http,weather.wait_http,weather.wait_for,weather.clean_uart=vm,http,wait_http,wait_for,clean_uart
    output.mkdir(parents=True,exist_ok=True)
    layout=weather.native_layout()
    labels=scroll_layout()
    run=output/('vms-'+uuid.uuid4().hex[:12])
    report={'passed':False,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'flows':{},'cache_layout':layout,'scroll_layout':labels,
            'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),
            'scope':'Real guest HTTP/cache and exact city/title/icon pixels with immutable factory bitmaps, guard strips, scroll directions/pauses and blocked refresh/theme reset. QMP observations briefly pause/resume execution; no memory/register/program patches. Literal factory differences recorded separately. No physical timing or whole-program identity.'}
    try:
        for variant in ('original','reconstructed'):
            options.firmware=variant
            report['flows'][variant]=exercise(options,run/variant,layout,labels)
            print('PASS real guest field HTTP/scroll:',variant,flush=True)
        report['passed']=True
    except Exception as error:
        report['error']=str(error)
        raise
    finally:vm.save_json(output/'report.json',report)
    return report


def main():
    """Run isolated emulator copies of both images and stop every owned VM."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),display='none',paused=False,gdb_port=0,http_base_port=0)
    run_suite(options,args.output)


if __name__=='__main__':main()
