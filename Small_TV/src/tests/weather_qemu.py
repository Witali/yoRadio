"""Compare real guest weather HTTP, parsed RAM and displayed pixels in QEMU.

Only synthetic settings/responses are used. Read-only QMP observations never
patch RAM, registers, executable instructions or the immutable input images.
"""
import argparse
import datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import socket
import struct
import sys
import threading
import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '.build/small-tv-parity/oracle-deps'))
from elftools.elf.elffile import ELFFile


def payload(negative=False):
    """Use complete Kelvin responses with values that expose truncation/sector edges."""
    return {'weather':[{'id':801, 'main':'Clouds', 'description':'scattered clouds', 'icon':'02d'}],
            'main':{'temp':267.75 if negative else 299.95, 'temp_min':266.25 if negative else 294.65,
                    'temp_max':270.25 if negative else 302.65, 'humidity':41 if negative else 67, 'pressure':1013},
            'wind':{'speed':5.25 if negative else 3.75, 'deg':360 if negative else 11.25},
            'dt':1760000000, 'timezone':28800, 'visibility':10000, 'cod':200}


class WeatherFixture:
    """Hold a loopback-only persistent HTTP stream for SLIRP's guestfwd chardev."""
    def __init__(self, locations=None):
        self.lock = threading.Lock()
        self.locations = set(locations or ['Shenzhen,CN'])
        self.status, self.body = 503, b'Synthetic service temporarily unavailable'
        self.response_delay = 0
        self.requests, self.connections = [], []
        owner = self
        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'
            def setup(self):
                super().setup()
                with owner.lock: owner.connections.append(self.connection)
            def log_message(self, *args):
                pass
            def handle(self):
                try: super().handle()
                except (ConnectionResetError, BrokenPipeError): pass
            def do_GET(self):
                target = urlsplit(self.path)
                fields = parse_qs(target.query)
                with owner.lock:
                    status, body, delay = owner.status, owner.body, owner.response_delay
                    # Never retain a raw request URL, key, cookie or header.
                    owner.requests.append({'method':'GET', 'resource':target.path,
                        'synthetic_location':len(fields.get('q',[]))==1 and fields['q'][0] in owner.locations,
                        'synthetic_key':fields.get('appid') == ['disabled'],
                        'status':status, 'body_sha256':vm.digest(body), 'fragments':(len(body)+63)//64})
                if delay: time.sleep(delay)
                self.send_response(status)
                self.send_header('Content-Type', 'application/json' if body.startswith(b'{') else 'text/plain')
                self.send_header('Content-Length', str(len(body)))
                # guestfwd retains one host chardev across separate guest TCP
                # connections: do not close this host stream after one request.
                self.send_header('Connection', 'keep-alive')
                self.end_headers()
                for start in range(0, len(body), 64):
                    self.wfile.write(body[start:start+64])
                    self.wfile.flush()
                    time.sleep(.025)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def set_response(self, status, negative=False, data=None, delay=0):
        """Atomically select the next HTTP status and complete synthetic JSON body."""
        body = data if isinstance(data,bytes) else json.dumps(payload(negative) if data is None else data, separators=(',', ':')).encode()
        with self.lock:
            self.status, self.body, self.response_delay = status, body, delay

    def rows(self):
        """Copy completed request observations without exposing sensitive inputs."""
        with self.lock: return list(self.requests)

    def close(self):
        """Stop listeners and active chardev sockets after the VM has exited."""
        self.server.shutdown()
        with self.lock:
            for connection in self.connections:
                try: connection.shutdown(socket.SHUT_RDWR)
                except OSError: pass
                connection.close()
        self.server.server_close()
        self.thread.join(timeout=5)


def native_layout():
    """Derive the actual compiled weather struct ABI from the current ELF/DWARF."""
    path = ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        symbol = next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == 'cached_weather')
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                if die.tag == 'DW_TAG_variable' and die.attributes.get('DW_AT_name') and die.attributes['DW_AT_name'].value == b'cached_weather':
                    structure = die.get_DIE_from_attribute('DW_AT_type')
                    while structure.tag in ('DW_TAG_typedef', 'DW_TAG_const_type'):
                        structure = structure.get_DIE_from_attribute('DW_AT_type')
                    fields = {child.attributes['DW_AT_name'].value.decode():child.attributes['DW_AT_data_member_location'].value
                              for child in structure.iter_children() if child.tag == 'DW_TAG_member'}
                    size = structure.attributes['DW_AT_byte_size'].value
                    if size != symbol['st_size']: raise AssertionError('DWARF/symbol weather layout disagrees')
                    worker = next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == 'request_state')
                    return {'address':symbol['st_value'], 'size':size, 'fields':fields,
                            'request_state_address':worker['st_value'], 'elf_sha256':vm.digest(path.read_bytes())}
    raise AssertionError('No compiled cached_weather type')


