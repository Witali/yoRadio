import hashlib,io,json,re,runpy,struct,subprocess,sys,zipfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from esptool.bin_image import LoadFirmwareImage
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[1]; DEP=Path('C:/Work/yoRadio/.idf')
backend=sys.argv[1]; d=BASE/'sdk'/backend; before=BASE/'sdk-baseline'/backend
candidate=json.loads((BASE/'candidate-inputs.json').read_bytes()); row=json.loads((before/'snapshot.json').read_bytes())
cache=ROOT/row['cache']; old=ROOT/'.build/cnortc24'/backend
def load(p): return json.loads(Path(p).read_bytes())
def pin(p):
 b=Path(p).read_bytes(); return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def ident(b): return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,value):
 assert not p.exists(); p.write_text(json.dumps(value,indent=2)+'\n')
assert not (d/'static-qualification.json').exists()
assert load(d/'build-status.json')['state']=='BUILD_PASS_QUALIFICATION_PENDING'
assert load(d/'compiled/config/sdkconfig.json')==load(before/'sdkconfig.json')
assert (d/'compiled/config/sdkconfig.h').read_bytes()==(before/'sdkconfig.h').read_bytes()
for name,value in candidate['sources'].items(): assert pin(ROOT/name)==value
for item in candidate['protected']: assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256'])
for folder,commit in candidate['sdk_repositories'].items():
 assert subprocess.check_output(['git','-C',str(DEP/folder),'rev-parse','HEAD'],text=True).strip()==commit
 assert not subprocess.check_output(['git','-c','core.longpaths=true','-C',str(DEP/folder),'status','--porcelain','--untracked-files=no'])
helpers=runpy.run_path(str(ROOT/'.build/cyd-final-campaign-20261111-01/campaign.py'))
old_entries=load(before/'compile_commands.json'); entries=load(d/'compiled/compile_commands.json')
old_by={x['output']:x for x in old_entries}; new_by={x['output']:x for x in entries}; marker='-DCYD_OPENETH_PBUF_FAILURE_PROBE=1'
added=set(new_by)-set(old_by); assert len(added)==1 and not set(old_by)-set(new_by)
new_probe=new_by[next(iter(added))]; assert Path(new_probe['file']).name=='pbuf_failure.c'
main_command_changes=[]
for name,entry in old_by.items():
 after=new_by[name]; a=helpers['entry_tokens'](entry); b=helpers['entry_tokens'](after)
 assert all(entry[k]==after[k]for k in ('directory','file','output'))
 main=Path(name).as_posix().startswith('esp-idf/main/')
 assert b.count(marker)==int(main) and marker not in a
 assert [x for x in b if x!=marker]==a
 if main: main_command_changes.append(name)
def allocated(body):
 e=ELFFile(io.BytesIO(body)); result={}
 for s in e.iter_sections():
  rel=s['sh_type']in('SHT_REL','SHT_RELA')and bool(e.get_section(s['sh_info'])['sh_flags']&2)
  if s['sh_flags']&2 or rel:
   result[s.name]=dict(type=s['sh_type'],flags=s['sh_flags'],bytes=s['sh_size'],sha256=None if s['sh_type']=='SHT_NOBITS'else hashlib.sha256(s.data()).hexdigest())
   if rel:
    symbols=e.get_section(s['sh_link']); refs=[]
    for r in s.iter_relocations():
     sym=symbols.get_symbol(r['r_info_sym']); index=sym['st_shndx']; section=e.get_section(index).name if isinstance(index,int)else index
     refs.append((r['r_offset'],r['r_info_type'],r.entry.get('r_addend'),sym.name,sym['st_value'],sym['st_size'],sym['st_info']['type'],sym['st_info']['bind'],section))
    result[s.name]['symbol_references_sha256']=hashlib.sha256(json.dumps(refs).encode()).hexdigest()
 return result
changes=[]; original_objects=load(before/'objects.json')
with zipfile.ZipFile(before/'objects.zip')as archive,zipfile.ZipFile(d/'compiled/changed-objects.zip','x',compression=zipfile.ZIP_DEFLATED)as frozen:
 for item in original_objects:
  previous=archive.read(item['zip_member']); assert ident(previous)==dict(bytes=item['bytes'],sha256=item['sha256'])
  current=(ROOT/item['path']).read_bytes()
  if current!=previous:
   delta=dict(path=item['path'],source=item['source'],before=ident(previous),after=ident(current),before_allocated=allocated(previous),after_allocated=allocated(current))
   changes.append(delta); frozen.writestr(item['zip_member'],current)
 frozen.writestr(Path(new_probe['output']).as_posix(),(cache/new_probe['output']).read_bytes())
write(d/'object-comparison.json',dict(objects=len(original_objects),main_command_macro_changes=main_command_changes,new_probe_command=new_probe,changed_existing=changes))
assert [Path(x['source']).name for x in changes]==['pcm.c'],'Unexpected existing object difference; investigate preserved before/after bytes'
shutil=__import__('shutil'); shutil.copyfile(cache/'esp-idf/main/libmain.a',d/'compiled/libmain.a')
elf_path=d/'compiled/yoradio_cyd2usb_native.elf'; image_file=d/'fixture/yoradio_cyd2usb_native.bin'
body=image_file.read_bytes(); image=LoadFirmwareImage('esp32',body)
assert image.chip_id==image.ROM_LOADER.IMAGE_CHIP_ID and image.calculate_checksum()==image.checksum
assert image.append_digest and image.stored_digest==image.calc_digest and len(body)==image.data_length+32
assert body[:24]==(old/'fixture/yoradio_cyd2usb_native.bin').read_bytes()[:24]
assert image.segments[0].data[144:176].hex()==pin(elf_path)['sha256']
appdesc=bytearray(image.segments[0].data[:256]); appdesc[144:176]=bytes(32)
original_app=LoadFirmwareImage('esp32',(old/'fixture/yoradio_cyd2usb_native.bin').read_bytes())
old_desc=bytearray(original_app.segments[0].data[:256]); old_desc[144:176]=bytes(32); assert appdesc==old_desc
for p in (old/'fixture').rglob('*'):
 if p.is_file()and p.name!='yoradio_cyd2usb_native.bin': assert pin(p)==pin(d/'fixture'/p.relative_to(old/'fixture'))
