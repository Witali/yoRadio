from pathlib import Path
import hashlib
import json
import shutil

root = Path(__file__).resolve().parents[1]
folder = root / 'tests/results/cyd-network-settings-20261020'
sdk = json.loads((folder / 'SDK.json').read_text(encoding='utf-8'))
assert sdk['passed'] and len(sdk['images']) == 6
lines = [
    '# CYD N5 and full FLAC backend matrix: SDK application exports', '',
    'Six complete GCC application images from clean source `' + sdk['source_commit'] + '`.',
    'No board was flashed or reset. Vendor FLAC remains the default; custom is',
    'selected only in three explicit development images.', '',
    '| FLAC | Audio output | App bytes | OTA spare bytes | Saved image |',
    '| --- | --- | ---: | ---: | --- |',
]
for image in sdk['images']:
    variant = image['variant']
    lines.append('| ' + image['flac_selection'] + ' | ' + image['backend'] + ' | ' +
                 str(image['app_bytes']) + ' | ' + str(image['ota_free_bytes']) + ' | ' +
                 '[app.bin](../../../firmware/development/' + variant + '/app.bin), ' +
                 '[manifest](../../../firmware/development/' + variant + '/manifest.json) |')
lines += ['', '[SDK.json](SDK.json) verifies every app/ELF/compiler/configuration/evidence',
    'receipt, the ESP32 chip 0/Xtensa ELF identity, all application segments and',
    'XOR/SHA256, partition MD5/ranges and both 0x1b0000-byte OTA slots.',
    'Full nm logs prove `custom_flac_decoder_feed` appears only in custom images',
    'and `esp_flac_dec_register` only in vendor images.', '',
    'Every vendor SDK configuration is unchanged from its N4 backend image.',
    'Each custom configuration differs by exactly the two FLAC selectors.',
    'Board pins, clocks, DMA-related settings, socket limits, Wi-Fi buffers and',
    'SNTP capacity are preserved. The three audio owners retain stream/core 0',
    'priority 3, decoder/core 1 priority 5 and output/core 1 priority 6. Their',
    'complete unchanged source, three-row task table and creation loop are',
    'compared with the previous checkpoint. Display/bootstrap and the permanent',
    'Wi-Fi owner calls, stack macros and board configuration are unchanged.', '',
    'Five logs have zero compiler warnings. The clean custom legacy build',
    'retains the three known IDF 5.5.4 APLL deprecation warnings; its adapter',
    'still sets `use_apll=false`. The vendor legacy incremental build reused that',
    'unchanged driver object and emitted no new compiler warning. The full',
    '[52-unit Clang campaign](README.md) remains separate from GCC code generation.', '',
    '[Actual final ELF DWARF](SDK-layout.json) reports network owner 936 bytes',
    '(N4: 760), network snapshot 160 (N4: 80), settings record structure 25 and',
    'runtime settings view 80. Profiles remain 481, Wi-Fi config 184 and power',
    'snapshot 20 bytes. These structure sizes exclude mutex/SDK allocation costs,',
    'allocator/RTOS overhead, simultaneous heap peaks and actual stack headroom.', '',
    'The full custom backend application build/export matrix is now complete.',
    'Custom decoder QEMU PCM/guards/lifecycle execution and physical vendor/custom',
    'A/B, RF/DHCP/AP/restart, DMA/watchdog/heap/stack/power and long playback remain',
    'open in the [transfer plan](../../../docs/ESP32_CYD_C3_TRANSFER_PLAN.md).',
    'The ESP32-C3 production source was unchanged by this N5 integration; its',
    'prior N4 image and independently repeated ordinary reboot API gate remain',
    'recorded separately. No C3 hardware settings are imported into CYD.', '']
(folder / 'SDK.md').write_text('\n'.join(lines), encoding='utf-8')
for name in ['qualify-n5-sdk.py', 'inspect-n5-layout.py', 'verify-n5-firmware-index.py']:
    shutil.copyfile(root / '.build' / name, folder / 'helpers' / name)

plan = root / 'docs/ESP32_CYD_C3_TRANSFER_PLAN.md'
data = plan.read_text(encoding='utf-8')
old = 'SDK exports новых настроек и физическая AP/client/DHCP/reboot проверка остаются.'
new = ('[Шесть полных CYD exports](../tests/results/cyd-network-settings-20261020/SDK.md) из чистого `195cd3b0e` '
       'проверены для vendor/custom FLAC и всех трёх backend; конфигурации и core bindings сохранены. '
       'Физическая AP/client/DHCP/reboot проверка остаётся.')
assert data.count(old) == 1
data = data.replace(old, new)
old = 'Остальные custom backend exports, custom-path QEMU, watchdog/ресурсы и физический vendor/custom A/B остаются.'
new = ('[Все три custom backend exports](../tests/results/cyd-network-settings-20261020/SDK.md) собраны и проверены; '
       'custom-path QEMU, watchdog/ресурсы и физический vendor/custom A/B остаются.')
assert data.count(old) == 1
data = data.replace(old, new)
old = '[Пять сборок после network/power](../tests/results/network-power-transfer-20261019/SDK.md) проверены: три CYD backend, C3 и CYD custom FLAC PDM;'
new = ('[Шесть CYD сборок после N5](../tests/results/cyd-network-settings-20261020/SDK.md) проверены: vendor/custom FLAC во всех трёх backend; '
       '[C3 N4 image](../tests/results/network-power-transfer-20261019/SDK.md) сохраняет отдельный baseline;')
assert data.count(old) == 1
data = data.replace(old, new)
data += ('\n- 2026-10-20, CYD-C3-09/12/15: [шесть чистых SDK exports](../tests/results/cyd-network-settings-20261020/SDK.md) '
         'из `195cd3b0e` закрывают build/export matrix vendor/custom FLAC × PDM/continuous/legacy. '
         'Проверены image/ELF/compiler/config/evidence hashes, обе OTA slots и прежние core/priority/stack. '
         'Actual DWARF owner936/snapshot160/settings25/runtime80 зафиксированы без заявления о свободном heap/HWM. '
         'Custom-path QEMU и физическая приёмка остаются открыты.\n')
plan.write_text(data, encoding='utf-8')

design = root / 'docs/CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md'
data = design.read_text(encoding='utf-8')
old = ('и программно проверены. Полные SDK exports новых настроек и физическая\n'
       'приёмка остаются открытыми.')
new = ('и программно проверены. [Шесть SDK exports](../tests/results/cyd-network-settings-20261020/SDK.md)\n'
       'новых настроек сохранены; физическая приёмка остаётся открытой.')
assert data.count(old) == 1
design.write_text(data.replace(old, new), encoding='utf-8')
print('Recorded six checked production exports and updated remaining gates')
