from collections import Counter
import re
import runpy
import sys
from common import *
from esptool.bin_image import LoadFirmwareImage

backend=sys.argv[1]; directory=BASE/backend; row=load(directory/'baseline.json'); prep=load(BASE/'preflight.json')
cache=ROOT/row['cache']; rtc_on=ROOT/row['rtc_on']; clang=BASE/'clang-shared'
helpers=runpy.run_path(str(ROOT/'.build/cyd-final-campaign-20261111-01/campaign.py'))
config=load(cache/'config/sdkconfig.json'); before_config=load(rtc_on/'compiled/config/sdkconfig.json')
delta=helpers['delta'](before_config,config)
assert delta==dict(YORADIO_WS_STATUS_RTC_SLOW=dict(before_present=True,before=True,after_present=True,after=False))
old_header=(directory/'baseline/sdkconfig.h').read_bytes(); header=(cache/'config/sdkconfig.h').read_bytes()
line=b'#define CONFIG_YORADIO_WS_STATUS_RTC_SLOW 1\r\n'
assert old_header.count(line)==1 and old_header.replace(line,b'')==header,'Unexpected generated header delta'
old_generated=load(rtc_on/'baseline.json')['generated_headers']
for item in old_generated:
    if item['path']!='config/sdkconfig.h':
        assert pin(cache/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256'])
entries=load(cache/'compile_commands.json')
assert {x['output']:x for x in entries}=={x['output']:x for x in load(directory/'baseline/compile_commands.json')}
changed_raw=[]; changed_allocated=[]; ws_object=None
for item in row['objects']:
    path=ROOT/item['path']; after=pin(path)
    if after!=item['identity']: changed_raw.append(dict(path=item['path'],before=item['identity'],after=after))
    signature=alloc_signature(path)
    if signature!=item['allocated']: changed_allocated.append(item['path'])
    if Path(item['source']).name=='websocket_service.c': ws_object=item['path']
assert changed_allocated==[ws_object],'Unexpected allocated code/data/relocation change outside workspace TU'
write(directory/'object-comparison.json',dict(objects=len(row['objects']),changed_raw=changed_raw,
    changed_allocated=changed_allocated,other_allocated_sections_and_relocations_identical=True,
    scope='Raw debug/metadata differences are retained separately from allocated code/data and related relocations. Only WS TU allocation changes are allowed.'))
assert pin(cache/'openeth-rx-overlay/esp_eth_mac_openeth.c')['sha256']==prep['generated_sha256']
image_file=directory/'fixture/yoradio_cyd2usb_native.bin'; body=image_file.read_bytes(); image=LoadFirmwareImage('esp32',body)
assert image.chip_id==image.ROM_LOADER.IMAGE_CHIP_ID and image.calculate_checksum()==image.checksum
assert image.append_digest and image.stored_digest==image.calc_digest and len(body)==image.data_length+32
assert body[:24]==(rtc_on/'fixture/yoradio_cyd2usb_native.bin').read_bytes()[:24]
elf_file=directory/'compiled/yoradio_cyd2usb_native.elf'
assert image.segments[0].data[144:176].hex()==pin(elf_file)['sha256']
appdesc=bytearray(image.segments[0].data[:256]); appdesc[144:176]=bytes(32)
old_appdesc=bytearray.fromhex(row['original_app_descriptor_hex']); old_appdesc[144:176]=bytes(32)
assert appdesc==old_appdesc
for path in (rtc_on/'fixture').rglob('*'):
    if path.is_file() and path.relative_to(rtc_on/'fixture').as_posix() not in ('yoradio_cyd2usb_native.bin','config/sdkconfig.json'):
        assert pin(path)==pin(directory/'fixture'/path.relative_to(rtc_on/'fixture'))
exporter=runpy.run_path(str(ROOT/'tools/export_cyd_production.py'))
slots=exporter['partition_slots']((directory/'fixture/partition_table/partition-table.bin').read_bytes(),4*1024**2)
assert len(slots)==2 and all(s['bytes']==0x1b0000 and len(body)<s['bytes'] for s in slots)
with elf_file.open('rb') as stream:
    elf=ELFFile(stream); table=elf.get_section_by_name('.symtab'); assert elf['e_machine']=='EM_XTENSA'
    value=lambda name:table.get_symbol_by_name(name)[0]['st_value']
    reserve=elf.get_section_by_name('.rtc_slow_reserved')
    geometry=dict(rtc_slow_used_bytes=value('_rtc_slow_length'),rtc_slow_reserved_bytes=reserve['sh_size'],
        rtc_slow_free_bytes=reserve['sh_addr']-value('_rtc_force_slow_end'),heap_start=value('_heap_start'),
        dram_bss_bytes=elf.get_section_by_name('.dram0.bss')['sh_size'])
    assert geometry['rtc_slow_used_bytes']==104 and geometry['rtc_slow_reserved_bytes']==24 and geometry['rtc_slow_free_bytes']==8064
    assert geometry['heap_start']-row['geometry']['heap_start']==6560
    assert geometry['dram_bss_bytes']-row['geometry']['dram_bss_bytes']==6560
    storage={}
    for name,size in (('s_status',5120),('s_previous',508),('s_current',508),('s_clients',384),('s_sockets',40),
        ('s_running',1),('s_work_pending',4),('s_producers',4),('s_playlist_revision',4),('s_poll_timer',4),('s_display',5168)):
        sym,=[s for s in table.get_symbol_by_name(name) if s['st_info']['type']=='STT_OBJECT']
        assert sym['st_size']==size and elf.get_section(sym['st_shndx']).name=='.dram0.bss'
        storage[name]=dict(bytes=size,address=sym['st_value'],section='.dram0.bss')
    probe,=[s for s in table.get_symbol_by_name('s_probe') if s['st_info']['type']=='STT_OBJECT']
    assert probe['st_size']==64 and 0x50000000<=probe['st_value']<probe['st_value']+64<=0x50002000
    probe_proof=dict(bytes=64,address=probe['st_value'],section=elf.get_section(probe['st_shndx']).name)
objdump=DEP/'tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32-elf-objdump.exe'
subprocess.run(list(map(str,[sys.executable,'-B',ROOT/'tests/check-cyd-ogg-stack.py','--elf',elf_file,'--objdump',objdump,'--output',directory/'stack-frame.json'])),check=True)
stack=load(directory/'stack-frame.json'); assert stack['passed'] and stack['frame_bytes']==dict(decoder_task=1760,ogp_decode_word_page=2144)
compiler_delta=helpers['delta'](config,load(clang/'config/sdkconfig.json'))
assert compiler_delta==load(rtc_on/'compiler-config-delta.json')
write(directory/'compiler-config-delta.json',compiler_delta); write(directory/'rtc-config-delta.json',delta)
tidy=DEP/'tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe'
diagnostic=re.compile(r'^(.*?):(\d+):(\d+): (warning|error): (.*?)(?: \[([^\]]+)\])?$',re.M)
lint=[]
for label,name in (('websocket','websocket_service.c'),('openeth','esp_eth_mac_openeth.c')):
    entry,=[x for x in load(clang/'compile_commands.json') if Path(x['file']).name==name]
    source=Path(entry['file']); output=directory/('lint-'+label); output.mkdir()
    header_filter='.*' if label=='openeth' else re.escape(ROOT.as_posix()).replace('/',r'[/\\]')+r'[/\\]'
    with (output/'stdout.log').open('xb') as out,(output/'stderr.log').open('xb') as err:
        code=subprocess.run(list(map(str,[tidy,source,'-p',clang,'--config-file='+str(ROOT/'.clang-tidy'),
            '--header-filter='+header_filter,'--export-fixes='+str(output/'fixes.yaml')])),cwd=entry['directory'],stdout=out,stderr=err).returncode
    text=(output/'stdout.log').read_text(errors='replace')+(output/'stderr.log').read_text(errors='replace'); sites=[]
    for m in diagnostic.findall(text):
        file='SDK/openeth/esp_eth_mac_openeth.c' if label=='openeth' and Path(m[0]).resolve()==source.resolve() else m[0]
        sites.append(dict(file=file,line=int(m[1]),column=int(m[2]),severity=m[3],message=m[4],check=m[5]))
    if label=='openeth': previous=load(rtc_on/'lint-after/report.json')['diagnostics']
    else:
        old_report=load(ROOT/'.build/cyd-ws-normal-production-20261124'/('vendor-'+backend)/'lint/report.json')
        previous,=[r['diagnostics'] for r in old_report['results'] if Path(r['file']).name==name]
    catalog=lambda values:Counter((v['file'],v['severity'],v['message'],v['check']) for v in values)
    same_catalog=catalog(previous)==catalog(sites)
    report=dict(whole_tu=True,returncode=code,source=pin(source),config=pin(clang/'config/sdkconfig.json'),
        warnings=sum(x['severity']=='warning' for x in sites),errors=sum(x['severity']=='error' for x in sites),
        diagnostics=sites,warning_catalog_unchanged=same_catalog)
    write(output/'report.json',report); assert code==0 and not report['errors'] and same_catalog
    lint.append(dict(unit=label,warnings=report['warnings'],errors=0))
guard(prep,row)
write(directory/'qualification.json',dict(passed=True,physical_tested=False,native_run=False,backend=backend,
    rtc_workspace=False,rtc_probe_enabled=True,source_commit=SOURCE,image=pin(image_file),elf=pin(elf_file),
    effective_config_delta=delta,generated_header_delta='Only CONFIG_YORADIO_WS_STATUS_RTC_SLOW removed',
    object_count=len(row['objects']),changed_raw_object_count=len(changed_raw),changed_allocated=changed_allocated,
    geometry=geometry,workspace_and_controls=storage,rtc_probe=probe_proof,static_frames=stack['frame_bytes'],lint=lint,
    descriptor_context='Original A/B PROJECT_VER/date preserved; not a clean new production release.',ota_slots=slots))
print('QUALIFIED RTC-OFF '+backend,flush=True)
