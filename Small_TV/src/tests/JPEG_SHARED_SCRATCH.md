# Общее временное хранилище JPEG

Следующий checkpoint сохраняет этот storage contract, меняя representation
временных коэффициентов для сокращения flash-записей. Ниже сохранены исходные
raw-backing измерения; новые A/B результаты и tradeoffs — [JPEG_COEFFICIENTS](JPEG_COEFFICIENTS.md).

Checkpoint 2026-10-20. `storage/jpeg_scratch.c/.h` и настоящий libjpeg проверены
совместно на host с NOR core. Это **не включение libjpeg в рабочую UI прошивку**:
app `3e030c1c…` по-прежнему использует TJpgd. Предыдущая standalone target probe
`6cb29771…` проверяет transport/ESP-IDF, но новый scratch/codec там не исполнялись.

## Контракт и разделение модулей

Один открытый `jpeg_nor_t` с одним 4 KiB кэшем обслуживает до 16 файлов.
First-fit allocator выделяет точное число байтов без округления каждого файла
до сектора. Четыре массива по 115200 байт занимают ровно 460800 байт; соседние
файлы делят физический сектор и видят согласованные данные общего кэша.
Объекты принадлежат вызывающему коду, heap и writable globals в модуле отсутствуют.

Pinned upstream `c85e6b905bf237038faa936dab160ebfc5da0344`, `src/jmemmgr.c`,
хранит `first_undef_row` и запрещает writable gaps. Scratch отслеживает непрерывный
инициализированный префикс: сначала последовательная запись, затем произвольное
чтение/перезапись этого префикса. Прочитать старые временные данные предыдущего
файла или перескочить незаписанную область нельзя. Нулевая запись в конце файла
не инициализирует промежуток. Префикс растёт только после успешной полной записи.
Это контракт виртуальных массивов libjpeg, не полноценная файловая система.

File token передаётся по значению: owner, slot и монотонный 64-bit ID. Закрытый
token не оживает после повторного выделения slot или abort/reopen. Переполнение
ID отклоняется; owner нельзя обнулять/пересоздавать, пока существуют старые tokens.
Вызовы сериализуются владельцем. Mandatory checkpoint выполняется и для операций,
которые обслуживаются из RAM, чтобы истечение общего бюджета останавливало decode.
При I/O error весь job перестаёт работать; close/abort остаются доступны без I/O.
Abort отбрасывает dirty temp RAM, не записывая ненужные временные данные на flash.

Общий hard-capped pool allocator стенда остался в `probe_memory.c`; прежний
bounded stdio backend вынесен в `probe_backing_stdio.c`, новый NOR bridge —
`jpeg_scratch/probe_backing_nor.c`. Эталонный декодер использует stdio, кандидат —
настоящие scratch/NOR C-модули. Строгая host-модель независимо проверяет физические
адреса, page boundaries, 1→0 program и 4 KiB erase, сохраняет partial writes и
все physical bytes между циклами reuse. Её два массива по 4 MiB — только host
oracle и canaries; они не входят в память firmware.

## Выполненные проверки

- Native: 16432 assertions, 5000 random operations при page128/256, 134 partial
  error/silent-fault cases, byte fragmentation, shared-sector coherence, границы,
  unwritten prefix, stale tokens, cancel при RAM hit, cleanup и ID exhaustion.
- 13 скомпилированных unsafe mutants отвергнуты runtime assertions. Ошибка
  компиляции/загрузки или crash не принимается за успешный negative control.
- Actual libjpeg/NOR: 25 resource cases, 924 lossless cases, 16 invalid inputs,
  4 optional-mode controls, 18 budget cases; 48 non-flat 12-bit images и
  12 truncated inputs. Все 38912 entries flash tables совпали с upstream.
- Pillow независимо подтвердил все pixels 18 baseline/progressive JPEG.
- 1227 logical I/O/allocation fault recoveries, 36 truncated recoveries и
  12 format transitions прошли с новым NOR backend. Общий старый runner всё ещё
  описывает свою область как logical hooks; physical gate выполнен отдельно.
- 2238 partial physical I/O errors: каждый из 2010 callbacks трёх малых fixtures,
  по 57 выбранных callbacks четырёх 240×240 fixtures. После ошибки тот же JPEG
  object, permanent pools и реально изменённая NOR использованы для recovery;
  все recovery pixels точные, stores закрыты, final pool zero. Не утверждается
  exhaustive coverage десятков тысяч callbacks каждого полного изображения.

Physical codec gate возвращает ошибку после реального partial read/program/erase.
Silent write/erase readback проверяет отдельный NOR contract. Обнаружение любой
silent corruption чтения временных коэффициентов не обещается: scratch не имеет
полного checksum каждого читаемого блока. Это не гарантия против произвольного
аппаратного bit rot и не hardware power-loss acceptance.

