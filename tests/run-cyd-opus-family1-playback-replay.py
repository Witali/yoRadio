"""Audit exact completed native02 image provenance/DROM placement, then replay without rebuilding.

The original02 external-observer NONPASS remains unchanged. Aggregate ELF WA
and nm d are recorded, not relabelled read-only. A readonly own input section,
actual SDK DROM region/alias/map and identical ELF/app/flash bytes establish
the declared const object's flash placement. Native PCM/status checks remain
the unchanged original controller's integration oracle.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import struct
import sys
ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'tests/run-cyd-opus-family1-playback-qemu.py'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def elf_sections(body):
    need(body[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',body,18)[0]==94,'actual ELF32 little-endian Xtensa')
    offset=struct.unpack_from('<I',body,32)[0];width,count,names=struct.unpack_from('<HHH',body,46);need(width==40 and count>names and offset+width*count<=len(body),'bounded actual ELF section table')
    sections=[dict(zip(('name_offset','type','flags','address','offset','bytes','link','info','alignment','entry_bytes'),struct.unpack_from('<10I',body,offset+i*width))) for i in range(count)]
    string=sections[names];text=body[string['offset']:string['offset']+string['bytes']]
    for section in sections:section['name']=text[section['name_offset']:].split(b'\0',1)[0].decode('ascii')
    return sections
def symbol(body,sections,name):
    matches=[]
    for section in sections:
        if section['type']!=2:continue
        need(section['entry_bytes']==16 and section['link']<len(sections),'ordinary bounded actual symbol table');strings=sections[section['link']];text=body[strings['offset']:strings['offset']+strings['bytes']]
        for at in range(section['offset'],section['offset']+section['bytes'],16):
            string,value,size,info,other,index=struct.unpack_from('<IIIBBH',body,at)
            if text[string:].split(b'\0',1)[0].decode('ascii')==name:matches.append(dict(value=value,bytes=size,info=info,visibility=other,section=index))
    need(len(matches)==1 and matches[0]['section']<len(sections),'unique defined own symbol');return matches[0]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source-build',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--audit-only',action='store_true');parser.add_argument('--qemu-timeout',type=int,default=1200);args=parser.parse_args()
    source=args.source_build.resolve();out=args.output.resolve();need(sys.platform=='win32' and source.is_relative_to(ROOT/'.build') and out.is_relative_to(ROOT/'.build') and not out.exists() and 1<=args.qemu_timeout<=1200,'fresh bounded read-only Windows audit/replay')
    original=json.loads((source/'report.json').read_bytes());bundle=json.loads((source/'execution-bundle.json').read_bytes());child=json.loads((source/'sdk-child.json').read_text('utf-8-sig'))
    native_source=bundle['sources'].get(str(NATIVE));need(native_source and sha(NATIVE)==native_source['sha256'],'unchanged original native parser/runtime controller')
    native=module('family1_exact_image_native',NATIVE)
    class Replay:
        run_command=native.common.Campaign.run_command
        def __init__(self):
            self.out=out;self.environment=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TMP=str(out/'tmp'),TEMP=str(out/'tmp'),TMPDIR=str(out/'tmp'));self.report=dict(passed=False,completed=False,commands=[],sources={},artifacts={},runtime={},target_executed=False,sdk_build_executed=False,production_selected=False)
        def save(self):native.common.write_json(out/'report.json',self.report)
    out.mkdir(parents=True);(out/'tmp').mkdir();replay=Replay();report=replay.report
    def copy(path,relative):
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes());need(pin(target)==pin(path),'exact read-only copied provenance');return target
    original_pins={str(source/name):pin(source/name) for name in ('report.json','execution-bundle.json','sdk-child.json','source-manifest.json','actual-compiler-closure.json','fixture-preparation.json')}
    def verify():
        for path,expected in original_pins.items():need(pin(path)==expected,'original02 evidence remains immutable')
        for original_path,row in bundle['sources'].items():need(sha(original_path)==sha(source/row['snapshot'])==row['sha256'],'all initial/final original source bindings read in place')
        for path,digest in bundle['artifacts'].items():need(sha(source/path)==digest,'all initial/final exact original build artifacts read in place')
        for path,digest in report['runtime'].items():
            actual=Path(shutil.which(path.split(':',1)[1]) or '') if path.startswith('runtime-path-redacted:') else Path(path)
            need(actual.is_file() and sha(actual)==digest,'same original native runtime')
    replay.save()
    try:
        need(original['passed'] is False and original['completed'] is False and original['target_executed'] is False and original['failure']=='actual target immutable zero storage' and
            child['pid']>0 and child['exit_status']==0 and len([r for r in original['commands'] if r['name']=='build' and r['state']=='complete' and r['exit_status']==0])==1,'genuine original02 SDK zero / observer NONPASS before QEMU')
        for name in ('report.json','execution-bundle.json','sdk-child.json','source-manifest.json','actual-compiler-closure.json','fixture-preparation.json'):copy(source/name,Path('original02')/name)
        controller=copy(Path(__file__),Path('audit/replay-controller.py'));report.update(sources=bundle['sources'],artifacts=bundle['artifacts'],runtime=dict(bundle['runtime']),source_capture=str(source),artifacts_read_in_place=True,
            audit_controller=pin(controller),original_build=dict(capture=source.name,pins=original_pins,actual_child_pid=child['pid'],actual_child_status=0,original_observer_nonpass_preserved=True))
        verify();desc=json.loads((source/'build/project_description.json').read_bytes());elf=source/'build'/desc['app_elf'];app=elf.with_suffix('.bin');flash=source/'qemu-flash.bin';obj=source/'build/esp-idf/main/CMakeFiles/__idf_main.dir/main.c.obj'
        elf_body=elf.read_bytes();sections=elf_sections(elf_body);own=symbol(elf_body,sections,'ofp_zero_chunk');section=sections[own['section']]
        object_body=obj.read_bytes();object_sections=elf_sections(object_body);input_section=next(s for s in object_sections if s['name']=='.rodata.ofp_zero_chunk')
        need(own['bytes']==2048 and own['info']&15==1 and section['name']=='.flash.rodata' and section['flags']&2 and not section['flags']&4 and
            input_section['bytes']==2048 and input_section['flags']==2,'own allocated non-W input section and actual aggregate flash section, without relabelling WA')
        elf_offset=section['offset']+own['value']-section['address'];need(0<=own['value']-section['address']<=section['bytes']-own['bytes'],'symbol contained in actual output section')
        need(elf_body[elf_offset:elf_offset+2048]==object_body[input_section['offset']:input_section['offset']+2048]==bytes(2048),'identical complete zero object in own object and linked ELF')
        header=source/'project/main/opus_family1_playback.h';need(b'static const uint8_t ofp_zero_chunk[OFP_CHUNK_FRAMES*8*2]={0};' in header.read_bytes(),'unchanged declared const public adapter object')
        generated=source/'build/esp-idf/esp_system/ld';memory=copy(generated/'memory.ld',Path('audit/memory.ld'));script=copy(generated/'sections.ld',Path('audit/sections.ld'));memory_text=memory.read_text();section_text=script.read_text()
        need(re.search(r'drom0_0_seg\s*\(R\)\s*:\s*org\s*=\s*0x3F400020,\s*len\s*=\s*0x400000-0x20',memory_text) and
            'REGION_ALIAS("default_rodata_seg", drom0_0_seg);' in memory_text and 'REGION_ALIAS("default_rodata_seg", dram0_0_seg);' not in memory_text,'actual generated read-only DROM region and selected alias')
        need(0x3f400020<=own['value'] and own['value']+2048<=0x3f800000,'entire object in actual DROM bounds, not RAM')
        position=section_text.index('  .flash.rodata : ALIGN(0x10)');need('} > default_rodata_seg' in section_text[position:section_text.index('ASSERT((ADDR(.flash.tdata)',position)],'actual output section assigned to selected DROM alias')
        map_path=elf.with_suffix('.map');map_text=map_path.read_text();placement=re.search(r'\.rodata\.ofp_zero_chunk\s*\n\s*(0x[0-9a-f]+)\s+(0x[0-9a-f]+)\s+esp-idf/main/libmain\.a\(main\.c\.obj\)',map_text)
        need(placement and int(placement[1],16)==own['value'] and int(placement[2],16)==2048,'exact own input-section linker-map placement')
        idf=Path(desc['idf_path']);sdk_memory=copy(idf/'components/esp_system/ld/esp32/memory.ld.in',Path('audit/sdk-memory.ld.in'));need('drom0_0_seg (R)' in sdk_memory.read_text() and 'Flash mapped constant data' in sdk_memory.read_text(),'pinned primary SDK mapping source')
        recipe=json.loads((source/'build/flasher_args.json').read_bytes());merged=flash.read_bytes()
        for offset,path in recipe['flash_files'].items():
            body=(source/'build'/path).read_bytes();need(merged[int(offset,0):int(offset,0)+len(body)]==body,'all exact original merged image components')
        image=app.read_bytes();need(image[0]==0xe9 and 1<=image[1]<=16,'ordinary original ESP32 SDK app image');at=24;segments=[]
        for _ in range(image[1]):
            need(at+8<=len(image),'complete original segment header');address,size=struct.unpack_from('<II',image,at);at+=8;need(size<=len(image)-at,'bounded complete original segment')
            if address<=own['value'] and own['value']+2048<=address+size:segments.append(dict(address=address,bytes=size,file_offset=at+own['value']-address))
            at+=size
        need(len(segments)==1,'unique app-image DROM segment covering own object');segment=segments[0];app_offset=int(recipe['app']['offset'],0);offset=segment['file_offset']
        need(image[offset:offset+2048]==merged[app_offset+offset:app_offset+offset+2048]==bytes(2048),'identical complete object through original app and merged flash bytes')
        compiler=Path(desc['c_compiler']);readelf=compiler.with_name(compiler.name.replace('gcc','readelf'));nm=compiler.with_name(compiler.name.replace('gcc','nm'))
        for path in (readelf,nm):report['runtime'][str(path)]=sha(path)
        replay.run_command('readelf-version',[readelf,'--version']);replay.run_command('linked-sections',[readelf,'-SW',elf]);replay.run_command('own-object-sections',[readelf,'-SW',obj]);symbols=replay.run_command('own-symbol',[nm,'-S','--defined-only',elf])
        observed=re.search(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+(\S)\s+ofp_zero_chunk$',symbols,re.M);need(observed and int(observed[1],16)==own['value'] and int(observed[2],16)==2048,'actual nm address/size, class recorded without generic acceptance')
        report['image_audit']=dict(passed=True,own_symbol=own,own_input_section=input_section,aggregate_output_section=section,nm_class=observed[3],app_segment=segment,app_flash_offset=app_offset,
            elf_zero_sha256=hashlib.sha256(bytes(2048)).hexdigest(),drom_origin=0x3f400020,drom_end=0x3f800000,generated_memory=pin(memory),generated_sections=pin(script),sdk_memory_source=pin(sdk_memory),
            explanation='Own input has A without W; aggregate output flags are retained exactly. Linker R DROM alias/map and original image bytes establish flash constant placement; nm class is not treated as generic permissions.',
            primary_doc='https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-guides/memory-types.html#drom-data-stored-in-flash')
        replay.save();verify()
        if args.audit_only:
            report.update(passed=True,completed=True,audit_only=True);print(json.dumps(dict(passed=True,audit_only=True,target_executed=False,symbol_address=hex(own['value']),aggregate_flags=section['flags'],own_flags=input_section['flags'],nm_class=observed[3],bytes=2048)));return 0
        qemu=next(Path(path) for path in bundle['runtime'] if path.endswith('qemu-system-xtensa.exe'));rom=Path('C:/Work/QEMU-ESP32/pc-bios')
        print('AUDITED exact original02 image; starting offline native replay without SDK build',flush=True)
        log=replay.run_command('qemu',[qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',rom,'-display','none','-monitor','none','-serial','stdio',
            '-no-reboot','-snapshot','-nic','none','-drive','file='+str(flash)+',if=mtd,format=raw'],args.qemu_timeout)
        reference=json.loads((source/'fixture-preparation.json').read_bytes());report['measurements']=native.parse_log(log+'\n'+(out/'qemu.stderr.log').read_text(errors='replace'),reference)
        verify();need(report['measurements']['gate_passed'],'unchanged complete PCM/status/owner/resource integration gate');report.update(passed=True,completed=True,audit_only=False);print(json.dumps(dict(passed=True,references=12,adapter_cases=22,exact_original_image=True,sdk_build_executed=False)));return 0
    except Exception as error:
        report.update(passed=False,completed=False,failure_type=type(error).__name__,failure=str(error));print(json.dumps(dict(passed=False,failure=str(error))));return 1
    finally:replay.save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
