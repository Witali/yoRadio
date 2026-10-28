"""Actual C2 main-app bootstrap: legacy/torn/foreign layouts and protected bytes."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace
from elftools.elf.elffile import ELFFile

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Small_TV/src/tests'))
from photo_owner_qemu import process_handle
from qemu_storage import direct_flash_backing
import weather_qemu as weather

def sha(path):
    """Identify real firmware/emulator/test bytes, not a build-directory label."""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compiled_layout(elf_path):
    """Read actual storage address and type offsets from the exact linked ELF."""
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        symbols=[s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name=='storage' and s['st_value']]
        assert len(symbols)==1
        names={'jpeg_espidf_t','jpeg_transport_t','jpeg_transport_usage_t'};layouts={}
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name=die.attributes.get('DW_AT_name')
                if die.tag!='DW_TAG_typedef' or not name or name.value.decode(errors='replace') not in names:continue
                key=name.value.decode()
                while die.tag!='DW_TAG_structure_type' and 'DW_AT_type' in die.attributes:
                    die=die.get_DIE_from_attribute('DW_AT_type')
                fields={c.attributes['DW_AT_name'].value.decode():c.attributes['DW_AT_data_member_location'].value
                    for c in die.iter_children() if c.tag=='DW_TAG_member'}
                if fields:layouts[key]=fields
            if set(layouts)==names:break
        assert set(layouts)==names
        return dict(storage=symbols[0]['st_value'],fields=layouts)

def observe(qmp,layout):
    """Read only the identified transport capability/counter fields; no guest calls."""
    fields=layout['fields'];base=layout['storage']+fields['jpeg_espidf_t']['transport']
    get=lambda address,count:int.from_bytes(weather.read_bytes(qmp,address,count),'little')
    result={name:get(base+fields['jpeg_transport_t'][name],1) for name in ('authorized','active')}
    result['usage']={name:get(base+fields['jpeg_transport_t']['usage']+offset,8)
                     for name,offset in fields['jpeg_transport_usage_t'].items()}
    result['last_error']=get(base+fields['jpeg_transport_t']['last_error'],4)
    return result

def main():
    """Own/reap every fresh VM, retaining exact pre/post physical flash images."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu-root',type=Path,required=True)
    parser.add_argument('--dependency-root',type=Path,default=Path('C:/Work/yoRadio'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    frozen=json.loads((args.qemu_root/'frozen-inputs.json').read_text())
    for row in frozen['files']:assert sha(args.qemu_root/row['file'])==row['sha256']
    sys.path.insert(0,str(args.qemu_root/'tools'));import small_tv_vm as vm
    from small_tv_http_test import http,wait_http,clean_uart
    weather.vm=vm
    archive=ROOT/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest=json.loads((archive/'manifest.json').read_text());plan=json.loads((archive/'jpeg-cache-plan.json').read_text())
    elf=ROOT/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    assert sha(elf)==manifest['elf_sha256'];layout=compiled_layout(elf)
    assets=(archive/'assets.bin').read_bytes();stamp_offset=plan['guard_ownership']['authority']['stamp']['offset']
    expected=assets[stamp_offset-0x200000:stamp_offset-0x200000+64];assert expected[:8]==b'STVOWN1\0'
    previous_proof=ROOT/'Small_TV/qemu/parity/jpeg-main-integration-validation-20261023.json'
    previous=json.loads(previous_proof.read_text())
    saved=next(x for x in previous['raw'] if x['source']=='.build/photo-owner-20261023/qemu-service-floor/flash-after-1.bin')
    previous_image=previous_proof.parent/saved['file'];previous_flash=gzip.decompress(previous_image.read_bytes())
    assert hashlib.sha256(previous_flash).hexdigest()==saved['sha256'] and len(previous_flash)==0x400000
    inputs={str(p.resolve()):sha(p) for p in [Path(__file__),ROOT/'Small_TV/src/tests/photo_owner_qemu.py',
        ROOT/'Small_TV/src/tests/weather_qemu.py',elf,*[archive/n for n in ('manifest.json','source-manifest.json',
        'app.bin','bootloader.bin','partition-table.bin','assets.bin','jpeg-cache-plan.json')],previous_proof,previous_image]}
    report=dict(passed=False,all_functionality_verified=False,lcd_tested=False,rf_tested=False,
        network_acceptance=False,hardware_tested=False,app_sha256=next(x['sha256'] for x in manifest['images'] if x['file']=='app.bin'),
        elf_sha256=sha(elf),source_sha256=manifest['source_sha256'],qemu_sha256=sha(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        inputs_sha256=inputs,compiled_observation_layout=layout,cases=[])
    fixture=weather.WeatherFixture();fixture.set_response(200)
    options=SimpleNamespace(yoradio=str(ROOT),firmware='reconstructed',qemu=str(args.qemu_root/'bin/qemu-system-riscv32.exe'),
        rom_elf=str(args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf'),
        hardware_profile=str(ROOT/'Small_TV/qemu/profiles/small-tv-c2.json'),network='clock',display='none',
        persistent=True,paused=True,gdb_port=0,http_base_port=0,service_port=fixture.port)
    original_seed=vm.seed_clock_network;session=handle=kernel=None;state=None
    try:
        for case in ('erased','torn','id-written','torn-header','occupied','foreign-stamp','foreign-compatible',
                     'bad-resource','bad-flags','owned-nonempty','upgrade-real'):
            def seed(data,firmware,state,yoradio,ssid=None):
                """Mutate only the disposable PREBOOT fixture; never guest RAM/PC/code."""
                data=bytearray(original_seed(data,firmware,state,yoradio,ssid))
                if case=='upgrade-real':
                    # Real retained old-main NVS/photos/cache; replace ONLY the
                    # application before boot. Dial/mask are declared synthetic
                    # preferences below to prevent unrelated cache warm-up writes.
                    data=bytearray(previous_flash)
                    app=(archive/'app.bin').read_bytes();data[0x10000:0x10000+len(app)]=app
                struct.pack_into('<I',data,0x3e7000+0x168,3) # Ordinary user-selected dial theme.
                struct.pack_into('<I',data,0x3e7000+0x1a4,0) # No automatic photo-cache jobs.
                if case!='upgrade-real':
                    data[0x27cfe0:0x27d000]=bytes(range(32)) # Synthetic user slot-tail bytes.
                if case=='owned-nonempty':
                    for extent in plan['candidate_extents']:
                        data[extent['offset']:extent['offset']+extent['bytes']]=b'\x35'*extent['bytes']
                elif case!='upgrade-real':data[stamp_offset:stamp_offset+64]=b'\xff'*64
                if case=='torn':
                    data[stamp_offset+8:stamp_offset+40]=bytes(value|((i*73+51)&255) for i,value in enumerate(expected[8:40]))
                    assert data[stamp_offset+8:stamp_offset+40] not in (expected[8:40],b'\xff'*32)
                elif case in ('id-written','torn-header'):
                    data[stamp_offset+8:stamp_offset+40]=expected[8:40]
                    if case=='torn-header':
                        data[stamp_offset:stamp_offset+8]=bytes(value|((i*73+51)&255) for i,value in enumerate(expected[:8]))
                        assert data[stamp_offset:stamp_offset+8] not in (expected[:8],b'\xff'*8)
                elif case=='occupied':
                    extent=plan['candidate_extents'][-1];data[extent['offset']+extent['bytes']-1]=0xfe
                elif case=='foreign-stamp':data[stamp_offset+63]=0xfe
                elif case=='foreign-compatible':data[stamp_offset:stamp_offset+8]=expected[:8]
                elif case=='bad-resource':data[0x27d000]^=1
                elif case=='bad-flags':
                    struct.pack_into('<I',data,0x8000+3*32+28,0x80000000)
                    data[0x8000+4*32+16:0x8000+4*32+32]=hashlib.md5(data[0x8000:0x8000+4*32]).digest()
                return data
            vm.seed_clock_network=seed
            state=args.output/case;state.mkdir()
            for boot in range(2 if case=='erased' else 1):
                session,prepared=vm.launch(options,state);kernel,handle=process_handle(session['pid'])
                before=(state/'flash.bin').read_bytes();(state/f'before-{boot}.bin').write_bytes(before)
                with vm.QMP(session['qmp_port'],session['name']) as qmp:
                    assert direct_flash_backing(qmp,state);qmp.execute('cont')
                url=session['web_urls']['station'];wait_http(url,'/getclocktype',expected=b'3')
                with vm.QMP(session['qmp_port'],session['name']) as qmp:observed=observe(qmp,layout)
                authorized=case in ('erased','torn','id-written','torn-header','owned-nonempty','upgrade-real')
                assert bool(observed['authorized'])==authorized,(case,observed)
                assert observed['active']==0 and observed['usage']['erase_calls']==0,(case,observed)
                programmed=40 if case in ('erased','torn') and boot==0 else 8 if case in ('id-written','torn-header') else 0
                assert observed['usage']['program_bytes']==programmed,(case,observed)
                status,body=http(url,'/get_Photo_File?file=5&chunk=0&size=0');assert status==200 and json.loads(body)['exists']
                assert clean_uart(state)
                row=dict(case=case,boot=boot,session=session,observation=observed,expected_authorized=authorized,owners_stopped=False)
                report['cases'].append(row)
                (state/f'uart-{boot}.log').write_bytes((state/'uart.log').read_bytes())
                vm.control(state,'stop');assert kernel.WaitForSingleObject(handle,10000)==0
                kernel.CloseHandle(handle);handle=None;session=None;row['owners_stopped']=True
                after=(state/'flash.bin').read_bytes();(state/f'after-{boot}.bin').write_bytes(after)
                target=bytearray(before)
                if programmed:target[stamp_offset:stamp_offset+64]=expected
                # SDK may initialize NVS/RF calibration. Everything else, including
                # all preferences/photos/unused candidate bytes, must be EXACT.
                assert after[:0x9000]==target[:0x9000] and after[0xf000:]==target[0xf000:],case
                if boot or case=='upgrade-real':assert after[0x9000:0xf000]==before[0x9000:0xf000],case
                row.update(protected_bytes_exact=True,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest())
                print('PASS actual main bootstrap:',case,'boot',boot,'authorized',authorized,'stamp bytes',programmed,flush=True)
        assert all(sha(Path(p))==digest for p,digest in inputs.items())
        report['passed']=True
    except Exception as error:
        report['error']=type(error).__name__+': '+str(error);raise
    finally:
        if session:
            for name in ('uart.log','qemu.log','session.json'):
                if (state/name).exists():(state/('failure-'+name)).write_bytes((state/name).read_bytes())
            if not handle or kernel.WaitForSingleObject(handle,0)!=0:vm.control(state,'stop')
            if handle:assert kernel.WaitForSingleObject(handle,10000)==0;kernel.CloseHandle(handle)
        vm.seed_clock_network=original_seed;fixture.close()
        vm.save_json(args.output/'report.json',report)
    print('PASS main legacy provisioning:',len(report['cases']),'owned cold processes, protected bytes exact')

if __name__=='__main__':main()
