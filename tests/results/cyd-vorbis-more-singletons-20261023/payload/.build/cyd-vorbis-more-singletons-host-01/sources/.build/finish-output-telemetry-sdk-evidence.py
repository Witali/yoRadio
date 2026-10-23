from pathlib import Path
import hashlib
import json

ROOT=Path.cwd()
telemetry=ROOT/'tests/results/cyd-output-telemetry-20261020'
http=ROOT/'tests/results/cyd-http-request-buffer-20261020'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
report=json.loads((telemetry/'SDK.json').read_text())
assert report['passed'] and len(report['images'])==6
rows=['# CYD output telemetry and HTTP buffer production checkpoint\n',
    'All six complete GCC applications were built/exported from clean source `'+report['source_commit']+'`.\n',
    'The production exporter independently checks ESP32/Xtensa identity, image/ELF hashes, image checksum and appended SHA256, both OTA slots, pinned tools/configuration and raw evidence receipts. No board operation was performed.\n',
    '| Backend / FLAC | App bytes | OTA free bytes | Compiler warnings |',
    '| --- | ---: | ---: | ---: |']
for row in report['images']:
    label=row['backend']+' / '+('custom' if row['custom_flac'] else 'vendor')
    rows.append('| '+label+' | '+str(row['app_bytes'])+' | '+str(row['ota_free_bytes'])+' | '+str(len(row['warnings']))+' |')
rows.extend(['',
    'Each `firmware/development/esp32-cyd2usb-native-output-telemetry-<variant>/` contains the successful hand-off application, configuration, partitions, flash recipe, logs and manifest. Existing development checkpoints and versioned releases were preserved.',
    '',
    'Relative to each matching N5 image, the only sdkconfig change is the added default-enabled `YORADIO_HTTP_REQUEST_BUFFER_RELEASE`. Hardware clocks/pins, DMA geometry, codec selections, quiet diagnostics profile, cores/priorities/stacks and OTA partitions retain their baseline. The three-owner task table and board configuration are checked against `edccc3ac`.',
    '',
    'Final ELF symbols verify both PDM callback and metrics queue-drop helper in IRAM, plus the 64-byte state and 8-byte lock in DRAM. Both DAC variants retain the state/lock and driver counters. These static sizes do not measure heap savings, runtime overhead or IRQ latency. Quiet/diagnostic helper object evidence remains in the initial archive.',
    '',
    'All six actual SDK compile databases select the hash-audited build-local HTTP source, byte-identical to the separately compiled whole-source Xtensa checkpoint. The linked release symbol and correct vendor/custom FLAC symbols are present. SDK installations were not patched in place.',
    '',
    'If legacy driver warnings are present, they are exclusively the three known IDF 5.5.4 APLL deprecation diagnostics; their exact raw lines are retained in `SDK.json`. No new warning was suppressed. The complete Clang53 checkpoint remains 86 baseline warnings and zero errors.',
    '',
    'The vendor PDM environment log also records one SDK activation cleanup warning: a temporary file was already absent (WinError 2). Pinned `tools/export_utils/shell_types.py` only warns while removing old activation files and continues; the SDK source is copied in `appendix-tools`. This is recorded separately from compiler diagnostics. The first local qualification attempt rejected it because its warning classifier was too broad; only that classifier changed, without rebuilding or modifying any image.',
    '',
    'Physical playback/HTTP/HTTPS/WebUI/OTA, live memory savings, DMA/IRQ behavior, audio quality, watchdog/resource margins and prolonged operation remain open. This appendix does not close stages 12, 13, 14 or physical acceptance.',
    '',
    '`SDK.json` retains all six receipts, configuration differences, selected ELF symbols/addresses, compile rows and hashes. `appendix-tools/` preserves the exact local qualification/build helpers used. The raw initial archive files and bound README/HOST reports were not changed.'])
(telemetry/'SDK.md').write_text('\n'.join(rows)+'\n')
tools=telemetry/'appendix-tools';tools.mkdir(exist_ok=False)
for name in ('qualify-output-telemetry-sdk.py','qualify-output-telemetry-sdk-attempt01.py','run-output-telemetry-production.ps1'):
    (tools/name).write_bytes((ROOT/'.build'/name).read_bytes())
(tools/'sdk-shell_types.py').write_bytes(Path('C:/Work/yoRadio/.idf/v6.0.2/tools/export_utils/shell_types.py').read_bytes())
(tools/'qualification-history.json').write_text(json.dumps({'first_attempt_exit':1,
    'first_attempt_scope':'Local post-build verifier only; all six exporter receipts were already PASS.',
    'reason':'An SDK old-temporary-activation-file cleanup warning (WinError 2) was classified as a compiler warning.',
    'correction':'Classify only that exact confirmed SDK warning separately; keep all other compiler diagnostics strictly checked.',
    'firmware_rebuilt_or_modified':False,'final_qualification_passed':True},indent=2)+'\n')
link={'passed':True,'source_commit':report['source_commit'],
    'qualification_path':'../cyd-output-telemetry-20261020/SDK.json',
    'qualification_sha256':sha(telemetry/'SDK.json'),
    'images':[{'variant':row['variant'],'app_sha256':row['app_sha256'],
        'manifest_sha256':row['manifest_sha256'],'http_overlay_source_sha256':row['http_overlay_source_sha256']} for row in report['images']],
    'physical_tested':False}
(http/'SDK-link.json').write_text(json.dumps(link,indent=2)+'\n')
(http/'SDK.md').write_text('# Linked CYD application gate\n\nAll six GCC production applications from clean source `'+report['source_commit']+'` passed the [production matrix](../cyd-output-telemetry-20261020/SDK.md). Every compile database selects the same byte-exact audited HTTP overlay as the original whole-source Xtensa object gate, enables the release option, and every ELF defines the release extension. Relative to each matching N5 configuration, only this new option changed.\n\n`SDK-link.json` binds the complete qualification and six image/manifest hashes. Host/SDK evidence remains bounded as documented; no physical HTTP/TLS result or 4096-byte heap-saving claim is implied. The initial README and all raw reports remain unchanged.\n')
for base in (telemetry,http):
    path=base/'manifest.json'
    manifest=json.loads(path.read_text())
    old=dict(manifest['files'])
    for name,row in old.items():
        expected=row if isinstance(row,str) else row['sha256']
        assert sha(base/name)==expected,name
    for file in sorted(base.rglob('*')):
        if not file.is_file() or file==path:continue
        name=file.relative_to(base).as_posix()
        if name not in old:manifest['files'][name]={'sha256':sha(file),'bytes':file.stat().st_size}
    assert all(manifest['files'][name]==row for name,row in old.items())
    manifest['sdk_appendix']={'source_commit':report['source_commit'],'physical_tested':False,
        'qualification_sha256':sha(telemetry/'SDK.json')}
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print('Extended without changing',len(old),'prior file records:',base.name,len(manifest['files']))
