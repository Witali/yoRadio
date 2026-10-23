import hashlib, json, shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'.build/sdk-web-components-final'
out.mkdir(exist_ok=False)
hashes={}
paths=['idf/components/native_web_transport/native_web_transport.c',
       'idf/components/native_web_transport/include/native_web_transport.h']
results={}
for board,project,build in [('c3','esp32c3-oled-native','build-lint-web-transfer'),('cyd','esp32-cyd2usb-native','build-lint-health')]:
    dst=out/board;dst.mkdir()
    folder=root/'idf'/project/build
    for suffix in ['out.log','err.log']:
        shutil.copyfile(root/'.build'/f'{board}-web-http-fallback-objects.{suffix}',dst/suffix)
    shutil.copyfile(folder/'native-httpd-rfc6455/manifest.json',dst/'httpd-overlay.json')
    shutil.copyfile(folder/'config/sdkconfig.json',dst/'sdkconfig.json')
    commands=json.loads((folder/'compile_commands.json').read_text())
    ws=[c for c in commands if Path(c['file']).name=='websocket_service.c']
    assert len(ws)==1 and 'clang' in ws[0]['command']
    (dst/'websocket-compile-command.json').write_text(json.dumps(ws,indent=2)+'\n')
    results[board]={'passed':True,'build_directory':str(folder.relative_to(root)),
                    'units':'main, native_web_transport, esp_http_server',
                    'wrapper_command':f'.build/run-web-diagnostic.ps1 -Board {board} -Build {build} -Log {board}-web-http-fallback-objects'}
    paths.extend('idf/'+project+'/'+p for p in ['CMakeLists.txt','main/CMakeLists.txt','main/Kconfig.projbuild',
                        'main/web_service.c','main/websocket_service.c'])
for relative in paths:
    path=root/relative;target=out/'sources'/relative
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
    hashes[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
(out/'report.json').write_text(json.dumps({'passed':True,'scope':'Pinned Clang component object builds, no final ELF/application image or physical qualification.',
        'targets':results,'source_sha256':hashes},indent=2)+'\n')
print('Frozen component build evidence for C3 and CYD')
