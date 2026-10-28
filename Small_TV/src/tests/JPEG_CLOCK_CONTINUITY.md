# Часы во время декодирования JPEG

Checkpoint 2026-10-23, неизменённая app `abf14143…`, ELF `896558f5…`, production
source `64edeef9…`. Новая прошивка для этих проверок не собиралась.

## Отдельный LCD gate

`jpeg_clock_qemu.py` обычным HTTP загружает progressive gray8 JPEG 240×240,
508 bytes в пятый слот. Аппаратные breakpoints наблюдают вход/настоящий возврат
`jpeg_decoder_decode`, renderer и final coordinator yield. RAM, PC, регистры,
код и время гостя не подменяются. На входе и конце принятого кадра foreground
decoder активен, background выключен, cache slot=4. HTTP служит только trigger.

| Тема | Кадров при decode | Максимальный интервал, guest s | Контроль без finish |
|---|---:|---:|---:|
| classic | 5 | 1.069112 | 20 кадров |
| simple | 4 | 1.101215 | 13 кадров |
| dial | 4 | 1.116249 | 14 кадров |

Все темы проходят настоящий переход минуты. Наблюдается весь library call:
prefix/tail ≤2.5 guest s. Simple captures приходятся на законченные second/reset
updates, промежуточные no-op вызовы не считаются кадрами. Контроль выполняет
start/chunk, но не finish: decoder не активен. Все 6 owned VM stopped/reaped.

Каждый полный кадр, 57600 pixels, сверяется с двумя исполненными RV32 references:
нашим и literal factory. Reference панели начинают чистыми, без копирования
actual pixels, масок или допусков. Factory corrections объявлены: bounded
classic fields/weather, perpendicular dial strokes; simple использует полное
построение заводской темы, учитывая исправление перехода минуты. Только isolated
native reference пропускает запуск RTOS photo owner, который не рисует часы.
Actual QEMU main исполняет guard/worker полностью. JPEG/BMP/glyph bodies в
reference не подменяются готовыми пикселями.

Итого 13 workload +47 control =60 кадров /3456000 actual pixels без отличий.
16 workload +12 control отрицательных вариантов отчёта отклонены. Evidence reader
дополнительно сверяет календарное приращение с guest time (допуск1.25s на секундную
дискретизацию и границу renderer). Это один representative gray fixture, не
приёмка LCD при всех CMYK/RGB/12-bit нагрузках.

## Отдельный HTTP/storage gate

`photo_owner_qemu.py` повторно проверен на этой app. Persistent HTTP/1.1
`WeatherFixture` заменяет одноразовую HTTP/1.0 заглушку: SLIRP guestfwd сохраняет
host stream между guest TCP connections. GET timeout10s, zero errors и обычная
одна persistent connection сохранены.

| Fixture | Результат finish | Host s в этой QEMU |
|---|---|---:|
| full-cmyk12 | 200 OK | 305.000 |
| flat-sampling44-8 | 400 backing-capacity; required=524288 available=460800 | 0.500 |
| flat-sampling44-12 | 400 heap-headroom; required=15379 available=6692 | 0.484 |
| rich-progressive420-8 | 200 OK | 146.438 |
| flat-gray-progressive-8 | 200 OK | 37.250 |

862 GET/0errors, max0.875host s. Отдельный no-upload control:160 GET/0errors,
max0.500host s. По2cold процесса на gate остановлены/reaped. После настоящего
перезапуска source gray JPEG читается HTTP побайтно. Protected flash сохранна;
no-upload control дополнительно сохраняет все media/cache/scratch bytes.

Первый опыт с прежней host границей240s завершился TimeoutError на CMYK12.
Отдельная пассивная диагностика показала прогресс: guest~10.198→19.369s,
issued program bytes60672→292352, calls1858→6535, decoder активен, media mutex
свободен, I/O errors нет. Stack candidates не являются unwound trace.
Полный повтор с explicit `--finish-host-timeout 900` завершился. Default240,
GET10s и firmware budgets180guest s/200000calls/64MiB read/16MiB program прежние.
`-icount shift=3,align=off,sleep=on`: host seconds не измеряют скорость MCU.

## Readback и восстановление

`photo_flash_evidence.py` независимо читает stable wire format обоих journal
banks: CRC, commit footer, canonical fields, newest generation, layout/codec IDs,
source SHA и весь scattered RGB565 frame. Выбор newest предшествует identity
check: foreign newest не позволяет откатиться к старому matching.

Unmodified upstream libjpeg-turbo3.2.0 (`c85e6b…`, executable `ec59abe8…`) получил
57600 gray samples=128. Явный независимый RGB565 R5/G6/B5 little endian даёт
SHA `a3ec07b0…`: совпадает с физическими115200bytes и journal после3LCD decodes,
HTTP workflow/cold и recovery. Source/frame damage и newest foreign codec с
правильным CRC/footer отвергаются evidence reader; это не injected power cuts.

`jpeg_decode_recovery_qemu.py` получает настоящий **остановленный** backing первого
незавершённого CMYK12 опыта. Slot5 не ready, size=0. Обычный новый boot и gray
upload/finish успешны: journal1→2, source/frame SHA точны, protected bytes прежние.
Это остановка VM до publication, не brownout посреди physical program/erase.
Live failure copy, сделанная до stop, не используется как stopped input.

[Сокращение coefficient writes](JPEG_COEFFICIENTS.md) остаётся включённым через
production `jpeg_backing`. Cache предотвращает повторный decode при показе;
[cold photo gate](PHOTO_PREFETCH.md) доказал0JPEG program/erase attempts. Новая
HTTP cold проверка подтверждает persistence, но не cache-hit rendering без записи.

## Повторение и дальнейшие проверки

```powershell
python -B Small_TV/src/tests/jpeg_clock_qemu.py --qemu-root FROZEN --output NEW_LCD
python -B Small_TV/src/tests/jpeg_clock_qemu.py --qemu-root FROZEN --control --output NEW_CONTROL
python -B Small_TV/src/tests/photo_owner_qemu.py --qemu-root FROZEN --finish-host-timeout 900 --output NEW_HTTP
python -B Small_TV/src/tests/photo_owner_qemu.py --qemu-root FROZEN --control --output NEW_HTTP_CONTROL
python -B Small_TV/src/tests/jpeg_decode_recovery_qemu.py --qemu-root FROZEN --interrupted-flash STOPPED_FLASH --expected-frame-sha256 a3ec07b094d96c0fc6b420ba1a8666639a108c9e925c5f199c3e8f6f8ee10745 --output NEW_RECOVERY
python -B Small_TV/src/tests/verify_jpeg_clock_evidence.py --proof Small_TV/qemu/parity/jpeg-clock-continuity-validation-20261023.json
```

Proof сохраняет lossless sector deltas полных4MiB images, captures/logs/reports,
исторический timeout/diagnostic inputs отдельно от acceptance. Frozen QEMU47files,
app/ELF/source/fixtures/helpers связаны SHA. Factory ELF/ROM повторно проверены
при упаковке; ROM сверена с actual prepared metadata. Эти дополнительные archival
fingerprints не выдаются за runtime input capture.

Открыты полный current target format/RAM/stack/fault matrix, LCD под принятыми
CMYK12/rich RGB progressive, реальные разрывы publication/program/erase,
clients/reconnect/churn, whole-image audit/full/24h/hardware. Network/LCD gates
отдельны. SDK/frozen QEMU не изменены, физических действий и push нет.
