import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
out=root/'tests/results/native-runtime-transfer-20261018'
report=json.loads((out/'SDK.json').read_text())
layout=json.loads((out/'SDK-layout.json').read_text())
assert report['passed'] and layout['passed']
for board,label in [('cyd','CYD PDM'),('c3','C3 stereo PDM')]:
    image=next(item for item in report['images'] if item['label']==label)
    assert image['elf_sha256']==layout['targets'][board]['elf_sha256']
lines=['# Time and private Wi-Fi: target SDK qualification','',
       '2026-10-18. Four GCC production images from clean source',
       f"`{report['source_commit']}`. Application/ELF hashes, embedded ELF identity,",
       'saved SDK configuration and available OTA space are verified in',
       '[SDK.json](SDK.json). Host behavioral and lint evidence is in [HOST.md](HOST.md).',
       'No board was flashed or reset for this checkpoint.','',
       '| Image | App bytes | OTA spare bytes | Saved firmware |',
       '| --- | ---: | ---: | --- |']
for item in report['images']:
    lines.append(f"| {item['label']} | {item['app_bytes']} | {item['ota_free_bytes']} | [app.bin](../../../firmware/development/{item['variant']}/app.bin), [manifest](../../../firmware/development/{item['variant']}/manifest.json) |")
lines += ['',
    'All configurations are compared with the preceding OTA checkpoint. The',
    'only CYD change is `LWIP_SNTP_MAX_SERVERS: 1 -> 2`, required by the two-server',
    'time service. C3 configuration is unchanged. The production wrapper applies',
    'that minimum only in each isolated build configuration; prior images and',
    'external seed files remain intact. Existing flash, Wi-Fi buffers, socket limits,',
    'audio backend, GPIO and SDK selections remain as in those qualified profiles.',
    '',
    'CYD stream stays on core 0 / priority 3, decoder on core 1 / priority 5 and',
    'output on core 1 / priority 6. Existing display/network bootstrap bindings',
    'are also covered by the actual startup/event host campaign. These are',
    'source/build checks, not physical task scheduling measurements.',
    '',
    'Actual final ELF DWARF sizes are recorded in [SDK-layout.json](SDK-layout.json).',
    'They describe target structures, excluding allocator/RTOS overhead; they',
    'do not establish simultaneous allocation peaks or free heap/stack margin.',
    '',
    '| Structure | CYD bytes | C3 bytes |',
    '| --- | ---: | ---: |']
common=sorted(set(layout['targets']['cyd']['bytes'])&set(layout['targets']['c3']['bytes']))
for name in common:
    lines.append(f"| `{name}` | {layout['targets']['cyd']['bytes'][name]} | {layout['targets']['c3']['bytes'][name]} |")
lines += ['',
    'The symbol logs preserve actual linked-target object symbol sizes for',
    'network/time, Wi-Fi owner/HTTP/I/O, shared SNTP, WebSocket and TLS units.',
    'They are a baseline for later CYD memory work, not an optimization or',
    'physical performance claim.',
    '',
    'Compiler warning instances per image: '+', '.join(f"{x['label']} {len(x['compiler_warnings'])}" for x in report['images'])+'.',
    'The legacy DAC build retains pinned IDF 5.5.4 deprecated APLL API warnings;',
    'its existing configuration disables those APLL branches. Raw build logs',
    'and compiler/configuration identity accompany each development image.',
    'SDK/Kconfig and CMake advisories remain visible in those logs; they are',
    'separate from the compiler-warning counts above.',
    '',
    'Experimental Xtensa Clang 20.1.1 optimized code generation remains affected',
    'by the recorded `time_settings_valid` vector instruction-selection crash.',
    'Complete clang-tidy AST analysis and these production GCC builds pass',
    'separately. No production source workaround or warning suppression was added.',
    '',
    'Remaining gates include runtime profile/reconnect/RSSI/power integration,',
    'physical RF/AP and clock behavior, flash power loss, TLS/audio/TFT resource',
    'measurements and long-running playback. Custom CYD FLAC runtime and private',
    'Xtensa codec ABI work remain separate plan stages.','']
(out/'SDK.md').write_text('\n'.join(lines),encoding='utf-8')
print('Wrote SDK.md for',report['source_commit'])
