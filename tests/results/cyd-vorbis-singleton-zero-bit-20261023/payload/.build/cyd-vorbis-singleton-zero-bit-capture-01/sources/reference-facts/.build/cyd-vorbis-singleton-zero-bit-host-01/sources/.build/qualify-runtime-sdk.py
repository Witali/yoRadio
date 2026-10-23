import hashlib,json,re,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'tests/results/native-runtime-transfer-20261018'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
cases=[
 ('CYD PDM','esp32-cyd2usb-native-runtime-transfer-pdm','esp32-cyd2usb-native-ota-transfer-pdm','esp32-cyd2usb-native','build-c3-transfer'),
 ('CYD continuous DAC','esp32-cyd2usb-native-runtime-transfer-continuous','esp32-cyd2usb-native-ota-transfer-continuous','esp32-cyd2usb-native','build-c3-transfer-dac'),
 ('CYD legacy DAC','esp32-cyd2usb-native-runtime-transfer-legacy','esp32-cyd2usb-native-ota-transfer-legacy','esp32-cyd2usb-native','build-c3-transfer-legacy'),
 ('C3 stereo PDM','esp32c3-oled-native-runtime-transfer','esp32c3-oled-native-ota-transfer','esp32c3-oled-native','build-c3-transfer')]
results=[];layouts={}
for label,variant,prior,project,build_name in cases:
    dest=root/'firmware/development'/variant;build=root/'idf'/project/build_name
    manifest=json.loads((dest/'manifest.json').read_text())
    assert manifest['source_commit']==head and manifest['build_check']=='PASS' and not manifest['physical_tested']
    assert digest(Path(manifest['compiler']))==manifest['compiler_sha256']
    image=(dest/'app.bin').read_bytes()
    assert len(image)==manifest['app_bytes'] and digest(dest/'app.bin')==manifest['app_sha256']
    assert image[176:208].hex()==manifest['elf_sha256']
    assert head[:8] in manifest['app_version'] and not manifest['app_version'].endswith('-dirty')
    description=json.loads((build/'project_description.json').read_text())
    assert digest(build/description['app_elf'])==manifest['elf_sha256']
    config=json.loads((dest/'sdkconfig.json').read_text())
    assert config==json.loads((build/'config/sdkconfig.json').read_text())
    old=json.loads((root/'firmware/development'/prior/'sdkconfig.json').read_text())
    changes={k:{'previous':old.get(k),'current':config.get(k)} for k in sorted(set(old)|set(config)) if old.get(k)!=config.get(k)}
    allowed={'LWIP_SNTP_MAX_SERVERS'} if project=='esp32-cyd2usb-native' else set()
    assert set(changes)<=allowed,changes
    assert config['HTTPD_WS_PRE_HANDSHAKE_CB_SUPPORT'] and config['HTTPD_WS_POST_HANDSHAKE_CB_SUPPORT']
    assert not config['HTTPD_QUEUE_WORK_BLOCKING'] and config['LWIP_MAX_SOCKETS']==old['LWIP_MAX_SOCKETS']==10
    assert manifest['source_dirty'] is False
    if project=='esp32c3-oled-native':
        assert config['HTTPD_WS_STRICTER_RFC6455']
        assert digest(dest/'sdkconfig.json')==manifest['sdkconfig_sha256']
        assert digest(dest/'sdkconfig')==manifest['sdkconfig_text_sha256']
        for filename,expected in manifest['build_metadata_sha256'].items():
            assert digest(dest/filename)==expected
        evidence=manifest['additional_host_evidence']
        assert digest(root/evidence['path'])==evidence['sha256']
        slot=0x1d0000;logs=[dest/'build.log',dest/'build-stderr.log']
    else:
        slot=min(p['bytes'] for p in manifest['ota_slots'])
        assert slot==0x1b0000
        assert digest(dest/'sdkconfig')==manifest['sdkconfig_sha256']
        assert digest(dest/'sdkconfig.json')==manifest['sdkconfig_json_sha256']
        for filename,key in [('partition-table.bin','partition_table_sha256'),
                             ('flasher_args.json','flasher_args_sha256'),
                             ('project_description.json','project_description_sha256')]:
            assert digest(dest/filename)==manifest[key]
        for entry in manifest['evidence']:
            assert digest(Path(entry['path']))==entry['sha256']
        for entry in manifest['build_logs']:
            assert digest(dest/entry['file'])==entry['sha256']
        logs=[dest/entry['file'] for entry in manifest['build_logs']]
    assert len(image)<=slot
    warnings=[line for path in logs for line in path.read_text(encoding='utf-8',errors='replace').splitlines() if re.search(r'\bwarning:',line)]
    results.append(dict(label=label,variant=variant,app_bytes=len(image),ota_slot_bytes=slot,ota_free_bytes=slot-len(image),
                        app_sha256=manifest['app_sha256'],elf_sha256=manifest['elf_sha256'],sdkconfig_changes=changes,
                        compiler_warnings=warnings,manifest_sha256=digest(dest/'manifest.json')))
    if variant.endswith('-pdm') or project=='esp32c3-oled-native':
        board='c3' if project=='esp32c3-oled-native' else 'cyd'
        prefix='riscv32-esp-elf' if board=='c3' else 'xtensa-esp32-elf'
        nm=Path(description['c_compiler']).with_name(prefix+'-nm.exe')
        units={'ws':build/'esp-idf/main/CMakeFiles/__idf_main.dir/websocket_service.c.obj',
               'tls':build/'esp-idf/native_web_transport/CMakeFiles/__idf_native_web_transport.dir/native_web_transport.c.obj',
               'time':build/'esp-idf/main/CMakeFiles/__idf_main.dir/time_service.c.obj',
               'network':build/'esp-idf/main/CMakeFiles/__idf_main.dir/network_service.c.obj',
               'wifi-store':build/'esp-idf/native_wifi_store/CMakeFiles/__idf_native_wifi_store.dir/native_wifi_store.c.obj',
               'wifi-http':build/'esp-idf/native_wifi_store/CMakeFiles/__idf_native_wifi_store.dir/native_wifi_http.c.obj',
               'wifi-io':build/'esp-idf/native_wifi_store/CMakeFiles/__idf_native_wifi_store.dir/native_wifi_request_io.c.obj',
               'time-backend':build/'esp-idf/native_time/CMakeFiles/__idf_native_time.dir/native_time_sntp.c.obj'}
        layouts[board]={}
        for unit,path in units.items():
            raw=subprocess.check_output([str(nm),'-S','--size-sort','-C',str(path)],text=True)
            (out/f'sdk-{board}-{unit}-symbols.log').write_text(raw)
            selected=[]
            for line in raw.splitlines():
                match=re.match(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+([bBdDrR])\s+(.+)$',line)
                if match:
                    _,size,kind,name=match.groups()
                    selected.append(dict(name=name,kind=kind,bytes=int(size,16)))
            layouts[board][unit]=selected
        assert any(s['name']=='s_clients' for s in layouts[board]['ws'])
source=(root/'idf/esp32-cyd2usb-native/main/audio_service.c').read_text()
affinity=[]
for function,name,priority,core in [('stream_task','radio_stream',3,0),('decoder_task','audio_decode',5,1),('output_task','audio_output',6,1)]:
    assert re.search(r'\{'+function+r',\s*"'+name+r'",\s*BOARD_TASK_STACK_\w+,\s*'+str(priority)+r',\s*'+str(core)+r'\}',source)
    affinity.append(dict(task=name,core=core,priority=priority))
report=dict(passed=True,source_commit=head,physical_tested=False,images=results,target_object_symbols=layouts,
            cyd_pipeline_affinity=affinity,scope='Time/private-Wi-Fi checkpoint: GCC final ELF/image/archive/config integrity and actual target object symbol sizes. No physical OTA/flash, power-loss, heap/stack/timing or audio admission claim.')
(out/'SDK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'images':[{k:r[k] for k in ['label','app_bytes','ota_free_bytes','sdkconfig_changes']} for r in results],
                  'websocket_clients_bytes':{b:next(s['bytes'] for s in layouts[b]['ws'] if s['name']=='s_clients') for b in layouts}},indent=2))
