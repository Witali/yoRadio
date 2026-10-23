from pathlib import Path
import hashlib,json,shutil
root=Path(__file__).resolve().parents[1]
out=root/'.build/flac-shared-sdk-components';out.mkdir(exist_ok=False)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=[root/'idf/components/custom_flac'/n for n in ['CMakeLists.txt','custom_flac_adapter.cpp','custom_flac_adapter.h']]
sources += [root/'idf/esp32c3-oled-native/components/custom_flac'/n for n in ['CMakeLists.txt','custom_flac_adapter.cpp','custom_flac_adapter.h']]
sources += [root/'idf/esp32-cyd2usb-native/CMakeLists.txt',Path(__file__),root/'.build/run-flac-component-sdk.ps1']
sources += [p for folder in ['yoRadio/src/audioI2S/flac_decoder','idf/components/custom_codec_support'] for p in (root/folder).rglob('*') if p.is_file()]
report={'passed':True,'scope':'Actual pinned RISC-V/Xtensa custom_flac component compilation and archive, not application link, target execution or physical performance. Shared adapter/core algorithms unchanged.','source_sha256':{p.relative_to(root).as_posix():digest(p) for p in sources},'targets':{}}
for p in sources:
    dest=out/'sources'/p.relative_to(root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
for board,project in [('c3','esp32c3-oled-native'),('cyd','esp32-cyd2usb-native')]:
    build=root/'idf'/project/'build-c3-transfer'
    database=json.loads((build/'compile_commands.json').read_text())
    selected=[entry for entry in database if Path(entry['file']).resolve() in {root/'idf/components/custom_flac/custom_flac_adapter.cpp',root/'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'}]
    assert len(selected)==2,(board,selected)
    assert all('-DFLAC_OUTPUT_FRAMES=512' in entry['command'] and '-DFLAC_SEGMENTED_WORKSPACE=1' in entry['command'] for entry in selected)
    assert all('-DFLAC_BYTEWISE_RICE=1' not in entry['command'] for entry in selected)
    logs=[]
    for kind in ['out','err']:
        src=root/f'.build/flac-shared-{board}-component.{kind}.log';shutil.copyfile(src,out/f'{board}-{kind}.log');logs.append(src.read_text(errors='replace'))
    warnings=[line for text in logs for line in text.splitlines() if 'warning:' in line or 'error:' in line]
    assert not warnings,warnings
    lib=build/'esp-idf/custom_flac/libcustom_flac.a';assert lib.is_file()
    config=build/'config/sdkconfig.json';shutil.copyfile(config,out/(board+'-sdkconfig.json'))
    report['targets'][board]={'units':selected,'library_sha256':digest(lib),'library_bytes':lib.stat().st_size,'sdkconfig_sha256':digest(config),'compiler_diagnostics':warnings}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'targets':list(report['targets']),'source_files':len(sources)}))
