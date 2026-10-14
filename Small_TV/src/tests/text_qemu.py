"""Exercise actual UTF-8 settings/weather HTTP and bounded text pixels in both VMs."""
from __future__ import annotations
import argparse
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
import uuid

import weather_qemu as weather
import field_qemu as fields
from text_oracle import source_fonts,glyph_pixels
from weather_qemu import ROOT,read_bytes,region

FONTS,SPLEEN,BDF=source_fonts()


def tokens(text):
    """Declare Unicode cells independently, merging only explicit temperature spellings."""
    result=[]
    index=0
    while index<len(text):
        if text[index]=='°' and index+1<len(text) and text[index+1] in 'CF':
            result.append(0x2103 if text[index+1]=='C' else 0x2109)
            index+=2
        else:
            result.append(ord(text[index]))
            index+=1
    return result


def expected_text(text,width,offset,color):
    """Compose independent BDF/factory glyphs, clipping every RGB byte to its field."""
    codes=tokens(text)
    cells=sum(24 if code in (0x2103,0x2109) else 12 for code in codes)
    x=(width-cells)//2 if cells<=width else -offset
    result=bytearray(width*24*3)
    ink=fields.rgb(color)
    for code in codes:
        shape=glyph_pixels(code,24,FONTS,SPLEEN)
        for y,row in enumerate(shape):
            for dx,paint in enumerate(row):
                px=x+dx
                if 0<=px<width and paint:
                    result[(y*width+px)*3:(y*width+px+1)*3]=ink
        x+=24 if code in (0x2103,0x2109) else 12
    return bytes(result),cells


def cache(qmp,variant,layout):
    """Read exact raw label bytes so a torn factory UTF-8 prefix remains observable."""
    if variant=='original':
        raw=read_bytes(qmp,0x3fcbff6c,40)
        main,description=raw[:20].split(b'\0')[0],raw[20:].split(b'\0')[0]
        valid=bool(read_bytes(qmp,0x3fcc39d7,1)[0])
    else:
        raw=read_bytes(qmp,layout['address'],layout['size'])
        positions=layout['fields']
        main=raw[positions['main']:positions['main']+16].split(b'\0')[0]
        description=raw[positions['description']:positions['description']+65].split(b'\0')[0]
        valid=bool(raw[positions['valid']])
    return {'valid':valid,'main_hex':main.hex(),'description_hex':description.hex()}


def native_frame(qmp,folder,layout,city,title):
    """Require decoded cache text, scalar widths and all field/guard pixels to agree."""
    labels,pixels,seconds,generation=fields.capture(qmp,folder,layout)
    differences={}
    for index,text,rect,color in [(0,city,[0,10,180,24],0x07e0),(2,title,[160,83,80,24],0xffe0)]:
        label=labels[index]
        # The shared raw-state reader uses Latin-1 to preserve legacy unit bytes.
        # These two fields originate in UTF-8 JSON, so require valid UTF-8 here.
        actual=label['text'].encode('latin1').decode('utf-8')
        label['text']=actual
        wanted,length=expected_text(text,rect[2],label['offset'],color)
        if (actual,label['length'],label['x'],label['y'],label['width'],label['color']) != \
                (text,length,rect[0],rect[1],rect[2],color):
            differences['state-'+str(index)]=1
        elif label['offset']>max(0,length-rect[2]):
            raise AssertionError('Unicode scroll offset exceeds the true glyph overflow')
        else:
            differences['field-'+str(index)]=fields.different_pixels(region(pixels,rect),wanted)
    for index,rect in enumerate(fields.GUARDS):
        differences['guard-'+str(index)]=fields.different_pixels(region(pixels,rect),bytes(rect[2]*rect[3]*3))
    return {'labels':labels,'virtual_seconds':seconds,'rendered_weather_generation':generation,
            'different_pixels':differences,'passed':not any(differences.values())}


def wait_frame(qmp,folder,layout,city,title,predicate=None):
    """Observe complete rendered frames without accepting transient half-written SPI output."""
    deadline=time.monotonic()+90
    last=None
    while time.monotonic()<deadline:
        last=native_frame(qmp,folder,layout,city,title)
        if last['passed'] and (predicate is None or predicate(last)):
            return last
        time.sleep(.1)
    raise AssertionError('No valid UTF-8 field frame: '+str(last))


def payload_bytes(main,description):
    """Split the fixture's first multibyte scalar across its 64-byte server writes."""
    data=weather.payload()
    data['weather'][0].update(main=main,description=description,icon='02d')
    for count in range(64):
        body=json.dumps({'padding':'P'*count,**data},ensure_ascii=False,separators=(',',':')).encode('utf-8')
        first=next((index for index,byte in enumerate(body) if byte>=128),None)
        if first is None or first%64==63:
            return body,first is not None
    raise AssertionError('Cannot place a multibyte split in the fixture')


