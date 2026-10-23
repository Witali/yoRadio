import hashlib,json,subprocess
from pathlib import Path
root=Path.cwd()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for mode in ['custom','vendor']:
    build=root/('.build/cyd-flac-runtime-sdk-'+mode)
    config=json.loads((build/'config/sdkconfig.json').read_text())
    assert bool(config.get('YORADIO_FLAC_DECODER_CUSTOM'))==(mode=='custom')
    assert bool(config.get('YORADIO_FLAC_DECODER_ESPRESSIF'))==(mode=='vendor')
    entries=json.loads((build/'compile_commands.json').read_text()); rows=[]
    sources=[root/'idf/esp32-cyd2usb-native/main'/name for name in ['audio_service.c','decoder_registration.c']]
    if mode=='custom': sources += [root/'idf/components/custom_flac/custom_flac_adapter.cpp',root/'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp']
    for source in sources:
        entry=next(row for row in entries if Path(row['file']).resolve()==source)
        before=sha(source)
        result=subprocess.run(entry['command'],cwd=entry['directory'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        (build/(source.name+'.compile.log')).write_bytes(result.stdout)
        assert result.returncode==0, result.stdout.decode(errors='replace')
        assert before==sha(source)
        rows.append(dict(source=source.relative_to(root).as_posix(),sha256=before,command=entry['command'],exit_code=result.returncode,diagnostics=result.stdout.decode(errors='replace')))
    nm=Path(entries[0]['command'].split()[0]).with_name('xtensa-esp32-elf-nm.exe')
    audio=build/'esp-idf/main/CMakeFiles/__idf_main.dir/audio_service.c.obj'
    registration=build/'esp-idf/main/CMakeFiles/__idf_main.dir/decoder_registration.c.obj'
    symbols={}
    for obj in [audio,registration]:
        result=subprocess.run([str(nm),'-u',str(obj)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True)
        symbols[obj.name]=result.stdout.decode();(build/(obj.name+'.nm.log')).write_bytes(result.stdout)
    assert ('custom_flac_decoder_feed' in symbols[audio.name])==(mode=='custom')
    assert ('esp_flac_dec_register' in symbols[registration.name])==(mode=='vendor')
    report=dict(passed=True,selection=mode,scope='Actual Xtensa GCC compilation and object-symbol inspection of CYD integration units; custom mode also compiles real adapter/core. Application link, QEMU and physical execution are not covered.',units=rows,sdkconfig_sha256=sha(build/'sdkconfig'),config_json_sha256=sha(build/'config/sdkconfig.json'),symbols=symbols)
    (build/'integration-compile.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS actual Xtensa GCC '+mode+'-selected CYD integration units')
