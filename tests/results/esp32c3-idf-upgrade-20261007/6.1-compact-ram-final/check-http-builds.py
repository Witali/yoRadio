import hashlib, json, sys
from pathlib import Path
sys.path.insert(0,'tools')
from patch_httpd_content_length import GUARD
rows=[]
for variant in ('production','profile','deep-sleep','rtc32k'):
    base=Path('firmware/development/esp32c3-idf-6.1-compact-ram-'+variant)
    target=Path('firmware/development/esp32c3-idf-6.1-compact-ram-http-'+variant)
    old=(base/'sdkconfig').read_bytes();new=(target/'sdkconfig').read_bytes()
    assert old==new,variant
    manifest=json.loads((target/'manifest.json').read_text())
    assert hashlib.sha256((target/'app.bin').read_bytes()).hexdigest()==manifest['image']['sha256']
    build=Path(manifest['build_directory'])
    generated=build/'yoradio_httpd/httpd_parse.c'
    assert generated.read_text().count(GUARD)==1
    commands=json.loads((build/'compile_commands.json').read_text())
    parsers=[r for r in commands if Path(r['file']).name=='httpd_parse.c']
    assert len(parsers)==1 and Path(parsers[0]['file']).resolve()==generated.resolve()
    rows.append(dict(variant=variant,config_identical_to_original=True,image=manifest['image'],
        sdkconfig_sha256=hashlib.sha256(new).hexdigest(),
        generated_http_parser_sha256=hashlib.sha256(generated.read_bytes()).hexdigest(),
        only_generated_parser_compiled=True))
Path('.build/idf-upgrade/default-config-6.1-compact-ram-http.json').write_text(json.dumps(dict(passed=True,builds=rows),indent=2)+'\n')
print('PASS: four unchanged configurations, image hashes and generated HTTP parser compilation')
