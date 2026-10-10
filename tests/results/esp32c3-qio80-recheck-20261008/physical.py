import json, subprocess, sys, time, struct, threading
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, require
from ota import snapshot, verify_snapshot, image_info
from flash_mode import validate
from serial_lines import serial_lines
import serial

ROOT=Path('.build/c3-qio80-recheck-20261008')
OUT=ROOT/'physical'
PRIVATE=ROOT/'private'
BOARD=Board('http://192.168.100.4')
HOST='192.168.100.253'
PORT='COM9'
QUIET=Path('firmware/development/esp32c3-idf-6.1-compact-icy-quiet/app.bin')
TRUST=Path('.build/c3-tls-records-20261007/trust')
PHASES=[]

def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def run(name,command,required=False,timeout=1800,private=False):
    folder=PRIVATE if private else OUT
    label=name.replace('/','-')
    print('START',name,flush=True)
    start=time.monotonic()
    try:
        with (folder/(label+'.log')).open('xb') as log:
            proc=subprocess.run(list(map(str,command)),stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
        code=proc.returncode
    except subprocess.TimeoutExpired:
        code=124
    PHASES.append(dict(name=name,code=code,seconds=time.monotonic()-start))
    save(OUT/'phases.json',PHASES)
    print('END',name,code,flush=True)
    require(not required or code==0,'Required phase failed: '+name)
    return code

def esp(name,*args):
    return run(name,[sys.executable,'-m','esptool','--chip','esp32c3','--port',PORT,
        '--before','usb-reset','--after','no-reset',*args],required=True,timeout=180,private=True)

def reset(name):
    run(name,['pwsh.exe','-NoProfile','-File',
        '.agents/skills/flash-reset-esp32c3-oled/scripts/reset_esp32c3_oled.ps1',
        '-Port',PORT,'-PythonPath',sys.executable],required=True,timeout=50,private=True)

def ready(expected,timeout=45):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        try:
            info=BOARD.info()
            if info.get('app_elf_sha256')==expected:
                BOARD.status();return info
        except (OSError,ValueError):pass
        time.sleep(.5)
    raise RuntimeError('Expected application did not return')

def capture_probe(mode,image,label):
    lines=[]; closed=threading.Event()
    port=serial.Serial(port=None,baudrate=115200,timeout=.2)
    port.dtr=port.rts=False;port.port=PORT;port.open()
    def read():
        for line in serial_lines(port,closed):
            if line.startswith('FLASH_PROBE_'):
                lines.append(line)
    reader=threading.Thread(target=read,daemon=True);reader.start()
    end=time.monotonic()+30
    while time.monotonic()<end and not any(x.startswith(('FLASH_PROBE_PASS','FLASH_PROBE_FAIL')) for x in lines):
        time.sleep(.1)
    closed.set();reader.join(2);port.close()
    text='\n'.join(lines)+'\n';(OUT/(label+'.log')).write_text(text)
    result=validate(text,image.read_bytes(),mode)
    result['identity']=ready(image_info(image.read_bytes())['app_elf_sha256'])
    save(OUT/(label+'.json'),result)

def runner(mode,label,suites,extra=()):
    image=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flash-{mode}80/app.bin')
    command=[sys.executable,'-X','utf8','tools/esp32c3_tests/diagnostic.py','run',
        '--board',BOARD.origin,'--host',HOST,'--serial-port',PORT,'--output',OUT/mode/label,
        '--sdkconfig',image.with_name('sdkconfig'),'--leave-stopped','--unpaced-files','--delivery-stats']
    for suite in suites:command+=['--suite',suite]
    command+=list(extra)
    return run(mode+'/'+label,command)

require(not OUT.exists() and not PRIVATE.exists(),'Keep earlier evidence')
OUT.mkdir();PRIVATE.mkdir()
initial=BOARD.status();identity=BOARD.info();before=snapshot(BOARD)
expected=image_info(QUIET.read_bytes())['app_elf_sha256']
require(identity['app_elf_sha256']==expected,'Unexpected initial firmware')
save(OUT/'initial.json',dict(identity=identity,status=initial))
backed=False;written=False
try:
    BOARD.stop()
    esp('flash-status-before','read-flash-status','--bytes','2')
    esp('backup','read-flash','0','0x400000',PRIVATE/'original-flash.bin')
    original=(PRIVATE/'original-flash.bin').read_bytes()
    require(len(original)==0x400000,'Incomplete flash backup')
    entries={}
    for offset in range(0x8000,0x9000,32):
        raw=original[offset:offset+32]
        if raw[:2]!=b'\xaaP':break
        magic,kind,sub,address,size,label,flags=struct.unpack('<HBBII16sI',raw)
        entries[label.split(b'\0')[0].decode()]=dict(type=kind,subtype=sub,address=address,size=size)
    require(entries['app0']['address']==0x10000 and entries['app1']['address']==0x1e0000 and
            all(entries[n]['size']==0x1d0000 for n in ('app0','app1')) and
            entries['nvs']['address']==0x9000 and entries['otadata']['address']==0xe000 and
            entries['spiffs']['address']==0x3b0000,'Unexpected partition layout')
    require(original[0x10000:0x10000+QUIET.stat().st_size]==QUIET.read_bytes(),'Active application differs from saved image')
    for name,start,end in [('boot',0,0x8000),('otadata',0xe000,0x10000),('apps',0x10000,0x3b0000)]:
        (PRIVATE/('original-'+name+'.bin')).write_bytes(original[start:end])
    save(OUT/'partition-layout.json',entries)
    backed=True
    for mode in ('dio','qio'):
        image=Path(f'firmware/development/esp32c3-idf-6.1-r9a97-flash-{mode}80/app.bin')
        boot=image.with_name('bootloader.bin')
        slot=identity['partition'] if mode=='dio' else BOARD.info()['partition']
        address=entries[slot]['address']
        require(image.stat().st_size<=entries[slot]['size'] and boot.stat().st_size<=0x8000,'Image exceeds verified region')
        written=True
        esp(mode+'-install','write-flash','--flash-mode','keep','--flash-freq','keep','--flash-size','keep',
            '0x0',boot,hex(address),image)
        reset(mode+'-start')
        capture_probe(mode,image,mode+'-boot-1')
        reset(mode+'-repeat')
        capture_probe(mode,image,mode+'-boot-2')
        # Run finite files before stress; both AUTO and explicit codecs are included.
        runner(mode,'matrix',['http','https'],[
            '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem','--tls-key',TRUST/'server.key'])
        runner(mode,'transitions-faults-websocket',['transitions','faults','websocket'])
        runner(mode,'switch',['switch'],['--cycles','3','--case','lc-48000-stereo',
            '--case','he-48000-stereo','--case','hev2-44100-stereo','--case','flac-level8'])
        runner(mode,'heavy-flac',['load'],['--case','stress-flac-48000-2ch-16bit-610s',
            '--fixture-manifest','.build/c3-reserve-soak-20261008/fixtures/manifest.json',
            '--load-seconds','60','--load-idle-recovery','--sustained-protocol','https',
            '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem','--tls-key',TRUST/'server.key'])
        runner(mode,'hev2-ten-minutes',['load'],['--case','hev2-44100-stereo',
            '--load-seconds','600','--load-idle-recovery','--sustained-protocol','https',
            '--https-origin','https://'+HOST+':8771','--tls-cert',TRUST/'server.pem','--tls-key',TRUST/'server.key'])
        run(mode+'/ota',[sys.executable,'-X','utf8','tools/esp32c3_tests/ota.py',
            '--board',BOARD.origin,'--firmware',image,'--suite','negative','--suite','roundtrip',
            '--suite','slow','--output',OUT/(mode+'-ota.json')])
        runner(mode,'boot-ready',['boot-time'],['--cycles','5'])
        save(OUT/(mode+'-settings.json'),verify_snapshot(BOARD,before))
finally:
    if backed and written:
        # Restore only regions changed by bootloader/application/OTA testing.
        # NVS, the partition table and SPIFFS are never written here.
        esp('restore','write-flash','--flash-mode','keep','--flash-freq','keep','--flash-size','keep',
            '0x0',PRIVATE/'original-boot.bin','0xe000',PRIVATE/'original-otadata.bin',
            '0x10000',PRIVATE/'original-apps.bin')
        esp('readback','read-flash','0','0x400000',PRIVATE/'restored-readback.bin')
        esp('flash-status-after','read-flash-status','--bytes','2')
        readback=(PRIVATE/'restored-readback.bin').read_bytes()
        same=readback==original
        save(OUT/'flash-restoration.json',dict(full_flash_equal=same,
            boot_equal=readback[:0x8000]==original[:0x8000],
            partition_table_equal=readback[0x8000:0x9000]==original[0x8000:0x9000],
            nvs_equal=readback[0x9000:0xe000]==original[0x9000:0xe000],
            otadata_equal=readback[0xe000:0x10000]==original[0xe000:0x10000],
            apps_equal=readback[0x10000:0x3b0000]==original[0x10000:0x3b0000],
            spiffs_equal=readback[0x3b0000:0x3f0000]==original[0x3b0000:0x3f0000]))
    reset('restore-start')
    final=ready(expected)
    if not initial['audio']:BOARD.stop()
    states=[]
    for _ in range(3):
        time.sleep(5);states.append(BOARD.status())
    restored=dict(identity=final,status=states,persistence=verify_snapshot(BOARD,before),
        playback_restored=all(s['audio']==initial['audio'] for s in states))
    save(OUT/'final-board.json',restored)
    require(restored['playback_restored'],'Initial playback not restored')
print('QIO_RECHECK_FINISHED',flush=True)
