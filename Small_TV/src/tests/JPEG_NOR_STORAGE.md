# NOR storage core для JPEG

Checkpoint 2026-10-20: `storage/jpeg_nor.c/.h` реализует настоящий алгоритм
sector read/modify/erase/program поверх транспортных callbacks. Он пока не
включён в production CMake и не выполняет запись в подключённое устройство.
Readonly [ownership guard](JPEG_OWNERSHIP_GUARD.md) теперь также подготовлен
отдельно. Atomic metadata, его production authorization/build integration,
ESP-IDF adapter и libjpeg integration остаются обязательными этапами.

## Контракт записи

ESP-IDF требует ранее стёртые данные для записи: NOR программирует биты `1→0`,
а erase адрес/размер должны быть sector-aligned. Основание: pinned
`components/spi_flash/include/esp_flash.h` и
[официальная SPI Flash API для ESP32-C2](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c2/api-reference/peripherals/spi_flash/index.html).
В этом модуле сектор — 4096 bytes; transport page geometry задаётся явно,
поддержаны 128/256-byte pages. Это контракт адаптера, не автоматическое
определение физического чипа по JEDEC ID.

- При open проверяются полные диапазоны, переполнения, сортировка/пересечения,
  точная округлённая logical capacity и покрытие независимым allowlist.
  Неверные параметры не меняют handle и не вызывают transport.
- Descriptors копируются в handle. Logical file может состоять из нескольких
  несмежных physical extents. Чтение/стирание/запись никогда не перескакивает
  через gaps; защищены также padding последнего logical sector и его соседи.
- Один выровненный 4096-byte cache объединяет частичные записи. Dirty reads
  видят новые байты без вынужденного flush. Eviction/sync/успешный close
  сохраняют сектор; abort отбрасывает RAM без I/O.
- Flush сначала сравнивает весь старый сектор. Если байты совпадают, program/
  erase не нужны; если достаточно `1→0`, программируются только изменённые pages.
  При `0→1` стирается ровно один owned sector, проверяется весь erase result,
  затем восстанавливаются все non-FF pages, включая неизменённые данные.
- В конце записи весь сектор читается и сравнивается. Частичный erase/program,
  даже сообщивший success, не разрешает успешный sync. Любая I/O/verify ошибка
  блокирует дальнейший I/O этого handle до abort/reopen.

Этот слой **не атомарен при потере питания**: частично изменённые owned sectors
остаются частичными. До их перезаписи metadata layer обязан durably invalidate
старый cache entry, а публиковать новый — только после flush/hash verification.
Нельзя использовать старую RAM cache как доказательство восстановления flash.

Owner сериализует операции. Allowlist — доверенная capability от будущего
resource/layout guard, не произвольные адреса из HTTP. Подготовленный guard
проверяет matching immutable resources/partitions и ownership stamp; transport
ещё должен подключить эту проверку перед выдачей capabilities. Один поиск FF
или full assets hash после пользовательских загрузок для этого не подходит.

## Проверки

`tests/jpeg_nor/run.ps1` собирает production-intended C core с MSVC `/W4 /WX`.
Transport model проверяет каждый адрес, page alignment и отсутствие program
`0→1`. Независимый expected result — flat byte array, который целиком сравнивается
с simulated flash после sync; sparse holes и padding не исключаются из проверки.

- 3000 детерминированных случайных overwrite/read/sync операций с 128/256-byte
  pages: переходы через page/sector/extent boundaries, dirty read-after-write.
- 83 fault scenarios: каждый из 66 read/erase/program callback ordinals в
  полном RMW, плюс 17 silent short erase/program. После ошибки — никаких новых
  обращений, abort/reopen и чтение реальных частично изменённых flash bytes.
- Все 7 stores актуального planner: scratch, metadata и пять кадров. Проверены
  начало/конец/cross-extent writes, logical-end padding и сохранность всего
  остального 4 MiB образа. Это RAM model, не физическая память устройства.
- Отдельно: no-op/coalesced writes, `1→0` без erase, explicit abort, contiguous
  capabilities, nulls, wrap/alias/bounds, попытки выйти из разрешённых ranges.
- 6 отдельно скомпилированных mutants должны упасть на runtime assertions:
  пропуск erase, потеря остальных pages, обход allowlist, пропуск write/erase
  verification и stale reads вместо dirty cache.

Первоначальный allowlist mutant прошёл ранний corpus: отсутствовал тест выхода
за **последний** allowed range. Реальная реализация такой запрос отвергала.
`FIXED_TEST` добавляет final-boundary/beyond-final cases. Первый failed mutation
report, executable и точный прежний test source сохранены; окончательные шесть
controls отвергаются. Число 1334640 assertions не является процентом покрытия.

В random workload модель насчитала 3780 erase callbacks и 90720 program callbacks.
Это synthetic stress, не JPEG traffic/endurance measurement. Core считает issued
calls/requested bytes, включая failed operations; successful counters означают
ответ callback, а не измеренные сигналы физического SPI или гарантированный ресурс.

## RV32 и границы применимости

GCC 15.2.0, `rv32imc_zicsr_zifencei`/`ilp32`, `-Os -Wall -Wextra -Werror`:

| Измерение | Bytes |
|---|---:|
| Исполняемые секции core object | 1848 |
| Static data/BSS | 0 |
| Caller-owned handle на RV32 | 4352 |
| Включённый в handle sector cache | 4096 |
| Наибольший отдельный stack frame (`flush_sector`) | 304 |

Object — `ET_REL`, не самостоятельная прошивка. Unresolved libc/transport,
окончательный link, total task/IRQ stack, peak heap и timing ещё не проверены.
Размер x64 handle4368 не подменяет RV32 размер4352. Compile/ABI measurement
не выдаётся за исполнение core на RV32 или аппаратную приёмку.

При подключении libjpeg использовать один shared scratch logical file и bounded
поддиапазоны для его backing stores. Посекторное округление каждого отдельного
массива может превысить рассчитанную общую ёмкость. Несколько независимых dirty
sector caches над общим физическим сектором также недопустимы. Нужны operation/
time budgets, measured codec I/O/wear и invalidation/publication/cold-recovery gates.

Production app остаётся `3e030c1c…`/TJpgd; 6 artifact tests подтвердили неизменность
текущего firmware archive. Новый компонент не входит в factory correspondence
inventory до его production integration; собственные source hashes включены в proof.

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_nor/run.ps1 -OutputDirectory NEW_OUTPUT
python Small_TV/src/tests/jpeg_nor/mutation_contract.py --fixtures NEW_OUTPUT --output OTHER_NEW_OUTPUT
```

Proof с точными native/RV32 outputs, logs, mutations и исходным тестом:
[`jpeg-nor-core-validation-20261020.json`](../../qemu/parity/jpeg-nor-core-validation-20261020.json).
