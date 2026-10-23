"""Validate real C3 compiler observations and prepare the isolated flash merge."""
import hashlib,json,re
from pathlib import Path

root=Path(__file__).resolve().parent.parent
out=root/'.build/c3-vorbis-format-baseline-01'
build=out/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
context=json.loads((out/'macro-context.json').read_text())
for relative,digest in context['build_outputs'].items(): assert sha(out/relative)==digest,relative
for relative,digest in context['reviewed_sources'].items(): assert sha(out/relative)==digest,relative
for name,row in context['frozen_inputs'].items():
    assert sha(name)==sha(out/row['snapshot'])==row['sha256'],name
records={}
for name in ('setup-macros','symbols','qemu-machine-help'):
    path=out/(name+'.json')
    row=json.loads(path.read_text())
    assert row['status']=='TERMINAL' and row['returncode']==0
    for log,identity in row['logs'].items():
        assert Path(log).stat().st_size==identity['bytes'] and sha(log)==identity['sha256']
    records[name]={'record':str(path.relative_to(out)),'sha256':sha(path),'returncode':0}
macros=(out/'setup-macros.stdout.log').read_text()
expected={'__riscv_xlen':32,'CONFIG_IDF_TARGET_ESP32C3':1,'CONFIG_FREERTOS_UNICORE':1,
          'CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ':160,'FORMAT_EXPECT_LOW_RATE_REJECTION':1}
for name,value in expected.items(): assert re.search(r'^#define '+name+' '+str(value)+r'$',macros,re.M),name
assert not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M)
symbols=(out/'symbols.stdout.log').read_text()
required=('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_open','esp_vorbis_dec_decode')
for name in required: assert re.search(r'\b'+name+'$',symbols,re.M),name
assert re.search(r'^esp32c3\s+Espressif ESP32-C3 machine$',(out/'qemu-machine-help.stdout.log').read_text(),re.M)
pins=json.loads((root/'.build/c3-vorbis-format-project-prep-01/pins.json').read_text())
for row in pins['external_inputs']:
    assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
recipe_path=build/'flasher_args.json'
recipe=json.loads(recipe_path.read_text())
assert recipe['flash_settings']=={'flash_mode':'dio','flash_size':'4MB','flash_freq':'40m'}
expected_flash={0:build/'bootloader/bootloader.bin',0x8000:build/'partition_table/partition-table.bin',0x10000:build/'c3_vorbis_public_format.bin'}
assert {int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()}==expected_flash
flash=out/'qemu-flash.bin'
assert not flash.exists() and not (out/'merge-plan.json').exists()
argv=[pins['tools']['python'],'-m','esptool','--chip','esp32c3','merge-bin','--output',str(flash),
      '--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
for offset,path in sorted(expected_flash.items()): argv += [hex(offset),str(path)]
argv+=['--pad-to-size','4MB']
report=dict(schema='c3-public-vorbis-postbuild-observations-v1',target_executed=False,
            macros=expected,limit_to_64khz=False,symbols=list(required),commands=records,
            recipe_sha256=sha(recipe_path),flash_inputs={str(p.relative_to(out)):sha(p) for p in expected_flash.values()},
            preparation_script_sha256=sha(__file__))
for name,document in (('postbuild-observations.json',report),('merge-plan.json',{'directory':str(out),'argv':argv})):
    with (out/name).open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(document,indent=2)+'\n')
print(json.dumps({'postbuild_checks':'PASS','target':'esp32c3','merge_plan_ready':True,'runtime_qualified':False}))