def utf8_prefix(text,limit=15):
    """Use Python's strict decoder to retain only the complete source-byte prefix."""
    data=text.encode('utf-8')[:limit]
    while data:
        try:return data.decode('utf-8')
        except UnicodeDecodeError:data=data[:-1]
    return ''


def factory_city_fault(options,folder):
    """Require the literal factory NULL-client fault for a real UTF-8 city request."""
    fixture=weather.WeatherFixture()
    fixture.set_response(200)
    options=SimpleNamespace(**{**vars(options),'firmware':'original','network':'clock',
                              'weather_port':fixture.port,'persistent':False})
    session=None
    report={'passed':False,'scope':'Expected immutable factory defect only; no corrected-program panic is permitted.'}
    try:
        session,prepared=vm.launch(options,folder)
        report['sources']=prepared['sources']
        url=session['web_urls']['station']
        wait_http(url,'/getclocktype',expected=b'0')
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            weather.wait_display(qmp)
        try:
            status,_=http(url,'/updateCity',{'city':'Тест,CN'},origin=url,ensure_ascii=False)
            report['post_status']=status
        except OSError as error:
            report['post_error']=type(error).__name__
        def observed():
            text=(folder/'uart.log').read_text(errors='replace')
            return ('Load access fault' in text and 'MEPC    : 0x4203e8f0' in text
                    and 'RA      : 0x4201098c' in text and 'MTVAL   : 0x0000000c' in text)
        wait_for(observed,'Expected stock UTF-8 URL/NULL-client fault did not occur')
        report.update(passed=True,panic_pc='0x4203e8f0',caller='0x4201098c',fault_address='0xc',
                      expected_fault_detected=True)
    finally:
        try:
            if session:
                vm.control(folder,'stop')
                vm.ensure_stopped(folder)
        finally:fixture.close()
        vm.save_json(folder/'factory-city-fault.json',report)
    return report


def exercise(options,folder,layout,label_layout):
    """Send real browser-style UTF-8 and fragmented weather; keep stock failures separate."""
    fixture=weather.WeatherFixture()
    cases=[('cyrillic','Тест','Облачно','Небольшой дождь'),
           ('unicode-scroll','ДлинныйГородДлинныйГород','Облачно','clear'),
           ('latin','München','Café','déjà vu'),
           ('unsupported-cjk','北京','😀','clear'),
           ('split-label-budget','A','12345678901234é','1234567890123é')]
    if options.firmware=='original':
        cases=[(name,'Fixture'+str(index),title,description) for index,(name,_,title,description) in enumerate(cases)]
    fixture.locations.update(city+',CN' for _,city,_,_ in cases)
    fixture.set_response(200)
    options=SimpleNamespace(**{**vars(options),'network':'clock','weather_port':fixture.port,'persistent':False})
    session=None
    result={'passed':False,'sources':{},'cases':[],'checks':{}}
    try:
        session,prepared=vm.launch(options,folder)
        result['sources']=prepared['sources']
        url=session['web_urls']['station']
        wait_http(url,'/getclocktype',expected=b'0')
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            weather.wait_display(qmp)
            for name,city,title,description in cases:
                body,split=payload_bytes(title,description)
                fixture.set_response(200,data=body)
                count=len(fixture.rows())
                status,_=http(url,'/updateCity',{'city':city+',CN'},origin=url,ensure_ascii=False)
                if status!=200:raise AssertionError('Real UTF-8 city POST failed')
                wait_for(lambda:len(fixture.rows())>count,'Unicode location did not request weather')
                main_bytes=(utf8_prefix(title).encode() if options.firmware=='reconstructed' else title.encode()[:15])
                description_bytes=(utf8_prefix(description).encode() if options.firmware=='reconstructed' else description.encode()[:15])
                def parsed():
                    state=cache(qmp,options.firmware,layout)
                    return state['valid'] and state['main_hex']==main_bytes.hex() and state['description_hex']==description_bytes.hex()
                wait_for(parsed,'UTF-8 response prefix never reached the actual cache')
                row={'case':name,'city':city,'source_main':title,'source_description':description,
                     'cache':cache(qmp,options.firmware,layout),'server_multibyte_split':split}
                if options.firmware=='reconstructed':
                    wanted=main_bytes.decode('utf-8')
                    row['frame']=wait_frame(qmp,folder,label_layout,city,wanted)
                    if name=='unicode-scroll':
                        first=wait_frame(qmp,folder,label_layout,city,wanted,
                                         lambda item:item['labels'][0]['offset']==0 and item['labels'][0]['pause']>0)
                        outward=wait_frame(qmp,folder,label_layout,city,wanted,
                                           lambda item:item['labels'][0]['offset']>0 and not item['labels'][0]['returning'])
                        end=wait_frame(qmp,folder,label_layout,city,wanted,
                                       lambda item:item['labels'][0]['offset']==item['labels'][0]['length']-180 and item['labels'][0]['returning'])
                        back=wait_frame(qmp,folder,label_layout,city,wanted,
                                        lambda item:item['labels'][0]['offset']>0 and item['labels'][0]['returning'] and not item['labels'][0]['pause'])
                        complete=wait_frame(qmp,folder,label_layout,city,wanted,
                                            lambda item:item['labels'][0]['completed'])
                        row['scroll']={'passed':True,'first':first,'outward':outward,'end':end,'back':back,'complete':complete}
                else:
                    weather.wait_display(qmp)
                    _,pixels,_,_=fields.capture(qmp,folder)
                    row['literal_city_vs_corrected_pixels']=fields.different_pixels(region(pixels,[0,10,180,24]),
                                                                                  expected_text(city,180,0,0x07e0)[0])
                    row['literal_frame_sha256']=vm.digest(pixels)
                row['passed']=True
                result['cases'].append(row)
            result['requests']=fixture.rows()
            if options.firmware=='reconstructed' and any(not row['synthetic_location'] or not row['synthetic_key'] for row in result['requests']):
                raise AssertionError('Native UTF-8 URL/query encoding changed the synthetic location')
            result['checks']={'browser_style_utf8_post':True,'actual_weather_prefixes':True,
                              'native_glyphs_width_scroll_guards':options.firmware=='reconstructed',
                              'no_panic':clean_uart(folder)}
            result['passed']=result['checks']['no_panic'] and len(result['cases'])==len(cases)
    except Exception as error:
        result['error']=str(error)
        raise
    finally:
        try:
            if session is not None:
                vm.control(folder,'stop')
                vm.ensure_stopped(folder)
        finally:fixture.close()
        vm.save_json(folder/'text-report.json',result)
    return result


