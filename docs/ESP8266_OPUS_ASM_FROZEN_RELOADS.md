# Opus ASM: повторные чтения стека без изменения компоновки

2026-09-14. Эксперимент по пункту 1
[списка возможностей](ESP8266_OPUS_ASM_OPTIMIZATION_OPPORTUNITIES.md).

## Кандидат и контроль

Основа — сохранённый tell-inline, `esp8266-opus-folding-control-v1`:
CPU160/QIO40, cache16, raw benchmark, пакеты заранее в RAM,
function/stage profiling и физический вывод выключены.

Восемь L32I, повторно читающих тот же private stack slot, заменены копией
уже загруженного регистра. В двухбайтовых местах используется MOV.N,
в трёхбайтовых — OR dst,src,src. Число инструкций, их длины и все адреса
остаются прежними: эксперимент проверяет удаление обращений к памяти,
а не экономию ROM или последующий сдвиг кода.

| Функция | Копия вместо второго чтения | Stack offset |
|---|---|---:|
| quant_partition | a3 = a7 | 28 |
| quant_band | a11 = a10 | 56 |
| quant_all_bands | a9 = a8 | 280 |
| quant_all_bands | a14 = a12 | 192 |
| opus_fft_impl | a3 = a11 | 68 |
| opus_fft_impl | a10 = a9 | 56 |
| opus_fft_impl | a11 = a10 | 180 |
| opus_fft_impl | a3 = a2 | 32 |

Offset относится к текущему frame каждой функции, не к глобальному адресу.
Переиспользуется ровно исходный live register; нового регистра, массива,
стека, IRAM или DRAM нет. C fallback, protected GCC snapshot и default
не меняются. Это post-link diagnostic variant, не новый production backend.

Артефакты:

- `firmware/development/esp8266-opus-frozen-reloads-control-v1/app.bin`;
- `firmware/development/esp8266-opus-frozen-reloads-candidate-v1/app.bin`;
- оба app по 903216 B, цель OTA slot не более 0xf0000 B;
- SHA256 кандидата: `a8f6c0a6cedea4108d7dfea61ddcaecb8996686fb1f26decb8cf86390d29c873`;
- SHA256 контроля: `0129559856a9b339ec8428d903fc3e9bd3a4489bc127f1ed7a310d127d310811`.

## Доказательство корректности

`tools/esp8266_opus_asm/frozen_reloads.cjs` находит каждый фрагмент в
reachable disassembly реального ELF. Требуются единственное совпадение,
непрерывные инструкции и отсутствие ветвления в середину фрагмента.
Symbolic private-stack model проверяет все конечные регистры для любых
входных значений; неизвестные операции, stores, calls, изменение SP,
не-stack loads и изменения SAR запрещены в доказательстве.

Данные стека принадлежат выполняемой задаче; этот аргумент не применяется
к volatile/MMIO, DMA или памяти, изменяемой другим владельцем. Прерывания
не отключаются. Восьми статических замен нельзя приписывать динамическую
частоту вызова без отдельного измерения.

Каждая инструкция-кандидат собирается настоящим LX106 assembler с
no-transform; её размер и дизассемблирование проверяются. ELF меняется
только в восьми указанных диапазонах. Все остальные байты, символы,
секции памяти, stack frames, литералы и адреса функций идентичны.

Штатный SDK elf2image v3 сначала воспроизводит исходный app побайтно,
затем упаковывает кандидат. В app разрешены только изменения этих восьми
инструкций, XOR checksum и appended SHA256. DIO в заголовке образа —
штатная упаковка SDK; сохранённая конфигурация bootloader/runtime QIO40.

Host-проверка parent tell-inline проходит 11 PCM-сценариев: пять основных
потоков, 320 кбит/с с пакетами 2,5/5/10/20 мс, 510 кбит/с и mixed/PLC/reset.
Guard/OOM self-tests сохранены. Это семантическая host-проверка родителя,
не исполнение нового Xtensa ASM на ПК. Эквивалентность восьми замен
проверяется отдельно symbolic/linked proof; физические PCM проверяются
непосредственно raw benchmark на плате.

## Проверки и измерения

- [x] Собрать два app и проверить неизменность layout/RAM и payload.
- [x] Шесть целевых regression tests, включая отрицательные проверки.
- [x] Повторить host PCM проверку родителя до 510 кбит/с.
- [ ] Десять физических A + десять B + десять повторных A.
- [ ] Сохранить все результаты, PCM hashes, максимумы и минимумы RAM/стека.
- [ ] Применить high-bitrate-first критерий и проверить размер эффекта
      относительно разброса; близость к шуму не называть ускорением.
- [ ] Вернуть обычную прошивку через OTA, проверить HTTP/WS и плейлист.

Производительность кандидата пока не подтверждена. Цель 70% не достигнута.

```powershell
node tools/esp8266_opus_asm/frozen_reloads.cjs
node --test tests/esp8266-opus-frozen-reloads.test.js
# OTA выполняется отдельно штатным check_prefill_board.cjs.
& tools/esp8266_opus_profile/run_raw_series.ps1 -Directory .build/opus-frozen-reloads-board/before -Fixtures firmware/development/esp8266-opus-asm-library/fixtures -Attempts 10 -IntervalMs 15000
# Затем отдельные candidate и after с проверкой нового OTA slot.
node tools/esp8266_opus_asm/report_frozen_reloads.cjs
```
