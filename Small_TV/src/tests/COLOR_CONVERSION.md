# Преобразование цветов и подготовка RGB565 для нового JPEG

Модуль `app/media/color_convert.c` отделён от настроек, JPEG, LCD transport и
сети. Два прежних helper RGB888↔RGB565 перенесены из `settings.c` с сохранением
имён и результатов. `settings.h` включает их новый общий header, поэтому ABI
существующих callers не меняется. SPI byte order по-прежнему задаёт display driver.

Новый `color_convert_row_rgb565` принимает grayscale/RGB/CMYK samples2–16бит,
использует переданные caller buffers, не выделяет heap и не вызывает I/O.
Для2–8бит используются byte samples, для9–16 —native-endian16-bit samples.
Unaligned input читается через `memcpy`. Перед выводом проверяются размер,
переполнение адреса/длины, отсутствие overlap и диапазон всех samples; ошибка
не оставляет частично изменённую строку. Пустая строка также отклоняется.

## Семантика цвета

- RGB8 сохраняет точное заводское усечение: R/B —старшие5бит, G —старшие6.
  Обратное преобразование повторяет старшие биты, как `0x42008a34`/`0x42008a6a`.
- Новые разрядности нормализуются из полного диапазона в0…255 с округлением,
  затем используется то же RGB565 усечение. Grayscale вычисляется один раз
  наpixel, восемь бит не требуют деления для нормализации.
- Две полярности CMYK заданы разными enum: conventional ink coverage и
  inverted Adobe samples. CMYK multiply выполняется до уменьшения разрядности;
  даже65535²+32767помещается вuint32. Чёрный компонент читается один раз наpixel.
- YCCK сначала преобразуется JPEG-библиотекой вCMYK; модуль не повторяет YCbCr
  transform и не угадывает формат по числу channels. Выбор полярности остаётся
  обязанностью будущего codec adapter.

Основание для явной полярности —
[upstream libjpeg3.2.0 documentation](https://github.com/libjpeg-turbo/libjpeg-turbo/blob/3.2.0/doc/libjpeg.txt),
раздел Special color spaces. Generic CMYK multiply предназначен для экранного
fallback; точный ICC color-management transform здесь не реализован. Наличие
CMYK/YCCK row conversion не объявляет полную поддержку этих JPEG в устройстве.

## Проверки2026-10-20

`color_convert_contract.py` выполняет literal factory RV32 bytes из исходного
ELF через Unicorn2.1.4, сверяя три диапазона code с assembly manifest. Ни один
LCD/format adapter при этих вызовах не используется.

| Проверка | Результат |
|---|---|
| Factory RGB565→RGB888, все возможные входы |65536совпадений с перенесённым C helper|
| Factory RGB888→RGB565: все channel values, boundaries, deterministic random |3304совпадения|
| Строки samples: все grayscale values2…16, RGB/CMYK boundaries и все8-bit C/K pairs |61row,549676samples; aligned/unaligned совпадают|
| Настоящий RV32 converter: начало/середина/конец строк |141row с exact pixels и canaries|
| Неверные arguments/последний sample наhost |65отказов без изменения buffers|
| Те же классы ошибок наRV32, включая32-bit size/address wrap |68отказов без изменения buffers|
| Настоящие JPEG: baseline/progressive/gray/RGB/CMYK/YCCK8/12-bit |66images;18из них независимо сверены с Pillow12.3.0/libjpeg-turbo3.1.4.1|

Standalone RV32 ELF:540bytes code+4read-only bytes, без unresolved-symbol stubs
и writable data. Converter frame96bytes, два прежних helper —0. Это размер и
frame данного модуля, не всей библиотеки, task stack или firmware heap.

Host DLL и RV32 ELF собирает `tests/color_convert/build.py`, фиксируя source и
binary hashes. Для MSVC нужен Developer Command Prompt; `--cmake`, `--ninja`
и `--toolchain-bin` принимают абсолютные пути. Пример:

```text
python Small_TV/src/tests/color_convert/build.py --output .build/color --toolchain-bin RV32_BIN
python Small_TV/src/tests/color_convert_contract.py --build .build/color --dependency-root DEPENDENCIES --python-modules ORACLE_MODULES --python-modules ELFTOOLS_MODULES --jpeg-build JPEG_BUILD --fixtures INDEPENDENT_IMAGES --fixtures RICH_12BIT_IMAGES --output .build/color-contract
```

Требуются Pillow, pinned Unicorn и pyelftools. Повторные output directories не
перезаписываются. RGB reference arithmetic использует независимое floating-point
округление; максимальный sample нечётный, поэтому точная половина при данных
делениях невозможна и различие tie rules не влияет на результат.

## Полная сборка и отдельные проверки подсистем

Получена сборка C8FD: app SHA256
`c8fdc949757d3caf6f433d67c1b682d7f14a0a556d413bd30a9e4874fc787e6d`,
1170032bytes при partition1536000bytes. ELF368AB7B5, source aggregateE34BEBEB.
DEBUGoff. App/bootloader/manifest сохранены в
`firmware/development/small-tv-esp32c2-reconstructed` этой ветки.

- Повторены5531native checks:107JPEG,98animation frames,18BMP, settings,
  uploads и HTTP handlers —pass.
- Отдельный display cold gate:2factory+2native процесса, каждый полный кадр
  совпадает с реальным factory setup referenceACC588AB.62inputs unchanged;
  network/executed=false, без HTTP readiness criterion.
- Отдельный network gate безLCD device: оба варианта дают HTTP и свежую SNTP
  до/после reset.59inputs unchanged; display/executed=false. Это не RF/WPA test.

Первый display запуск в sandbox закончился QMP startup timeout до наблюдения
кадра; процесс9856затем отсутствовал. Он сохранён как неуспешная попытка, причина
одним этим timeout не установлена. Новый отдельный запуск вне sandbox прошёл;
старый отчёт не переименован вpass. Pillow getdata deprecation warnings в color
test log также сохранены; это не ошибка decode или расхождение pixels.

Proof: `Small_TV/qemu/parity/color-conversion-validation-20261020.json` с raw
reports, logs, frames, fixtures и matching ELF. Это scoped acceptance новой
сборки, не полная regression/24h или physical acceptance.

Текущая app использует два прежних helper; новый row API ещё не подключён к
media decoder и удаляется section GC. В app остаётся прежний TJpgd. Libjpeg
candidate не включён: нужны NOR-aware backing/износ, codec adapter/privacy,
общий heap/stack, HTTP/upload/display и новые full/soak проверки. Продолжающиеся
full/H10 B50D относятся к прежним app/ELF/source и не доказывают C8FD acceptance.