exporter=runpy.run_path(str(ROOT/'tools/export_cyd_production.py'))
slots=exporter['partition_slots']((d/'fixture/partition_table/partition-table.bin').read_bytes(),4*1024**2)
assert len(slots)==2 and all(s['bytes']==0x1b0000 and len(body)<s['bytes']for s in slots)
with elf_path.open('rb')as f,(old/'compiled/yoradio_cyd2usb_native.elf').open('rb')as old_f:
 e,old_e=ELFFile(f),ELFFile(old_f); t=e.get_section_by_name('.symtab'); old_t=old_e.get_section_by_name('.symtab')
 value=lambda n:t.get_symbol_by_name(n)[0]['st_value']; old_value=lambda n:old_t.get_symbol_by_name(n)[0]['st_value']
 assert value('_rtc_slow_length')==104 and old_value('_rtc_slow_length')==104
 owners={}
 for name,size in (('s_pbuf_failures',128),('s_pbuf_failure_lock',8)):
  symbol,=t.get_symbol_by_name(name); sec=e.get_section(symbol['st_shndx']); offset=symbol['st_value']-sec['sh_addr']; data=sec.data()[offset:offset+size]
  assert symbol['st_size']==size and sec.name=='.dram0.data'
  if name=='s_pbuf_failures': assert data==bytes(128)
  else: assert struct.unpack('<II',data)==(0xb33fffff,0)
  owners[name]=dict(bytes=size,address=symbol['st_value'],section=sec.name,initial_bytes_sha256=hashlib.sha256(data).hexdigest(),initial_hex=data.hex()if size<=8 else None)
 data_delta=e.get_section_by_name('.dram0.data')['sh_size']-old_e.get_section_by_name('.dram0.data')['sh_size']
 bss_delta=e.get_section_by_name('.dram0.bss')['sh_size']-old_e.get_section_by_name('.dram0.bss')['sh_size']
 heap_delta=value('_heap_start')-old_value('_heap_start')
 assert data_delta==136 and bss_delta==0 and heap_delta==144
 assert e.get_section_by_name('.iram0.text')['sh_size']==old_e.get_section_by_name('.iram0.text')['sh_size']
 reserve=e.get_section_by_name('.rtc_slow_reserved'); assert reserve['sh_size']==24 and reserve['sh_addr']-value('_rtc_force_slow_end')==8064
 for name,size in (('s_status',5120),('s_previous',508),('s_current',508),('s_clients',384),('s_sockets',40),('s_display',5168)):
  symbol,=[s for s in t.get_symbol_by_name(name)if s['st_info']['type']=='STT_OBJECT']; assert symbol['st_size']==size and e.get_section(symbol['st_shndx']).name=='.dram0.bss'
dump=DEP/'tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin/xtensa-esp32-elf-objdump.exe'
frames={}
for name in ('__wrap_pbuf_alloc','cyd_openeth_pbuf_failure_dump','__wrap_native_audio_output_flush_pcm','__wrap_native_audio_output_write_pcm'):
 text=subprocess.check_output([str(dump),'-d','--disassemble='+name,str(elf_path)],text=True)
 (d/(name+'.disassembly.txt')).write_text(text)
 found,=re.findall(r'\bentry\s+a1,\s*(\d+)',text); frames[name]=int(found)
assert frames=={'__wrap_pbuf_alloc':48,'cyd_openeth_pbuf_failure_dump':192,'__wrap_native_audio_output_flush_pcm':160,'__wrap_native_audio_output_write_pcm':48}
subprocess.run(list(map(str,[sys.executable,'-B',ROOT/'tests/check-cyd-ogg-stack.py','--elf',elf_path,'--objdump',dump,'--output',d/'stack-frame.json'])),check=True)
write(d/'static-qualification.json',dict(passed=True,source_commit=candidate['source_commit'],backend=backend,physical_tested=False,native_run=False,
 image=pin(image_file),elf=pin(elf_path),config=pin(d/'compiled/config/sdkconfig.json'),effective_config_delta={},
 cmake_flag_delta=dict(CYD_OPENETH_PBUF_FAILURE_PROBE=dict(before=False,after=True)),main_command_changes=len(main_command_changes),
 changed_existing_objects=[dict(path=x['path'],before=x['before'],after=x['after'])for x in changes],new_probe_object=pin(cache/new_probe['output']),
 baseline_snapshot=pin(before/'snapshot.json'),baseline_objects_zip=pin(before/'objects.zip'),owners=owners,
 memory_delta=dict(dram_data_bytes=data_delta,dram_bss_bytes=bss_delta,heap_start_bytes=heap_delta,linker_alignment_bytes=heap_delta-data_delta),
 rtc_workspace=False,rtc_probe=True,pbuf_probe=True,qemu_sha256=candidate['qemu']['sha256'],
 geometry=dict(rtc_used_bytes=104,rtc_reserved_bytes=24,rtc_free_bytes=8064),frames=frames,total_stack_depth_verified=False,ota_slots=slots))
print('STATIC QUALIFIED '+backend,flush=True)
