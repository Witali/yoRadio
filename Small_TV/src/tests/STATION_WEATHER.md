# Погода при отключении и восстановлении STA

`station_weather_qemu.py` проверяет station-режим отдельно от AP-клиентов и LCD.
Работает неизменённый app `9c1a83bd…` / ELF `76b5ce37…` на QEMU `7a9764712b`
(`cce6b471…`). Только localhost fixtures, синтетические настройки и API key
`disabled`. RF/WPA и доступ к настоящему погодному сервису не проверяются.

`station_event_layout.py` извлекает из точного ELF/DWARF константы STA_START=2,
STA_DISCONNECTED=5, GOT_IP=0, адреса/размеры atomic globals и `ip_event_got_ip_t`.
Структура имеет 20 байт, адрес IPv4 начинается с offset 4. Ни структура другого
SDK, ни предположения по документации не подставляются вместо текущего ABI.

Последовательность каждого из двух случаев:

1. Получить валидную погоду и дождаться idle worker.
2. Запросить обновление через обычный `/updateCity`, удержать ответ на локальном
   погодном сервере. Доказать, что worker RUNNING, а старый cache не изменён.
3. Выключить внешнюю виртуальную AP. На входе **реального** SDK disconnect
   callback восстановить только AP, затем исполнить тело callback и обычный
   reconnect/DHCP. Не изменять guest connected flag, RAM, PC или код.
4. Наблюдать DISCONNECTED с connected=0/retries=1 и GOT_IP с connected=1/retries=0,
   сохранённым `10.0.2.15` и выключенным setup AP.
5. Освободить удержанный ответ, дождаться idle. Затем запросить отдельную свежую
   погоду с уникальной humidity=78/79 и проверить реальную новую публикацию.
   Прочитать тему обычным HTTP GET.

Один случай удерживает HTTP 200 с отрицательной температурой, второй — HTTP 503
с тем же JSON. В проверенном исполнении оба погодных запроса завершились при
обрыве транспорта **до освобождения ответа**, старый cache сохранился побайтно.
Это не доказательство получения полного HTTP 503: отказ от разбора полученного
503 JSON проверяется отдельно в погодном gate. Свежие ответы после восстановления
различаются по SHA тела и humidity, поэтому старый ответ не может выдаваться за
успешный recovery. Ожидание fixture заняло около 1,6 host s из её лимита 30 s;
гостевой HTTP timeout не менялся.

Финальный прогон: два реальных отключения, три GOT_IP (включая первоначальный),
два сохранённых cache и две свежие публикации; четыре refresh POST и два theme
GET прошли с HTTP 200. Один start/ноль stop HTTP-сервера, одна загрузка ROM,
без panic/watchdog. Pilot и финальный процесс остановлены и reaped. Production,
SDK и QEMU source не менялись.

[`station-weather-validation-20261024.json`](../../qemu/parity/station-weather-validation-20261024.json)
хранит 32 raw items / 32 payloads с 30274 новыми gzip bytes. Повторно используются
неизменённые старые payloads. Сохраняются реальные SDK IP bytes, состояния
atomic globals, raw weather cache, sanitized серверные request records и точные
Git blobs QEMU; полные flash/RAM/UART ВМ не копируются. Pilot имеет собственный
исходник, совпадающий с его hash; финальный прогон содержит дополнительные
HTTP/cache/timing observations и не смешивается с предыдущей версией стенда.

`verify_station_weather_evidence.py` повторно выводит ABI из ELF, связывает
инструкции/адреса с trace, декодирует raw doubles/text/generation и проверяет
ретраи, HTTP и fresh-body hashes. Девять negative controls отвергают отсутствие
disconnect, неверный IP, несброшенные retries, раннюю публикацию, stale recovery,
перезапись cache при ошибке, повторный server handle, лишнюю перезагрузку и
неостановленный процесс.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_station_weather_evidence.py `
  --proof Small_TV/qemu/parity/station-weather-validation-20261024.json
```

Для исторического producer используйте `--source-revision` с коммитом этого
checkpoint. Это чтение Git objects без отката рабочей копии. Selected STA
weather/recovery проверен; длительный churn/soak, управляемые потери кадров,
полная сетевая и аппаратная приёмка остаются открытыми.
