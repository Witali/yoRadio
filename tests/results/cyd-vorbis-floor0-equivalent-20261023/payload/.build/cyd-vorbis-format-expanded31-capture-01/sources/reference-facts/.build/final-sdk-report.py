import hashlib,json,re,shutil,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tests/results/native-warning-fixes-20261018'
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

cases=[
 ('CYD PDM','esp32-cyd2usb-native-startup-web-pcm-pdm','esp32-cyd2usb-native-format-dsp-pdm','esp32-cyd2usb-native','build-c3-transfer'),
 ('CYD continuous DAC','esp32-cyd2usb-native-startup-web-pcm-dac','esp32-cyd2usb-native-format-dsp-dac','esp32-cyd2usb-native','build-c3-transfer-dac'),
 ('CYD legacy DAC','esp32-cyd2usb-native-startup-web-pcm-legacy','esp32-cyd2usb-native-format-dsp-legacy','esp32-cyd2usb-native','build-c3-transfer-legacy'),
 ('C3 stereo PDM','esp32c3-oled-native-warning-fixes','esp32c3-oled-native-format-bitrate','esp32c3-oled-native','build-c3-transfer'),
]
results=[]
for label,variant,prior,project,build_name in cases:
 destination=ROOT/'firmware/development'/variant
 build=ROOT/'idf'/project/build_name
 manifest=json.loads((destination/'manifest.json').read_text())
 assert manifest['source_commit']==HEAD and manifest['build_check']=='PASS'
 image=(destination/'app.bin').read_bytes()
 assert len(image)==manifest['app_bytes'] and digest(destination/'app.bin')==manifest['app_sha256']
 assert image[176:208].hex()==manifest['elf_sha256']
 assert HEAD[:8] in manifest['app_version'] and not manifest['app_version'].endswith('-dirty')
 description=json.loads((build/'project_description.json').read_text())
 assert digest(build/description['app_elf'])==manifest['elf_sha256']
 config=json.loads((destination/'sdkconfig.json').read_text())
 assert config==json.loads((build/'config/sdkconfig.json').read_text())
 old=json.loads((ROOT/'firmware/development'/prior/'sdkconfig.json').read_text())
 changes={k:{'previous':old.get(k),'current':config.get(k)} for k in sorted(set(old)|set(config)) if old.get(k)!=config.get(k)}
 if project=='esp32c3-oled-native':
  assert config==old,'C3 tested hardware/RAM profile changed'
  files={'sdkconfig':build/'sdkconfig','partition-table.bin':build/'partition_table/partition-table.bin',
         'project_description.json':build/'project_description.json','flasher_args.json':build/'flasher_args.json',
         'build.log':ROOT/'.build/c3-warning-sdk-native.log'}
  metadata={}
  for name,source in files.items():
   shutil.copyfile(source,destination/name);metadata[name]=digest(destination/name)
  manifest['build_metadata_sha256']=metadata
  manifest['compiler']=description['c_compiler']
  manifest['compiler_sha256']=digest(Path(description['c_compiler']))
  manifest['ota_slot_bytes']=0x1d0000
  write(destination/'manifest.json',manifest)
  log_paths=[destination/'build.log'];slot=0x1d0000
 else:
  assert manifest['source_dirty'] is False
  assert config['HTTPD_WS_SUPPORT'] and not config['HTTPD_QUEUE_WORK_BLOCKING']
  assert config['LWIP_MAX_SOCKETS']==old['LWIP_MAX_SOCKETS']==10
  assert all(k.startswith('YORADIO_') or k in ('HTTPD_WS_SUPPORT','HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT','HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT') for k in changes),changes
  slot=min(entry['bytes'] for entry in manifest['ota_slots'])
  log_paths=[destination/entry['file'] for entry in manifest['build_logs']]
 assert len(image)<=slot
 warnings=[]
 for path in log_paths:
  for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
   if re.search(r'\bwarning:',line):warnings.append(line)
 results.append(dict(label=label,variant=variant,app_bytes=len(image),ota_slot_bytes=slot,
                     ota_free_bytes=slot-len(image),app_sha256=manifest['app_sha256'],
                     elf_sha256=manifest['elf_sha256'],sdkconfig_changes=changes,
                     compiler_warnings=warnings,manifest_sha256=digest(destination/'manifest.json')))

