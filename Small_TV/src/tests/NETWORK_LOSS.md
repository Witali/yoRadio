# Управляемая потеря пакетов и DHCP-повторы QEMU

`network_loss_qemu.py` запускает неизменённый native app `9c1a83bd…` /
ELF `76b5ce37…`, наблюдает две реальные виртуальные ассоциации с разными MAC
и теряет ровно один выбранный пакет второго клиента. Первый клиент и HTTP
должны продолжать работать. LCD не участвует в критерии; RF/WPA не заявляются.

Новые отключаемые QMP controls находятся в отдельном модуле QEMU
`hw/net/esp32c3_wifi_fault.c`: `softap-drop-next` и `softap-client-faults`.
В маске по 7 бит на каждого из трёх peer: probe request, authentication request,
association request, DHCP Discover, Request, Offer, ACK. Пакет потребляет свой
бит один раз. Сохраняются только счётчик и время, payload не журналируется.
Недопустимые биты отвергаются до изменения состояния. При нулевой маске
классификация и чтение времени не выполняются; обычный STA traffic исключён.

Это потеря на протокольной границе виртуального клиента после обычного guest
radio TX completion. Физические 802.11 ACK, шифрование и радиоканал так не
эмулируются. Существующие случайные link-loss controls остаются отдельными.

## Найденная и исправленная ошибка

На QEMU `287d95e1b1` после одной потери DHCP клиент оставался в state 6/7 без
таймера и повторной отправки. Наблюдались 12 guest s после потери, при этом
соседний клиент и сервер выдавали HTTP 200. Это ошибка модели, а не прошивки.

| Потерянный пакет | До исправления | После исправления |
|---|---|---|
| Probe request | Восстановление | Восстановление |
| Authentication request | Восстановление | Восстановление |
| Association request | Восстановление | Восстановление |
| DHCP Discover | Не восстановился за 12 guest s | Один повтор, DHCP завершён |
| DHCP Request | Не восстановился за 12 guest s | Один повтор, DHCP завершён |
| DHCP Offer | Не восстановился за 12 guest s | Один повтор, DHCP завершён |
| DHCP ACK | Не восстановился за 12 guest s | Один повтор, DHCP завершён |

QEMU `b85483c98d` добавляет retransmission deadlines с backoff 4/8/16/32/64 s,
jitter ±1 s с точностью до миллисекунды и итоговым пределом 64 s. Uniform jitter
получается через rejection sampling. Дедлайны проверяются существующими событиями
beacon, без программной задержки прошивки или busy wait. ACK отменяет таймер,
NAK начинает новую транзакцию, reassociation/reset очищают acquisition state.
Рекомендации по повторам: [RFC 2131 §4.1](https://www.rfc-editor.org/rfc/rfc2131.html#section-4.1).

У клиентов теперь свежие разные XID при начале транзакции. Повторы сохраняют
XID; parser принимает ответ только для соответствующего peer/lease. Ранее
использовался один постоянный XID. Constructors согласуют BOOTREQUEST,
chaddr и client identifier. Lease renewal/rebinding этим изменением не реализованы.

## Доказательства и совместимость

Before binary SHA:
`51b6746191d5dc910487ab1540b4279979f50a30eeec5da7fa74054f0674fb1a`.
After binary SHA:
`6d9d82665330a6f567d04eac9563ed05d2d14bdb47329d78e9f306fce3761a90`.

[`network-loss-validation-20261024.json`](../../qemu/parity/network-loss-validation-20261024.json)
сохраняет 14 actual before/after runs. Четыре успешных **before controls** имеют
`recovery_acceptance=false`: они доказывают воспроизведение дефекта и не считаются
приёмкой восстановления. Все семь after runs восстановились. У DHCP — ровно
один повтор, у здорового клиента — ноль; XID разных peer различны и стабильны.
112 negative controls отвергают подменённые SDK bytes, отсутствие потери,
непотреблённый fault, отключённого соседа, HTTP error, неверный результат recovery,
отсутствие проверки маски и неостановленный процесс.

Pure C protocol module прошёл 351 case, 905 усечённых чтений перед защитной
страницей, 10 000 случайных non-DHCP inputs и все 14 007 комбинаций backoff/jitter.
Проверены новые XID, поздние ответы и alias-safe начало транзакции.
Заводская прошивка прошла two-peer / primary departure / zero→survivor regression.
C3 default/modular прошли отдельные 60-second boot/console/panic/input checks.
Xtensa остался побайтно прежним `821d9807…`; известный CYD IDF6 PHY gap не закрыт.

В архиве 61 raw item / 54 payloads, 116266 новых gzip bytes с повторным
использованием прежних данных. Есть точные Git blobs обеих версий модели,
raw counters/time/state/SDK observations, unit report/source и regression reports.
Полные VM flash/RAM/UART не добавляются. Все 15 C2 и 2 C3 процесса этой серии
остановлены и reaped. App/SDK/physical board не изменялись.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_network_loss_evidence.py `
  --proof Small_TV/qemu/parity/network-loss-validation-20261024.json `
  --source-revision 98fedc62f
```

Исторический replay использует исходники `98fedc62f`. Следующий checkpoint
добавляет `--all-stages` и проверяет семь потерь подряд для любого из двух peer.
Повторная потеря Discover воспроизвела ошибку IP demux при задержанном первом
клиенте; она исправлена в QEMU `21a8d6dd8c`. Обе проверки задержки и обе
совмещённые последовательности после исправления прошли. См.
[NETWORK_STALLED_PEER.md](NETWORK_STALLED_PEER.md). Prolonged churn/soak,
произвольные последовательности потерь, полный network gate и аппаратная
RF/WPA приёмка остаются открытыми.