def read_bytes(qmp, address, size):
    """Observe only identified synthetic weather fields with the QMP memory reader."""
    reply = qmp.execute('human-monitor-command', **{'command-line':f'xp /{size}bx {address:#x}'})
    data = bytes(int(value, 16) for line in reply.splitlines() if ':' in line
                 for value in re.findall(r'0x([0-9a-fA-F]{2})\b', line.split(':',1)[1]))
    if len(data) != size: raise AssertionError('Unexpected QMP memory dump format')
    return data


def snapshot(qmp, variant, layout):
    """Decode factory globals or DWARF-derived native cache without replacing logic."""
    def text(raw): return raw.split(b'\0')[0].decode('ascii')
    if variant == 'original':
        raw = read_bytes(qmp, 0x3fcc3a30, 32)
        names = read_bytes(qmp, 0x3fcbff6c, 60)
        return {'valid':bool(read_bytes(qmp,0x3fcc39d7,1)[0]),
                'temperature_c':struct.unpack_from('<i',raw,28)[0],
                'humidity':struct.unpack_from('<i',raw,24)[0],
                'temperature_min_c':struct.unpack_from('<d',raw,0)[0],
                'temperature_max_c':struct.unpack_from('<d',raw,8)[0],
                'wind_mps':struct.unpack_from('<d',raw,16)[0],
                'main':text(names[:20]), 'description':text(names[20:40]),
                'wind_direction':text(names[40:60]),
                'icon_offset':int.from_bytes(read_bytes(qmp,0x3fcc3aa8,4),'little')}
    raw = read_bytes(qmp, layout['address'], layout['size'])
    fields = layout['fields']
    result = {'valid':bool(raw[fields['valid']])}
    for name in ('temperature_c','temperature_min_c','temperature_max_c','wind_mps'):
        result[name] = struct.unpack_from('<d',raw,fields[name])[0]
    result['humidity'] = struct.unpack_from('<i',raw,fields['humidity'])[0]
    for name in ('main','description','wind_direction','icon'):
        result[name] = text(raw[fields[name]:])
    return result


def wait_snapshot(qmp, variant, layout, predicate, message):
    """Poll live guest state with a deadline, preserving the final failing observation."""
    deadline = time.monotonic() + 90
    last = None
    while time.monotonic() < deadline:
        last = snapshot(qmp, variant, layout)
        if predicate(last): return last
        time.sleep(.2)
    raise AssertionError(f'{message}: {last}')


def virtual_seconds(qmp):
    """Read the actual emulated microsecond counter, independent of host CPU load."""
    return int.from_bytes(read_bytes(qmp,0x6004d000,4),'little') / 1e6


def wait_display(qmp):
    """Allow startup to finish and two guest seconds of rendering after a response."""
    target = max(25,virtual_seconds(qmp)+2)
    wait_for(lambda:virtual_seconds(qmp)>=target, 'Guest display virtual time stalled')


