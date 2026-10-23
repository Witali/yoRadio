from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / 'docs/ESP32_CYD_C3_TRANSFER_PLAN.md'
text = path.read_text(encoding='utf-8')
text = text.replace('Дата: 2026-10-18. Ветка:', 'Обновлено: 2026-10-19. Ветка:', 1)
old = '[Runtime profiles/reconnect/RSSI/power policy](CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md) и физическая AP/client проверка ещё впереди.'
new = '[Runtime N0–N3](CYD_NETWORK_RUNTIME_TRANSFER_DESIGN.md) реализован: immutable boot cache до пяти профилей, постоянный owner, late reconnect/wrap/APSTA, checked snapshot и RSSI validity/age. [Квалификация](../tests/results/cyd-network-runtime-20261019/README.md): owner44 + четыре controls, loader/netif/rollback/HTTP/WS/UI и Xtensa component compile проходят. N4 generation-aware power, N5 hostname/AP timeout, новые полные exports и физическая AP/client проверка остаются.'
assert text.count(old) == 1
text = text.replace(old, new, 1)
rows = text.splitlines()
for index, row in enumerate(rows):
    if row.startswith('| CYD-C3-12 |'):
        rows[index] = '| CYD-C3-12 | В работе | [Optional custom FLAC runtime](CYD_FLAC_TRANSFER_DESIGN.md) подключён к actual CYD decoder task; vendor остаётся default. [Квалификация](../tests/results/cyd-flac-runtime-20261019/README.md): 520 exact PCM сравнений, 4304 metadata-prefix случая, 24 allocation failure/reopen и lifecycle/maintenance controls, actual Xtensa custom/vendor component compile. Source depth и PCM16 разделены; workspace освобождается до maintenance ACK. Полные app exports, custom-path QEMU, watchdog/ресурсы и физический vendor/custom A/B остаются. |'
        break
else:
    raise AssertionError('missing FLAC plan row')
text = '\n'.join(rows) + '\n'
text += '''
- 2026-10-19, CYD-C3-09 N0–N3: заменён однопрофильный event-handler runtime
  на постоянного owner. Initial/manual cycle начинается с первого профиля,
  late outage — с последнего успешного, затем wrap. Один admitted manual cycle
  включает pending mailbox; APSTA сохраняется. Checked getter не отдаёт старый
  IP/RSSI при pending link event; WS/UI учитывают validity и отдельный AP state.
  [Frozen source/reports](../tests/results/cyd-network-runtime-20261019/README.md)
  фиксируют historical negatives отдельно от 44 текущих owner scenarios.
  Новая задача priority 2/core 0/stack 4096; прежние audio/display/bootstrap
  affinity и аппаратные настройки сохранены. N4/N5 остаются открыты.
- 2026-10-19, CYD-C3-12: optional custom FLAC интегрирован без переключения
  vendor default. [Доказательства](../tests/results/cyd-flac-runtime-20261019/README.md)
  связывают actual decoder/PCM/lifetime с shared core, включая source depth,
  metadata EOF, persistent OOM/reopen и concurrent maintenance cleanup до ACK.
  Component compile не считается полным application export или физической
  квалификацией; эти gates остаются в плане.
'''
path.write_text(text, encoding='utf-8')
