# Scan, фото и тема при переподключении AP-клиентов

`network_activity_qemu.py` дополняет проверку
[ухода любого AP-клиента](NETWORK_CLIENTS.md). Настоящий HTTP-запрос сначала
доходит до исполняемой функции в гостевой прошивке. В этой точке стенд меняет
присутствие внешнего клиента через QMP и проверяет, что HTTP future ещё не завершён.
Затем штатно исполняются тело функции, SDK callbacks, её возврат и HTTP-ответ.
Используются аппаратные RSP breakpoints; код/память/регистры/PC не подменяются.

Каждый из двух циклов содержит:

| Запрос | Наблюдаемая функция | Mask после изменения |
|---|---|---|
| GET `/scan` | `esp_wifi_scan_start` с blocking=1 | 2 — уходит первый |
| POST `/start_upload` | `photo_upload_start_detailed` | 3 — первый возвращается |
| MIME POST `/upload_chunk` | `photo_upload_chunk` | 1 — уходит второй |
| POST `/finish_upload` | `photo_upload_finish_detailed` | 3 — второй возвращается |
| POST `/setclocktype` | `settings_select_theme` | 2 — уходит первый |
| Повторный POST `/setclocktype` | `settings_select_theme` | 3 — первый возвращается |

Начальные два клиента имеют разные MAC/AID и DHCP-адреса. Перед следующим
шагом требуется действительная готовность DHCP, а переход проверяется по SDK
event bytes. HTTP проходит через общий мост и оставшегося peer; независимые
TCP-клиенты с отдельными host backends этим тестом не заявляются.

На неизменённом production app `9c1a83bd…` / ELF `76b5ce37…`, QEMU `7a9764712b`
(`cce6b471…`) получены 12 HTTP 200 на основных запросах, все три сети в каждом
scan и точные байты синтетического 508-byte JPEG после каждого цикла.
Дополнительно проверяется сохранённая тема через GET. HTTP-сервер стартовал
один раз и не останавливался. 14 SDK peer events включают два начальных и
12 переходов. Шесть callbacks попали внутрь наблюдаемых вызовов; остальные
пришли после возврата функции. У каждого изменения presence исходный HTTP
ещё был в работе в момент входа, что сохраняется отдельно.

Стенд не смешивает сетевую приёмку с LCD. Это native AP activity gate;
STA reconnect/weather, RF/WPA, продолжительный churn/soak и полный сетевой
жизненный цикл остаются отдельными пунктами. Заводской setup scan с известной
ошибкой обработки пустого результата и расширенный JPEG pipeline здесь не
выдаются за пройденный factory activity gate.

[`network-activity-validation-20261024.json`](../../qemu/parity/network-activity-validation-20261024.json)
содержит полный финальный отчёт, упорядоченные entry/return boundaries,
сырые SDK event bytes, ответы HTTP, ABI object и точные Git blobs модели QEMU.
29 raw items / 29 уникальных payloads, 25531 новых gzip bytes; прежние
неизменённые payloads используются повторно. Полная VM flash/RAM/UART не копируются.
Первый успешный pilot на один цикл хранится с **его** исходником; в финальную
приёмку входит отдельный запуск нового наблюдателя на два цикла. Обе ВМ остановлены
и reaped, production/SDK/QEMU source не изменены.

`verify_network_activity_evidence.py` повторно извлекает ABI из RV32 object,
сверяет адреса/entry instructions с exact ELF, воспроизводит MAC/AID transitions,
возвраты, HTTP и readback. Восемь negative controls отвергают уже завершённый
HTTP, подменённый MAC, неверную границу возврата, пропавшую сеть, изменённое фото,
повторный server handle, незавершённый процесс и ошибку finish.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_network_activity_evidence.py `
  --proof Small_TV/qemu/parity/network-activity-validation-20261024.json
```

После изменения наблюдателей используйте `--source-revision` с коммитом этого
checkpoint: исторические исходники читаются из Git без отката рабочей копии.
Для повторного живого прогона требуются явные `--qemu-root` с immutable tools,
`--qemu` с отдельным бинарником, `--abi` с target-derived layout и новая `--output`
директория. Критерий сохранённого gate — `--cycles 2`, значение по умолчанию.