def expected_values(row, negative=False):
    """Check explicit service values rather than accepting two equally wrong programs."""
    source = payload(negative)
    expected = {'temperature_c':-5 if negative else 26, 'humidity':41 if negative else 67,
                'wind_mps':source['wind']['speed'], 'temperature_min_c':source['main']['temp_min']-273.15,
                'temperature_max_c':source['main']['temp_max']-273.15, 'main':'Clouds',
                'description':'scattered cloud', 'wind_direction':'North' if negative else 'North-Northeast'}
    for key, value in expected.items():
        if row[key] != value: raise AssertionError(f'{key}: {row[key]} != {value}')
    if not row['valid']: raise AssertionError('Weather cache not valid')


def region(pixels, rectangle):
    """Extract a stable weather region, excluding clock/animation/rotating labels."""
    x,y,width,height = rectangle
    return b''.join(pixels[(yy*240+x)*3:(yy*240+x+width)*3] for yy in range(y,y+height))


def exercise(options, folder, layout):
    """Run failure, retry, positive/negative weather and non-200 JSON in a real guest."""
    fixture = WeatherFixture()
    options = SimpleNamespace(**{**vars(options),'network':'clock','weather_port':fixture.port,'persistent':False})
    session = None
    result = {'passed':False, 'snapshots':{}, 'captures':{}}
    try:
        session, prepared = vm.launch(options,folder)
        result['sources'] = prepared['sources']
        url = session['web_urls']['station']
        wait_http(url, '/getclocktype', expected=b'0')
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            result['weather_services'] = qmp.execute('qom-get',path='/machine/wifi',property='weather-services')
            if not result['weather_services']: raise AssertionError('Weather DNS property not enabled')
            wait_for(lambda: bool(fixture.rows()), 'Guest never requested weather')
            result['snapshots']['initial_503'] = wait_snapshot(qmp,options.firmware,layout,lambda r:not r['valid'],'Failure incorrectly enabled weather')
            fixture.set_response(200)
            row = wait_snapshot(qmp,options.firmware,layout,lambda r:r['valid'] and r['humidity']==67,'Positive weather was not parsed after retry')
            expected_values(row)
            result['snapshots']['positive'] = row
            # Startup lasts 18.1 virtual seconds; host sleeps cannot establish
            # its completion when several emulators compete for CPU time.
            wait_display(qmp)
            for index in range(3):
                image = folder/f'positive-{index}.png'
                vm.capture_png(qmp,image)
                result['captures'][image.stem] = vm.ppm_pixels(image.with_suffix('.ppm'))
                image.with_suffix('.ppm').unlink()
                time.sleep(.3)
            fixture.set_response(503, negative=True)
            count = len(fixture.rows())
            status,_ = http(url,'/updateCity',{'city':'Shenzhen,CN'},origin=url)
            if status != 200: raise AssertionError('Real /updateCity failed')
            wait_for(lambda:len(fixture.rows())>count, 'City update did not issue new weather HTTP')
            time.sleep(.5)
            if options.firmware == 'original':
                row = wait_snapshot(qmp,options.firmware,layout,lambda r:r['valid'] and r['humidity']==41,'Vendor non-200 parser behavior changed')
                result['factory_non_200_json_bug'] = True
            else:
                wait_for(lambda:int.from_bytes(read_bytes(qmp,layout['request_state_address'],4),'little')==0,
                         'Weather worker did not finish the HTTP 503 response')
                row = snapshot(qmp,options.firmware,layout)
                # An unchanged city retains its previous successful cache on
                # transport/status errors, but must not parse the error JSON.
                expected_values(row)
                result['native_rejects_non_200_json'] = True
            result['snapshots']['non_200_json'] = row
            fixture.set_response(200,negative=True)
            status,_ = http(url,'/updateCity',{'city':'Shenzhen,CN'},origin=url)
            if status != 200: raise AssertionError('Second city refresh failed')
            row = wait_snapshot(qmp,options.firmware,layout,lambda r:r['valid'] and r['humidity']==41,'Negative weather was not parsed')
            expected_values(row,True)
            result['snapshots']['negative'] = row
            wait_display(qmp)
            for index in range(3):
                image = folder/f'negative-{index}.png'
                vm.capture_png(qmp,image)
                result['captures'][image.stem] = vm.ppm_pixels(image.with_suffix('.ppm'))
                image.with_suffix('.ppm').unlink()
                time.sleep(.3)
        result['requests'] = fixture.rows()
        if not all(r['synthetic_key'] and r['synthetic_location'] and r['resource']=='/data/2.5/weather' for r in result['requests']):
            raise AssertionError('Guest requested the wrong weather URL')
        if not any(r['status']==200 for r in result['requests']): raise AssertionError('No successful weather HTTP')
        for negative in (False,True):
            expected = vm.digest(json.dumps(payload(negative),separators=(',',':')).encode())
            if not any(r['status']==200 and r['body_sha256']==expected for r in result['requests']):
                raise AssertionError('Missing successful positive/negative weather response')
        if not clean_uart(folder): raise AssertionError('Guest panic/watchdog during weather')
        if 'C2 DNS answer service=weather' not in (folder/'qemu.log').read_text(errors='replace'):
            raise AssertionError('No actual DNS reply for the weather hostname')
        result['passed'] = True
    except Exception as error:
        result['error'] = str(error)
        raise
    finally:
        try:
            if session is not None: vm.control(folder,'stop'); vm.ensure_stopped(folder)
        finally:
            fixture.close()
        result['requests'] = fixture.rows()
        saved = {key:value for key,value in result.items() if key != 'captures'}
        vm.save_json(folder/'weather-report.json',saved)
    return result


