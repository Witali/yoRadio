from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / 'docs/ESP32_CYD_C3_TRANSFER_PLAN.md'
data = path.read_text(encoding='utf-8')
old = 'Для N5 готово только checked NVS хранилище; hostname/AP timeout wiring и физическая AP/client проверка остаются.'
new = ('[N5 hostname/AP timeout](../tests/results/cyd-network-settings-20261020/README.md) подключён к runtime, HTTP и WebUI: '
       '82 owner случая/12 controls, HTTP80/7, UI48/14, actual NVS/reboot и полный Clang52/86warnings/0errors проходят. '
       'Настройки сохраняются без разрыва online соединения; optional AP timeout default0 использует checked immediate reboot lease без durable pending запроса. '
       'SDK exports новых настроек и физическая AP/client/DHCP/reboot проверка остаются.')
assert data.count(old) == 1
data = data.replace(old, new)
data = data.replace('Обновлено: 2026-10-19.', 'Обновлено: 2026-10-20.', 1)
data += ('\n- 2026-10-20, CYD-C3-09 N5: `de1fa7a3a` добавил reserved immediate restart, '
         '`a7012415d` подключил hostname/AP timeout, persistence и WebUI. '
         '[Frozen квалификация](../tests/results/cyd-network-settings-20261020/README.md) сохраняет '
         '82/12 owner, HTTP80/7, UI48/14, actual NVS и reboot arbitration обеих плат. '
         'Независимая проверка воспроизвела и закрыла stale timer-label после save/GET failure. '
         'Полный Clang52 прошёл с 86 warnings/0errors: пять новых low-risk diagnostics разобраны без suppression. '
         'N0–N5 программно реализованы; SDK новых настроек, физические gates и остальные этапы плана открыты.\n')
path.write_text(data, encoding='utf-8')
print('Updated N5 plan status; production SDK exports and physical gates remain open')
