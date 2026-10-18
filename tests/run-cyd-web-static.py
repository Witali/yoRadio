"""Execute CYD static workers and native page control logic with host I/O seams."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'idf/esp32-cyd2usb-native/main'
sys.path.insert(0, str(ROOT / 'tools/codec_benchmark'))
from run_output_dma_host import host, run
spec = spec_from_file_location('cyd_functions', ROOT/'tests/run-cyd-lifecycle.py')
helpers = module_from_spec(spec)
spec.loader.exec_module(helpers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--skip-page', action='store_true', help='Qualify C boundaries separately while the page is under development')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), ROOT/'tests/native/cyd_web_static_test.c', ROOT/'tests/native/cyd_web_start_test.c',
             ROOT/'tests/cyd-native-page.test.js', MAIN/'web_static.c', MAIN/'web_static.h',
             MAIN/'web_pages.cpp', MAIN/'web_pages.h', MAIN/'web_service.c', MAIN/'web_upload.h', MAIN/'web_reboot.h', MAIN/'web_ota.h',
             MAIN/'web_wifi.h', MAIN/'web_time.h',
             ROOT/'tests/run-cyd-lifecycle.py', ROOT/'idf/components/native_stream/include/json_buffer.h',
             ROOT/'idf/components/native_wifi_store/include/native_wifi_public.h',
             ROOT/'tools/codec_benchmark/run_output_dma_host.py']
    hashes = {}
    for path in files:
        relative = path.relative_to(ROOT)
        data = path.read_bytes()
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
        target = out/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    frozen = out/'sources'
    static_source = re.sub(r'^#include[^\n]*\n', '',
        (frozen/MAIN.relative_to(ROOT)/'web_static.c').read_text(encoding='utf-8'), flags=re.M)
    (out/'production.inc').write_text(static_source, encoding='utf-8')
    frozen_helpers_spec = spec_from_file_location('frozen_cyd_functions', frozen/'tests/run-cyd-lifecycle.py')
    frozen_helpers = module_from_spec(frozen_helpers_spec)
    frozen_helpers_spec.loader.exec_module(frozen_helpers)
    fixture = out/'fixtures'
    (fixture/'www').mkdir(parents=True, exist_ok=True)
    (fixture/'data').mkdir(exist_ok=True)
    for name, data in {'theme.css':b'raw css','empty.js':b'', 'empty.js.gz':b'compressed',
                       'large.css':b'x'*5100}.items():
        (fixture/'www'/name).write_bytes(data)
    (fixture/'data/playlist.csv').write_bytes(b'station\thttps://example.test/audio\n')
    (fixture/'data/wifi.csv').write_bytes(b'private data')
    binary = out/'static-test'
    try:
        (out/'build.log').write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(out),'-I'+host(frozen/'idf/components/native_wifi_store/include'),
            host(frozen/'tests/native/cyd_web_static_test.c'),'-o',host(binary)]))
        log = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                   'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(fixture)])
        (out/'test.log').write_bytes(log)
        web = (frozen/MAIN.relative_to(ROOT)/'web_service.c').read_text(encoding='utf-8')
        startup_source = frozen_helpers.function(web, 'capabilities_handler') + 'static atomic_bool s_started;\n' + frozen_helpers.function(web, 'web_service_start')
        (out/'web-start.inc').write_text(startup_source, encoding='utf-8')
        start_binary = out/'start-test'
        (out/'start-build.log').write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
            '-I'+host(out),'-I'+host(frozen/'idf/components/native_stream/include'),
            host(frozen/'tests/native/cyd_web_start_test.c'),'-o',host(start_binary)]))
        start_log = run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
                         'UBSAN_OPTIONS=halt_on_error=1',host(start_binary)])
        (out/'start.log').write_bytes(start_log)
        caps = json.loads(next(line.split('=',1)[1] for line in start_log.decode().splitlines() if line.startswith('CAPABILITIES=')))
        assert caps['audio_output'] == 'PDM "test"' and caps['websocket_clients'] == 2
        assert all(caps[name] is False for name in ('equalizer','sd','display_controls','wifi_profiles'))
        assert caps['ota'] is True and caps['ota_max_bytes']==0x1B0000 and caps['ota_body_max_bytes']==0x1B0000+4096
        assert all(caps[name] is True for name in ('playlist_upload','asset_upload','wifi_upload'))
        assert caps['upload_max_bytes'] == 98304 and caps['upload_max_files'] == 16
        assert caps['upload_name_max_bytes'] == 22 and caps['wifi_file_max_bytes'] == 799
        assert caps['wifi_body_max_bytes'] == 4096 and caps['wifi_ssid_max_bytes'] == 31 and caps['wifi_password_max_bytes'] == 63
        assert caps['nativeWiFiApi']=='/api/native/wifi' and caps['nativeWiFiMaxProfiles']==5
        assert caps['nativeWiFiPrivateExport'] is False and caps['nativeTimeApi']=='/api/native/time'
        controls = {}
        mutations = [
            ('missing_admission_guard','static', static_source.rindex('    if (!native_wifi_public_static_uri'),
             'web_static_handler(&r)==ESP_OK && r.status==404'),
            ('missing_worker_guard','static', static_source.index('    if (!native_wifi_public_static_uri'),
             'open_calls==opens'),
            ('wrong_wifi_edit_route','startup', None, 'route->handler==web_wifi_edit_handler'),
            ('missing_wifi_activation','startup', None, 'wifi_active && reboot_ready'),
        ]
        for name,kind,position,assertion in mutations:
            contents = static_source if kind=='static' else startup_source
            if kind=='static':
                end=contents.index('\n',contents.index('\n',position)+1)+1
                changed=contents[:position]+contents[end:]
            elif name=='wrong_wifi_edit_route':
                changed=contents.replace('.method=HTTP_POST, .handler=web_wifi_edit_handler',
                                         '.method=HTTP_POST, .handler=web_wifi_info_handler',1)
            else: changed=contents.replace('    web_wifi_activate();','    /* missing activation */',1)
            assert changed!=contents
            (out/('production.inc' if kind=='static' else 'web-start.inc')).write_text(changed)
            negative=out/(name+'-test')
            includes=['-I'+host(out),'-I'+host(frozen/'idf/components/native_wifi_store/include'),
                      '-I'+host(frozen/'idf/components/native_stream/include')]
            test=frozen/'tests/native'/('cyd_web_static_test.c' if kind=='static' else 'cyd_web_start_test.c')
            (out/(name+'-build.log')).write_bytes(run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
                '-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                *includes,host(test),'-o',host(negative)]))
            try:
                negative_log=run(['env','ASAN_OPTIONS=detect_leaks=0:halt_on_error=1',
                    'UBSAN_OPTIONS=halt_on_error=1',host(negative),*([host(fixture)] if kind=='static' else [])])
                failed=False
            except subprocess.CalledProcessError as error: negative_log=error.output;failed=True
            (out/(name+'.log')).write_bytes(negative_log)
            assert failed and b'Assertion' in negative_log and assertion.encode() in negative_log,(name,negative_log)
            assert b'ERROR: AddressSanitizer' not in negative_log and b'runtime error:' not in negative_log
            controls[name]={'detected':True,'expected_assertion':assertion}
            (out/('production.inc' if kind=='static' else 'web-start.inc')).write_text(contents)
        page = b''
        if not args.skip_page:
            page = subprocess.check_output(['node','--test',str(frozen/'tests/cyd-native-page.test.js')], stderr=subprocess.STDOUT)
            (out/'page.log').write_bytes(page)
    except subprocess.CalledProcessError as error:
        print(error.output.decode(errors='replace'), file=sys.stderr)
        raise
    (out/'report.json').write_text(json.dumps(dict(passed=True,physical_hardware=False,
        sanitizer='ASan/UBSan for actual static C functions; JavaScript executed in Node DOM/socket/fetch seams',
        source_sha256=hashes,page_tested=not args.skip_page,negative_controls=controls),indent=2)+'\n',encoding='utf-8')
    print(log.decode().strip())
    print(start_log.decode().strip())
    print(page.decode().strip())


if __name__ == '__main__':
    main()