def run_suite(options, output):
    """Publish live network/value/pixel evidence and retain failures as failures."""
    sys.path.insert(0,str(Path(options.qemu).resolve().parents[1]/'tools'))
    global vm, http, wait_http, wait_for, clean_uart
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    output.mkdir(parents=True,exist_ok=True)
    layout = native_layout()
    report = {'passed':False,'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'scope':'Real guest DNS/TCP/HTTP via isolated loopback fixture; parsed synthetic weather and stable LCD regions. No Internet service, physical RF or full-program equivalence.',
              'native_layout':layout,'flows':{},'regions':{},'qemu_sha256':vm.digest(Path(options.qemu).read_bytes())}
    run = output / ('vms-'+uuid.uuid4().hex[:12])
    try:
        for variant in ('original','reconstructed'):
            options.firmware = variant
            report['flows'][variant] = exercise(options,run/variant,layout)
            print('PASS real guest weather HTTP/parsed values:',variant,flush=True)
        rectangles = {'temperature':[80,180,72,24], 'humidity':[80,210,72,24],
                      'summary':[160,83,80,24], 'icon':[180,10,60,60]}
        for phase in ('positive','negative'):
            for name, rectangle in rectangles.items():
                captured = {v:[region(p,rectangle) for k,p in report['flows'][v]['captures'].items() if k.startswith(phase)] for v in report['flows']}
                if any(not any(any(p) for p in frames) for frames in captured.values()):
                    raise AssertionError(f'Weather LCD region is blank: {phase}/{name}')
                equal = any(a==b and any(a) for a in captured['original'] for b in captured['reconstructed'])
                report['regions'][phase+'_'+name] = {'rectangle':rectangle,'pixels_equal':equal}
                if not equal: raise AssertionError(f'Weather LCD differs: {phase}/{name}')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        for row in report['flows'].values(): row.pop('captures',None)
        vm.save_json(output/'report.json',report)
    return report


def main():
    """Use the installed emulator and archived firmware, leaving no VM running."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    sys.path.insert(0,str(args.qemu_root/'tools'))
    global vm, http, wait_http, wait_for, clean_uart
    import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,wait_for,clean_uart
    options=SimpleNamespace(yoradio=str(ROOT),qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(ROOT/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(args.qemu_root/'configs/boards/small-tv-c2.json'),display='none',paused=False,gdb_port=0,http_base_port=0)
    run_suite(options,args.output)


if __name__=='__main__': main()