# Record allocated symbols, without calling these physical free-heap measurements.
pdm=ROOT/'idf/esp32-cyd2usb-native/build-c3-transfer'
description=json.loads((pdm/'project_description.json').read_text())
nm=Path(description['c_compiler']).with_name('xtensa-esp32-elf-nm.exe')
symbols=subprocess.check_output([str(nm),'-S','--size-sort','-C',str(pdm/description['app_elf'])],text=True)
selected=[]
for line in symbols.splitlines():
 match=re.match(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+(\S)\s+(.+)$',line)
 if not match:continue
 address,size,kind,name=match.groups()
 if kind.lower() in ('b','d','r') and (re.search(r'normalizer|s_pcm_(?:bits|channels|sample_rate)|kSoftLimitLut|kGainQ12ByDb|kPeakByAttenuationDb',name)):
  region='flash_rodata' if 0x3f400000<=int(address,16)<0x3f800000 else 'dram'
  selected.append(dict(name=name,kind=kind,bytes=int(size,16),region=region))
(OUT/'sdk-normalizer-symbols.log').write_text('\n'.join(line for line in symbols.splitlines() if any(s['name'] in line for s in selected))+'\n',encoding='utf-8')
report=dict(passed=True,source_commit=HEAD,physical_tested=False,images=results,normalizer_symbols=selected,
            normalizer_dram_bytes=sum(s['bytes'] for s in selected if s['region']=='dram'),
            normalizer_rodata_bytes=sum(s['bytes'] for s in selected if s['region']=='flash_rodata'),
            normalizer_soft_limit_lut_bytes=sum(s['bytes'] for s in selected if 'kSoftLimitLut' in s['name']))
source=(ROOT/'idf/esp32-cyd2usb-native/main/audio_service.c').read_text()
affinity=[]
for function,name,priority,core in [('stream_task','radio_stream',3,0),('decoder_task','audio_decode',5,1),('output_task','audio_output',6,1)]:
 assert re.search(r'\{'+function+r',\s*"'+name+r'",\s*BOARD_TASK_STACK_\w+,\s*'+str(priority)+r',\s*'+str(core)+r'\}',source)
 affinity.append(dict(task=name,core=core,priority=priority))
report['cyd_pipeline_affinity']=affinity
write(OUT/'SDK.json',report)
rows=[]
for entry in results:
 relative='../../../firmware/development/'+entry['variant']+'/'
 rows.append('| '+entry['label']+' | [app.bin]('+relative+'app.bin) | '+str(entry['app_bytes'])+' | '+str(entry['ota_free_bytes'])+' | [manifest]('+relative+'manifest.json) |')
text='''# SDK build qualification

All four production images build from clean source `'''+HEAD+'''`.
CYD uses the pinned ESP-IDF 6.0.2/Xtensa GCC 15.2; C3 uses the pinned
ESP-IDF 6.1 revision 9a97f6c5/RISC-V GCC 15.2. No board was flashed.

| Variant | Image | App bytes | OTA spare bytes | Metadata |
| --- | --- | ---: | ---: | --- |
'''+ '\n'.join(rows)+'''

[Machine-readable checks](SDK.json) verify source version, image/ELF SHA-256,
archive/config agreement, partition capacity and changes from the preceding
profiles. CYD adds native WebUI settings and WebSocket support while retaining
its board, clock, DMA and socket profiles. The tested C3 configuration is
identical to its preceding archived profile. Exact configuration differences
and compiler warning lines are retained in the JSON report.

CYD preserves the original pinned audio tasks: `radio_stream` on core 0 at
priority 3; `audio_decode` on core 1 at priority 5; `audio_output` on core 1 at
priority 6. The startup harness asserts these assignments in every variant.

The CYD wrapper archives build logs, config, partition and project metadata;
C3 retains the corresponding files beside its image. See [host qualification](HOST.md)
and the earlier [startup/PCM/WebUI qualification](../cyd-startup-pcm-web-20261018/HOST.md).
No physical network/audio/browser, heap/stack headroom or power-loss acceptance
is claimed. AAC owner-view qualification and the remaining transfer stages
stay open in the plan.
'''
(OUT/'SDK.md').write_text(text,encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))