def run_suite(options,output):
    """Bind real UTF-8 transport/render evidence to the immutable applications and emulator."""
    global vm,http,wait_http,wait_for,clean_uart
    sys.path.insert(0,str(Path(options.qemu).resolve().parents[1]/'tools'))
    overlay=getattr(options,'http_helper_overlay',None)
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    import small_tv_http_test as helper
    if overlay:
        # The full suite may already have imported the canonical helper. Load
        # the exact committed overlay under a distinct name instead of relying
        # on sys.path to replace Python's existing module cache.
        path=Path(overlay).resolve()/'small_tv_http_test.py'
        metadata=json.loads((Path(overlay)/'manifest.json').read_text())
        if vm.digest(path.read_bytes())!=metadata['sha256']:
            raise ValueError('HTTP helper overlay changed since its pinned snapshot')
        spec=importlib.util.spec_from_file_location('small_tv_http_test_utf8_fixture',path)
        helper=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        http,wait_http,wait_for,clean_uart=helper.http,helper.wait_http,helper.wait_for,helper.clean_uart
    weather.vm=fields.vm=vm
    weather.http=fields.http=http
    weather.wait_for=fields.wait_for=wait_for
    output.mkdir(parents=True,exist_ok=True)
    layout,label_layout=weather.native_layout(),fields.scroll_layout()
    report={'passed':False,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'flows':{},'cache_layout':layout,'scroll_layout':label_layout,
            'font_source_sha256':vm.digest(BDF.read_bytes()),'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),'scope':__doc__}
    report['http_helper_sha256']=vm.digest(Path(helper.__file__).read_bytes())
    if overlay:
        report['http_helper_overlay']=json.loads((Path(overlay)/'manifest.json').read_text())
    run=output/('vms-'+uuid.uuid4().hex[:12])
    try:
        report['factory_utf8_city_fault']=factory_city_fault(options,run/'factory-city-fault')
        for variant in ('original','reconstructed'):
            options.firmware=variant
            report['flows'][variant]=exercise(options,run/variant,layout,label_layout)
            print('PASS actual UTF-8 HTTP/cache/render:',variant,flush=True)
        report['passed']=all(row['passed'] for row in report['flows'].values())
    except Exception as error:
        report['error']=str(error)
        variant=getattr(options,'firmware','factory-city-fault')
        if (run/variant/'text-report.json').exists():
            report['flows'][variant]=json.loads((run/variant/'text-report.json').read_text())
        elif (run/'factory-city-fault/factory-city-fault.json').exists():
            report['factory_utf8_city_fault']=json.loads((run/'factory-city-fault/factory-city-fault.json').read_text())
        raise
    finally:vm.save_json(output/'report.json',report)
    return report


def main():
    """Use local loopback fixtures and always close owned VMs/listeners."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--http-helper-overlay',type=Path,help='Immutable committed HTTP-helper snapshot for concurrent-checkout testing')
    args=parser.parse_args()
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(args.qemu_root/'configs/boards/small-tv-c2.json'),display='none',paused=False,gdb_port=0,http_base_port=0,
        http_helper_overlay=args.http_helper_overlay)
    run_suite(options,args.output)


if __name__=='__main__':main()