RV32IMC/ILP32 `-Os`: module code1240 bytes, writable/readonly static0,
scratch handle576, token24, region32, largest individual frame48 bytes. Это
relocatable object measurement, не target execution, full call-chain stack,
whole-app peak heap или окончательный link.

## Измеренный трафик

Первый decode детерминированных **non-flat** 240×240 fixtures, один sector cache,
page256, flash в начале содержит non-FF данные. Повторный cycle сохраняет flash;
его трафик также есть в raw report, но в таблице приведён только первый.

| Режим | Scratch bytes | Physical read bytes | Physical program bytes | Erase callbacks |
|---|---:|---:|---:|---:|
| progressive 4:2:0 12-bit | 172800 | 5843712 | 1274624 | 311 |
| progressive YCCK 12-bit | 288000 | 10369920 | 2256896 | 551 |
| progressive CMYK 8-bit | 460800 | 16002560 | 3478784 | 848 |
| progressive CMYK 12-bit | 460800 | 16850432 | 3780608 | 923 |

Сумма erase callbacks не равна износу каждого сектора и не задаёт endurance
устройства. Host duration не является скоростью SPI/decode на ESP32-C2.
Эти данные показывают, почему capacity нельзя принимать за write traffic и
почему готовый RGB565 cache должен переживать повторные показы фотографии.
Значения не используются как универсальные production budgets.

По уточнению пользователя объективно невозможный вход должен получать точную
причину отказа. Следующий native codec contract должен различать неподдерживаемый
режим, повреждённый JPEG, нехватку RAM/scratch и I/O error. Resource refusal должен
показывать required/available и, где возможно, происходить до backing writes.
Это открытая интеграционная работа; raw `JERR_NO_BACKING_STORE` host-пробы не
считать уже готовым сообщением WebUI и не подменять им «повреждённый файл».

## Воспроизведение и оставшиеся работы

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_scratch/run.ps1 -OutputDirectory NEW_FIXTURES
pwsh -NoProfile -File Small_TV/src/tests/jpeg_scratch/build-host.ps1 -OutputDirectory NEW_REFERENCE
pwsh -NoProfile -File Small_TV/src/tests/jpeg_scratch/build-host.ps1 -Nor -Fixtures NEW_FIXTURES -OutputDirectory NEW_NOR
python -B Small_TV/src/tests/jpeg_library_probe/qualify.py --reference-build NEW_REFERENCE --candidate-build NEW_NOR --output NEW_MATRIX
python -B Small_TV/src/tests/jpeg_library_probe/flash_tables_contract.py --reference-build NEW_REFERENCE --candidate-build NEW_NOR --output NEW_TABLES
python -B Small_TV/src/tests/jpeg_library_probe/independent.py --reference-build NEW_REFERENCE --candidate-build NEW_NOR --output NEW_PILLOW
python -B Small_TV/src/tests/jpeg_library_probe/fault_contract.py --reference-build NEW_REFERENCE --candidate-build NEW_NOR --output NEW_LOGICAL_FAULTS
python -B Small_TV/src/tests/jpeg_scratch/physical_fault_contract.py --reference-build NEW_REFERENCE --candidate-build NEW_NOR --output NEW_PHYSICAL_FAULTS
python -B Small_TV/src/tests/jpeg_scratch/mutation_contract.py --fixtures NEW_FIXTURES --output NEW_MUTANTS
python -B Small_TV/src/tests/jpeg_scratch/rv32_footprint.py --toolchain-bin PINNED_TOOLCHAIN_BIN --output NEW_RV32
```

Для independent нужен Python с Pillow; SDK environment его не содержит.
Использован готовый bundled runtime без установки/изменения пакетов в SDK.
Все outputs — новые папки. Build pins сняты до compilation и проверены после;
native runner также фиксирует inputs/products. Первая native ошибка была
ошибкой порядка тестов (ID exhaustion до следующих allocations), первая NOR
build — отсутствующим CMake include каталога общих hooks. Неудачные попытки,
исправления и финальные результаты сохранены, не выдаются за успешные прогоны.

Proof: [jpeg-scratch-validation-20261020.json](../../qemu/parity/jpeg-scratch-validation-20261020.json).
6 artifact и 10 correspondence controls прошли; main app и SDK не менялись.
Старые шесть H10 owners проверены только чтением, новый debugger не подключался.

Открыты расширенная sampling matrix и вместимость редких легальных вариантов:
460800 — максимум текущих fixtures. Проверить округление coefficient arrays
для высоких sampling factors, не исключать требуемые варианты ради этого лимита.
Далее — source/upload invalidation и physical source/frame hashes, journal/cache
workflow, matching assets deployment с сохранением photos/settings, native bounded
codec bridge, полный target link/heap/task stack/time, HTTP/reset/LCD/full/24h и
hardware gates. Вся цель [IMPROVEMENT_PLAN](../IMPROVEMENT_PLAN.md) остаётся открытой.
