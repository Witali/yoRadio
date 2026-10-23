from pathlib import Path
import json
import shutil
import hashlib
import re

root = Path(__file__).resolve().parents[1]
out = root / 'tests/results/network-power-transfer-20261019'
report = json.loads((out / 'SDK.json').read_text(encoding='utf-8'))
custom = json.loads((out / 'SDK-custom.json').read_text(encoding='utf-8'))
layout = json.loads((out / 'SDK-layout.json').read_text(encoding='utf-8'))
assert report['passed'] and custom['passed'] and layout['passed']
assert report['source_commit'] == custom['source_commit']
custom_dir = root / 'firmware/development' / custom['variant']
custom_manifest = json.loads((custom_dir / 'manifest.json').read_text(encoding='utf-8'))
warnings = [line for entry in custom_manifest['build_logs']
            for line in (custom_dir / entry['file']).read_text(encoding='utf-8', errors='replace').splitlines()
            if re.search(r'\bwarning:', line)]
assert not warnings, warnings
lines = ['# Network runtime and audio power: production images', '',
         f"Five GCC application images from clean source `{report['source_commit']}`.",
         'The full transfer remains active. These are software build/export gates;',
         'no board was flashed or reset and no physical power or playback claim is made.', '',
         '| Image | App bytes | OTA spare bytes | Saved development firmware |',
         '| --- | ---: | ---: | --- |']
for image in report['images']:
    lines.append(f"| {image['label']} | {image['app_bytes']} | {image['ota_free_bytes']} | [app.bin](../../../firmware/development/{image['variant']}/app.bin), [manifest](../../../firmware/development/{image['variant']}/manifest.json) |")
lines += [f"| CYD custom FLAC, PDM | {custom['app_bytes']} | {custom['ota_free_bytes']} | [app.bin](../../../firmware/development/{custom['variant']}/app.bin), [manifest](../../../firmware/development/{custom['variant']}/manifest.json) |", '',
    '[SDK.json](SDK.json) checks compiler/app/ELF/configuration/metadata hashes',
    'and unchanged CYD stream/core 0 priority 3, decoder/core 1 priority 5,',
    'output/core 1 priority 6. The new CYD network owner retains its N1 budget',
    '(core 0, priority 2, stack 4096); N4 adds no task or stack-budget changes.',
    'Existing display/bootstrap bindings and C3 task priorities are preserved.', '',
    'All SDK configuration values were compared with the previous time/private',
    'Wi-Fi images. C3 is unchanged. The only new CYD keys select vendor FLAC',
    'by default. The custom image changes exactly those two mutually exclusive',
    'decoder selectors relative to vendor PDM. Flash, clocks, pins, Wi-Fi buffers,',
    'socket limits and SNTP capacity remain unchanged.', '',
    '[SDK-images.json](SDK-images.json) independently checks all five application',
    'segment bounds, XOR/SHA256, descriptor/ELF identity, ESP32 chip 0 versus',
    'ESP32-C3 chip 5, Xtensa versus RISC-V ELF machine, partition MD5/ranges and',
    'both OTA slots. CYD uses 0x1b0000-byte slots, C3 0x1d0000.', '',
    '[SDK-custom.json](SDK-custom.json) verifies the complete custom Xtensa',
    'application link. Its ELF defines `custom_flac_decoder_feed` and omits',
    '`esp_flac_dec_register`; vendor PDM has the opposite selection. It is an',
    'optional development image; vendor remains the default. The unchanged',
    '[current custom host regression](flac-after-n4/report.json) repeats 520',
    'exact PCM comparisons, 16 lifecycle groups and three semantic controls',
    'with all 23 frozen source hashes matching current production inputs.', '',
    'PDM, continuous DAC, custom FLAC PDM and C3 have zero compiler warnings.',
    'Legacy DAC retains the same three pinned IDF 5.5.4 APLL deprecation',
    'warnings; the adapter still uses `use_apll=false`. Full Clang AST and',
    'behavioral evidence remain in [README.md](README.md), which is immutable',
    'because its bytes are bound by firmware evidence hashes.', '',
    '[Actual ELF DWARF](SDK-layout.json) gives `native_network_power_snapshot_t`',
    '20 bytes and `wifi_config_t` 184 bytes on both pinned targets. CYD',
    '`network_profiles_t` is 481, `network_snapshot_t` 80 and `network_owner_t`',
    '760 bytes. The shared policy has 40 bytes of named static symbols on CYD',
    'and 32 on C3, excluding linker padding; the single-core lock is optimized',
    'out on C3. These are target structure/symbol sizes, not simultaneous heap',
    'peaks or measured task stack margins.', '',
    'N5 hostname/AP-timeout runtime and UI integration remains open; its',
    'persistence precursor alone is tested. [Read-only integration notes](n5-integration-plan.json)',
    'record the checked hostname OOM behavior and the guarded reboot/OTA-lease',
    'boundary. Custom FLAC QEMU, the remaining custom backend build matrix,',
    'RF/DHCP/AP channel behavior, hardware DMA/heap/stack/power measurements,',
    'memory/TLS policy and architecture-specific decoder work remain in the',
    '[full plan](../../../docs/ESP32_CYD_C3_TRANSFER_PLAN.md).', '']
(out / 'SDK.md').write_text('\n'.join(lines), encoding='utf-8')
for name in ['qualify-power-sdk.py', 'qualify-power-custom.py', 'verify-power-images.py',
             'inspect-power-layout.py', 'run-power-production.ps1', 'export-power-c3.py', 'export-stage02.py']:
    target = out / 'sdk-qualification' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / '.build' / name, target)
shutil.copyfile(root / '.build/n5-integration-review/plan.json', out / 'n5-integration-plan.json')
source = root / '.build/cyd-flac-after-n4-readonly-01'
flac_report = json.loads((source / 'report.json').read_text(encoding='utf-8'))
assert flac_report['passed']
for relative, expected in flac_report['source_sha256'].items():
    assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected, relative
for path in source.rglob('*'):
    if path.is_file() and path.suffix in {'.c','.cpp','.h','.inc','.py','.json','.log'} and '__pycache__' not in path.parts:
        target = out / 'flac-after-n4' / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, target)
print('Recorded five production images, target layout and current FLAC regression')
