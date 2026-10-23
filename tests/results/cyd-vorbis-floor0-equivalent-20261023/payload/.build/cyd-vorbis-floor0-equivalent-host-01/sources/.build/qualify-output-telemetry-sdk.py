"""Verify six actual linked applications without running any device operation."""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys

ROOT=Path.cwd()
OUT=ROOT/'tests/results/cyd-output-telemetry-20261020'
sys.path.insert(0,str(ROOT/'tools'))
from export_cyd_production import image_descriptor,partition_slots
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
git=lambda *args:subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=ROOT)
head=git('rev-parse','HEAD').decode().strip()
assert head.startswith('0f2a37c89'),head
images=[]
for custom in (False,True):
    for backend in ('pdm','continuous','legacy'):
        suffix=('custom-flac-' if custom else '')+backend
        variant='esp32-cyd2usb-native-output-telemetry-'+suffix
        folder=ROOT/'firmware/development'/variant
        receipt=json.loads((folder/'manifest.json').read_text())
        assert receipt['source_commit']==head and receipt['source_dirty'] is False
        assert receipt['build_check']=='PASS' and receipt['physical_tested'] is False
        assert receipt['target']=='esp32' and receipt['backend']==backend
        assert sha(receipt['compiler'])==receipt['compiler_sha256']
        for name,key in [('app.bin','app_sha256'),('sdkconfig','sdkconfig_sha256'),
            ('sdkconfig.json','sdkconfig_json_sha256'),('partition-table.bin','partition_table_sha256'),
            ('flasher_args.json','flasher_args_sha256'),('project_description.json','project_description_sha256')]:
            assert sha(folder/name)==receipt[key],(variant,name)
        for row in receipt['evidence']:
            assert sha(row['path'])==row['sha256'],row
        for row in receipt['build_logs']:
            assert sha(folder/row['file'])==row['sha256'],row
        image=(folder/'app.bin').read_bytes()
        descriptor=image_descriptor(image)
        assert len(image)==receipt['app_bytes'] and descriptor['elf_sha256']==receipt['elf_sha256']
        assert descriptor['version']==receipt['app_version'] and head[:8] in descriptor['version']
        assert not descriptor['version'].endswith('-dirty')
        assert image[0]==0xe9 and struct.unpack_from('<H',image,12)[0]==0
        position,checksum=24,0xef
        for index in range(image[1]):
            size=struct.unpack_from('<I',image,position+4)[0]
            position+=8
            assert size>0 and position+size<=len(image)
            for value in image[position:position+size]:checksum^=value
            position+=size
        end=((position+16)//16)*16-1
        assert image[end]==checksum and image[23]==1 and len(image)==end+33
        assert hashlib.sha256(image[:end+1]).digest()==image[end+1:]
        slots=partition_slots((folder/'partition-table.bin').read_bytes(),0x400000)
        limit=min(row['bytes'] for row in slots)
        assert limit==0x1b0000 and len(image)<=limit
        config=json.loads((folder/'sdkconfig.json').read_text())
        previous=json.loads((ROOT/'firmware/development'/('esp32-cyd2usb-native-network-settings-'+suffix)/'sdkconfig.json').read_text())
        changes={key:{'previous':previous.get(key),'current':config.get(key)} for key in sorted(set(previous)|set(config)) if previous.get(key)!=config.get(key)}
        assert changes=={'YORADIO_HTTP_REQUEST_BUFFER_RELEASE':{'previous':None,'current':True}},(variant,changes)
        assert not config.get('FREERTOS_UNICORE') and config['ESP_DEFAULT_CPU_FREQ_MHZ']==240
        assert not config.get('YORADIO_NATIVE_DIAGNOSTICS')
        build=Path(receipt['build_directory'])
        if not build.is_absolute():build=ROOT/build
        description=json.loads((build/'project_description.json').read_text())
        elf=build/description['app_elf']
        raw=elf.read_bytes()
        assert raw[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',raw,18)[0]==94
        assert sha(elf)==receipt['elf_sha256'] and sha(build/'config/sdkconfig.json')==receipt['sdkconfig_json_sha256']
        nm=Path(description['c_compiler']).with_name('xtensa-esp32-elf-nm.exe')
        command=[str(nm),'-S','--defined-only',str(elf)]
        output=subprocess.check_output(command)
        symbol_file=OUT/('sdk-symbols-'+suffix+'.log')
        symbol_file.write_bytes(output)
        symbols={}
        for line in output.decode().splitlines():
            fields=line.split()
            if len(fields)==4:
                symbols[fields[3]]={'address':int(fields[0],16),'bytes':int(fields[1],16),'type':fields[2]}
        assert ('custom_flac_decoder_feed' in symbols)==custom
        assert ('esp_flac_dec_register' in symbols)==(not custom)
        assert 'yoradio_http_client_release_request_buffer' in symbols
        assert 'native_output_metrics_snapshot' in symbols and 'native_output_metrics_end_write' in symbols
        selected={name:symbols[name] for name in ('s_output_metrics','s_output_metrics_lock')}
        assert selected['s_output_metrics']['bytes']==64 and selected['s_output_metrics_lock']['bytes']==8
        assert all(0x3ff80000<=row['address']<0x40000000 for row in selected.values())
        if backend=='pdm':
            for name in ('pdm_completion_queue_drop','native_output_metrics_queue_drop'):
                selected[name]=symbols[name]
                assert 0x40080000<=symbols[name]['address']<0x400a0000,(variant,name,symbols[name])
        compile_rows=json.loads((build/'compile_commands.json').read_text())
        overlay=[row for row in compile_rows if 'native-http-request-buffer' in row['file'] and Path(row['file']).name=='esp_http_client.c']
        assert len(overlay)==1 and 'xtensa-esp32-elf-gcc' in overlay[0]['command']
        overlay_file=Path(overlay[0]['file'])
        assert b'yoradio_http_client_release_request_buffer' in overlay_file.read_bytes()
        assert sha(overlay_file)==sha(ROOT/'.build/cyd-http-tx-target-01/esp_http_client.c')
        all_warnings=[line for row in receipt['build_logs'] for line in (folder/row['file']).read_text(errors='replace').splitlines() if re.search(r'\bwarning:',line)]
        environment_warnings=[line for line in all_warnings if line.startswith('warning:  Failed to clean temp activation directory with file ') and '[WinError 2]' in line]
        warnings=[line for line in all_warnings if line not in environment_warnings]
        assert len(warnings) in ({0,3} if backend=='legacy' else {0}),(variant,warnings)
        assert all(re.search(r"periph_rtc_apll_(?:freq_set|acquire|release)' is deprecated",line)
            and '/v5.5.4/components/driver/deprecated/i2s_legacy.c:' in line.replace('\\','/')
            for line in warnings),(variant,warnings)
        images.append(dict(variant=variant,backend=backend,custom_flac=custom,
            app_bytes=len(image),ota_slot_bytes=limit,ota_free_bytes=limit-len(image),
            app_sha256=receipt['app_sha256'],elf_sha256=receipt['elf_sha256'],
            manifest_sha256=sha(folder/'manifest.json'),config_changes=changes,
            integrated_symbols=selected,symbol_command=command,symbols_sha256=sha(symbol_file),
            http_overlay_source_sha256=sha(overlay_file),http_overlay_compile_row=overlay[0],warnings=warnings))
        images[-1]['sdk_environment_warnings']=environment_warnings

bindings={}
for name in ('audio_service.c','app_main.c','network_runtime.c'):
    relative='idf/esp32-cyd2usb-native/main/'+name
    previous=git('show','edccc3ac:'+relative).decode().replace('\r\n','\n')
    current=(ROOT/relative).read_text()
    calls=lambda text:re.findall(r'\bxTaskCreatePinnedToCore\([^;]+;',text,re.S)
    assert calls(previous)==calls(current) and calls(current),relative
    bindings[relative]={'source_sha256':sha(ROOT/relative),'unchanged_task_calls':calls(current)}
    if name=='audio_service.c':
        table=lambda text:re.search(r'static const pipeline_task_t task_config\[3\] = \{(.*?)\n    \};',text,re.S).group(1)
        assert table(previous)==table(current)
        bindings[relative]['unchanged_three_owner_table']=table(current)
relative='idf/esp32-cyd2usb-native/main/board_config.h'
assert git('show','edccc3ac:'+relative).replace(b'\r\n',b'\n')==(ROOT/relative).read_bytes().replace(b'\r\n',b'\n')
report=dict(passed=True,source_commit=head,physical_tested=False,images=images,
    unchanged_task_bindings=bindings,board_config_sha256=sha(ROOT/relative),
    scope='Six complete GCC Xtensa application exports, image/checksum/OTA/config/codec symbols and final integrated PDM callback/helper IRAM plus state/lock DRAM. No physical IRQ latency, DMA behavior, live heap savings, task runtime or audio-quality claim.')
(OUT/'SDK.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'source_commit':head,'images':[{key:row[key] for key in ('variant','app_bytes','ota_free_bytes')} for row in images]},indent=2))
