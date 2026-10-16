"""Observe real clock frames while an external weather server withholds its reply."""
import argparse,hashlib,json,socket,struct,sys,threading,time
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--yoradio',type=Path,default=ROOT)
parser.add_argument('--dependency-root',type=Path)
parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
dependencies=args.dependency_root or args.yoradio
sys.path[:0]=[str(args.qemu_root/'tools'),str(dependencies/'.build/small-tv-parity/oracle-deps')]
import small_tv_vm as vm
from small_tv_http_test import http,wait_http,wait_for,clean_uart
from gdb_observer import Observer
import weather_qemu as weather
import scene_qemu as scene
from elftools.elf.elffile import ELFFile
weather.vm=vm;weather.wait_for=wait_for;scene.vm=vm
args.output.mkdir(parents=True,exist_ok=False)
elf_path=args.yoradio/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
elf_sha=hashlib.sha256(elf_path.read_bytes()).hexdigest()
app=args.yoradio/'firmware/development/small-tv-esp32c2-reconstructed/app.bin'
if app.read_bytes()[176:208]!=bytes.fromhex(elf_sha):raise ValueError('App/ELF pair mismatch')
with elf_path.open('rb') as stream:
    elf=ELFFile(stream)
    symbols={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s['st_value']}
    running=[die.attributes['DW_AT_const_value'].value
             for cu in elf.get_dwarf_info().iter_CUs() for die in cu.iter_DIEs()
             if die.tag=='DW_TAG_enumerator' and die.attributes.get('DW_AT_name') and
                die.attributes['DW_AT_name'].value==b'REQUEST_RUNNING']
    if len(running)!=1:raise ValueError('Missing compiled REQUEST_RUNNING enum')
    running=running[0]
fixture=weather.WeatherFixture(['Shenzhen,CN','Fixture,CN']);fixture.set_response(200)
held=threading.Event();release=threading.Event();hold=False
handler=fixture.server.RequestHandlerClass
original_get=handler.do_GET
def controlled_get(self):
    """Hold only the external service response; never modify a guest task or cache."""
    if hold:
        held.set()
        release.wait(30)
    original_get(self)
handler.do_GET=controlled_get
with socket.socket() as reservation:
    reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
options=SimpleNamespace(yoradio=str(args.yoradio),
    qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
    rom_elf=str(dependencies/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
    hardware_profile=str(args.yoradio/'Small_TV/qemu/profiles/small-tv-c2.json'),
    network='clock',display='none',persistent=False,paused=True,gdb_port=port,
    firmware='reconstructed',service_port=fixture.port)
test_paths=[Path(__file__),*[Path(__file__).with_name(name) for name in
    ('gdb_observer.py','weather_qemu.py','scene_qemu.py')]]
fingerprints=[{'file':str(path.relative_to(ROOT)).replace('\\','/'),
               'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in test_paths]
helpers={name:hashlib.sha256((args.qemu_root/'tools'/name).read_bytes()).hexdigest()
         for name in ('small_tv_vm.py','small_tv_http_test.py','small_tv_network.py',
                      'small_tv_web.py','esp_board.py','esp_services.py')}
session=observer=None
result={'passed':False,'scope':__doc__,'native_elf_sha256':elf_sha,
        'app_sha256':vm.digest(app.read_bytes()),'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),
        'test_inputs':fingerprints,'helper_sha256':helpers,'compiled_running_mask':running}
def sample(qmp,name):
    """Record a real completed simple-clock second event using hardware breakpoints only."""
    entry=symbols['factory_draw_simple']
    code=None
    observer.interrupt();started=weather.virtual_seconds(qmp)
    while True:
        observer.breakpoint(entry);observer.continue_to(entry)
        current=observer.memory(entry,4)
        if code is None:code=current
        if current!=code:raise ValueError('Renderer code changed between observations')
        ready=bool(observer.register(14)) and not observer.register(13)
        local=list(struct.unpack('<9i',observer.memory(observer.register(11),36)))
        target=observer.register(1)
        observer.breakpoint(entry,False)
        return_code=observer.memory(target,4)
        observer.breakpoint(target);observer.continue_to(target);observer.breakpoint(target,False)
        if observer.memory(entry,4)!=code or observer.memory(target,4)!=return_code:
            raise ValueError('Hardware breakpoint changed guest code')
        if ready:break
    pixels=scene.picture(qmp,args.output,name)
    state=int.from_bytes(observer.memory(symbols['request_state'],4),'little')
    row={'local_tm':local,'request_state':state,'guest_seconds':weather.virtual_seconds(qmp),
         'wait_guest_seconds':weather.virtual_seconds(qmp)-started,'rgb_sha256':hashlib.sha256(pixels).hexdigest()}
    observer.resume()
    return row
try:
    session,prepared=vm.launch(options,args.output);result['sources']=prepared['sources']
    observer=Observer(port)
    with vm.QMP(session['qmp_port'],session['name']) as qmp:
        observer.resume();url=session['web_urls']['station']
        wait_http(url,'/getclocktype');weather.wait_display(qmp)
        status,_=http(url,'/setclocktype',{'clocktype':'1'},origin=url,timeout=20)
        if status!=200:raise ValueError('Cannot select simple theme')
        for index in range(70):
            result['before']=sample(qmp,'before')
            if result['before']['local_tm'][0] in (57,58):break
        else:raise ValueError('No imminent natural minute boundary')
        hold=True
        status,_=http(url,'/updateCity',{'city':'Fixture,CN'},origin=url,timeout=20)
        if status!=200:raise ValueError('City update failed')
        wait_for(held.is_set,'External weather request did not arrive')
        state=int.from_bytes(weather.read_bytes(qmp,symbols['request_state'],4),'little')
        if not state&running:raise ValueError('Weather task is not running: '+str(state))
        start=weather.virtual_seconds(qmp)
        wait_for(lambda:weather.virtual_seconds(qmp)>=start+3.2,'Guest time stalled during weather wait')
        result['during']=sample(qmp,'during')
        row=result['during']
        if not row['request_state']&running or row['wait_guest_seconds']>1.5:
            raise AssertionError('Clock waited for the weather task: '+str(row))
        if row['rgb_sha256']==result['before']['rgb_sha256']:
            raise AssertionError('Clock pixels did not advance while response was held')
        release.set()
        wait_for(lambda:int.from_bytes(weather.read_bytes(qmp,symbols['request_state'],4),'little')==0,
                 'Weather request did not complete after release')
        result['passed']=clean_uart(args.output)
        print(json.dumps({'passed':result['passed'],'during':row}),flush=True)
except Exception as error:
    result['error']=str(error)
    raise
finally:
    release.set()
    if observer:observer.close()
    if session:
        try:vm.control(args.output,'stop')
        finally:vm.ensure_stopped(args.output)
    fixture.close()
    result['inputs_unchanged']=elf_sha==hashlib.sha256(elf_path.read_bytes()).hexdigest() and result['app_sha256']==vm.digest(app.read_bytes())
    result['inputs_unchanged'] &= all(hashlib.sha256((ROOT/row['file']).read_bytes()).hexdigest()==row['sha256']
                                      for row in fingerprints)
    result['inputs_unchanged'] &= all(hashlib.sha256((args.qemu_root/'tools'/name).read_bytes()).hexdigest()==sha
                                      for name,sha in helpers.items())
    result['inputs_unchanged'] &= result['qemu_sha256']==vm.digest(Path(options.qemu).read_bytes())
    result['passed'] &= result['inputs_unchanged']
    vm.save_json(args.output/'report.json',result)
raise SystemExit(0 if result['passed'] else 1)
