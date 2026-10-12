#!/usr/bin/env python3
"""Capture both unmodified Small TV applications with matching synthetic settings.

Only working flash copies are seeded. No guest instructions, PC or RAM are
patched. Run with the Python bundled in the repository's ESP-IDF environment.
"""
import argparse
import concurrent.futures
import datetime as dt
import json
from pathlib import Path
import re
import struct
import sys
import time
from types import SimpleNamespace


def seed_settings(data, variant, state, yoradio):
    """Replace private state with the same explicit factory-format preferences."""
    data = bytearray(data)
    data[0x9000:0xf000] = b'\xff' * 0x6000
    raw = bytearray(4096)
    for offset, width, value in [(4,65,'yoRadio-QEMU'), (0x45,65,''),
            (0x86,65,'10.0.2.2'), (0xc7,20,'CN'), (0xdb,65,'Shenzhen'),
            (0x11c,65,'disabled')]:
        raw[offset:offset+width] = value.encode().ljust(width,b'\0')
    values = [2 if state.name.startswith('setup-') else 1, 0, THEMES[CURRENT_THEME],
              0,0,0,0,2,0,0xf800,0xffe0,0xffff,0,22,9,500,5,
              CURRENT_PHOTO_MASK if CURRENT_THEME=='photo' else 31]
    struct.pack_into('<18I',raw,0x160,*values)
    struct.pack_into('<I',raw,0,values[-1])
    if variant == 'original':
        # These five public media lengths differ from sanitized JPEGs by their
        # removed metadata bytes; use each image's complete original length.
        lengths = struct.unpack_from('<5I',data,0x3e7000+0x1a8)
    else:
        pack = json.loads((Path(yoradio)/'firmware/development/small-tv-esp32c2-reconstructed/assets-manifest.json').read_text())
        lengths = [item['size'] for item in pack['records'][:5]]
    struct.pack_into('<5I',raw,0x1a8,*lengths)
    data[0x3e7000:0x3e8000] = raw
    return data


def virtual_seconds(qmp):
    """Read elapsed virtual time from the emulated radio microsecond counter."""
    value = qmp.execute('human-monitor-command', **{'command-line':'xp /1wx 0x6004d000'})
    return int(re.findall(r'0x([0-9a-fA-F]{8})\b',value)[0],16)/1e6


def capture(variant, args, theme):
    """Boot, capture a complete scene and always stop this test VM."""
    state = args.state / (theme+'-'+variant)
    options = SimpleNamespace(firmware=variant,yoradio=str(args.yoradio),
        qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.yoradio/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        persistent=False,network='clock',display='none',gdb_port=0,paused=False,
        hardware_profile=str(args.qemu_root/'configs/boards/small-tv-c2.json'))
    session, prepared = vm.launch(options,state)
    try:
        with vm.QMP(session['qmp_port'],session['name']) as qmp:
            deadline = time.monotonic()+180
            while virtual_seconds(qmp)<args.virtual_seconds:
                if time.monotonic()>deadline:
                    raise TimeoutError('Guest did not reach the requested virtual time')
                time.sleep(.5)
            # Keep several actual captures to expose partial SPI redraws rather
            # than treating a single interrupted transfer as a graphics defect.
            captures=[]
            for index in range(3):
                target=args.virtual_seconds+index*3
                while virtual_seconds(qmp)<target:
                    if time.monotonic()>deadline:
                        raise TimeoutError('Guest stalled during captures')
                    time.sleep(.5)
                image=args.output/f'{theme}-{variant}-{index}.png'
                vm.capture_png(qmp,image)
                captures.append(vm.ppm_pixels(image.with_suffix('.ppm')))
                image.with_suffix('.ppm').unlink()
                time.sleep(.5)
            elapsed=virtual_seconds(qmp)
        uart=(state/'uart.log').read_text(errors='replace')
        return {'variant':variant,'virtual_seconds':elapsed,
                'no_panic':not any(word in uart for word in ['Guru Meditation','assert failed','abort() was called']),
                'ntp_reply':'C2 NTP reply' in (state/'qemu.log').read_text(errors='replace'),
                'qemu_sha256':vm.digest(Path(options.qemu).read_bytes()),
                'source':prepared['sources'],'captures':captures}
    finally:
        vm.control(state,'stop')


THEMES={'setup':0,'classic':0,'simple':1,'photo':2,'dial':3}
CURRENT_THEME='classic'
CURRENT_PHOTO_MASK=1


def static_pixels(theme):
    """Select fixed scene pixels, excluding live digits, hands and animation."""
    pixels=[]
    for y in range(240):
        for x in range(240):
            dynamic=(theme=='classic' and ((x<160 and 80<=y<144) or (x>=160 and y>=160)))
            dynamic=dynamic or (theme=='simple' and 10<=x<230 and 80<=y<160)
            dynamic=dynamic or (theme=='dial' and (x-120)**2+(y-120)**2<=96**2)
            if not dynamic:
                pixels.append((y*240+x)*3)
    return pixels


def main():
    """Run selected scenes and record measured differences without a parity claim."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,default=Path('C:/Work/QEMU-ESP32'))
    parser.add_argument('--yoradio',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--state',type=Path)
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--themes',nargs='+',choices=list(THEMES),default=list(THEMES))
    parser.add_argument('--virtual-seconds',type=float,default=40)
    parser.add_argument('--photo-mask',type=int,default=1,choices=range(32),
                        help='Default isolates the first photo to remove slideshow phase ambiguity')
    args=parser.parse_args()
    args.state=args.state or args.yoradio/'.build/small-tv-parity/vms'
    args.output.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(args.qemu_root/'tools'))
    global vm, CURRENT_THEME, CURRENT_PHOTO_MASK
    import small_tv_vm as vm
    vm.seed_clock_network=seed_settings
    CURRENT_PHOTO_MASK=args.photo_mask
    report={'tested_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'scenes':{},
            'photo_mask':args.photo_mask,
            'notes':['Matching synthetic preferences; disabled weather key; isolated QEMU NTP network.',
                     'Captures are real SPI framebuffer output. Capture times and animation phases vary.',
                     'Whole-frame equality is measured, not asserted. See README for remaining differences.']}
    for theme in args.themes:
        CURRENT_THEME=theme
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            original,reconstructed=list(pool.map(lambda variant:capture(variant,args,theme),['original','reconstructed']))
        # Compare all consecutive captures; retain both the best and worst
        # measurements so movement/partial redraws are visible in the report.
        ratios=[]; static_ratios=[]; fixed=static_pixels(theme)
        for left in original.pop('captures'):
            for right in reconstructed['captures']:
                ratios.append(sum(left[i:i+3]==right[i:i+3] for i in range(0,len(left),3))/57600)
                static_ratios.append(sum(left[i:i+3]==right[i:i+3] for i in fixed)/len(fixed))
        reconstructed.pop('captures')
        report['scenes'][theme]={'original':original,'reconstructed':reconstructed,
                                'equal_pixels_min':min(ratios),'equal_pixels_max':max(ratios),
                                'static_pixels':len(fixed),'static_equal_min':min(static_ratios),
                                'static_equal_max':max(static_ratios)}
        print(theme,':',round(max(ratios)*100,2),'% equal pixels',flush=True)
        vm.save_json(args.output/'comparison.json',report)


if __name__=='__main__':
    main()
