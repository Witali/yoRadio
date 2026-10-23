# Настраиваемый бюджет записи JPEG

По уточнению пользователя 2026-10-23 режим JPEG сам по себе не запрещается.
Ограничен **суммарный объём program requests** одной обработки: coefficient
scratch, RGB565 frame и cache journal. Default **200 KiB =204800 bytes**.
Сохранение исходного JPEG и обычных настроек учитывается отдельно.
Это не размер scratch, не размер JPEG и не число erase cycles.

## Настройка и применение

На странице Photos добавлен отдельный numeric field. GET `/get_jpeg_write_limit`
возвращает `{"limit_kib":200}`, POST `/set_jpeg_write_limit` принимает JSON с
целым `limit_kib` от0 до4294967295. Умножение на1024 выполняется в uint64.
Нулевой лимит запрещает **program и erase** decoder/cache. Уже подготовленный
matching cache можно читать. Новая загрузка может быть отклонена ещё на
инвалидации кэша: изменять исходник до durable invalidation небезопасно.

Preference хранится отдельным NVS u32 key `small_tv/jpeg_write_kib` и не меняет
native v1/v2 blob или заводской raw-sector ABI. При отсутствии key используется
200 без записи default. Повтор того же значения не пишет NVS и не сбрасывает
тему. Настройка публикуется после успешного сохранения. Local-site server
повторяет configuration API; физический NOR traffic он не симулирует.

Нулевой лимит действует также при startup: matching complete stamp разрешает
только чтение. Для legacy storage без stamp автоматическая разметка отключена,
storage остаётся недоступным, остальные часы/HTTP запускаются. После увеличения
лимита в таком состоянии требуется обычный перезапуск для безопасной startup
проверки и adoption. Другие записи приложения (настройки, исходный JPEG) этим
специальным лимитом обработки не запрещаются.

`jpeg_transport` проверяет всю следующую запись **до** physical callback.
Issued requests учитываются и при I/O error; отвергнутая операция не учитывается
как выполненная. Один allowance общий для всех портов. Расход предварительной
cache invalidation переносится через source upload в finish: второй полный
бюджет не выдаётся. Исходные photo writes проходят отдельно от JPEG transport.
Остальные call/read/time/erase guards сохраняются.

Уменьшение лимита действует на следующей cooperative checkpoint. Уже начатую
синхронную chip operation прервать нельзя. Счётчик не сбрасывается; если расход
уже больше нового лимита, порты отзываются до вычитания, исключая underflow.
Увеличение не пополняет текущий job, но разрешает новую попытку. Zero снимает
erase permission тоже. Cleanup не flush-ит временные данные, частичный кадр не
публикуется. Background failure запоминается для длины источника и достигнутого
лимита: slideshow не тратит тот же бюджет заново на каждом круге. Больший cap
или новый source разрешает retry; transient I/O/memory/cancel по-прежнему retryable.

Причины отказа: `flash-write-limit; required=N available=M` либо
`flash-writes-disabled; required=N available=0`. `required` — следующая суммарная
потребность (нижняя оценка полного decode), не предсказание будущего трафика.
Трафик произвольного progressive заранее неизвестен: отказ может произойти
после допустимого prefix, но ни один вызов не должен превысить бюджет.

## Проверки текущего образа

App `9c1a83bd…`, ELF `76b5ce37…`, source `7d95988c…`, DEBUG off.
Binary1476432bytes, свободно59568 в app partition. Saved production artifact:
`firmware/development/small-tv-esp32c2-reconstructed/`. Library D690 unchanged;
generated codec identity обновилась вместе с policy inputs.

- Native regression6298checks +direct privacy прошла. Дополнительный compiled
  control проверяет также совпадение diagnostic program count с физическим
  счётчиком **обоих** upload/cache phases. Legacy ABI/country/credentials/photo
  settings сохранены.13inventory controls,219app/535total functions и6artifact
  checks. Inventory не доказывает full-image equivalence.
- Transport348557assertions/34cases,18compiled unsafe transport variants отвергнуты
  runtime assertions, включая live reduction/reset/erase0/underflow. Интегрированные
  6 unsafe policy mutants проверяют ignore-user-cap, erase0, потерю invalidation traffic,
  неверный cumulative diagnostic и ошибки повторных фоновых попыток.
- DOM/HTTP contract:16cases, в том числе сохранённый0, uint32 maximum, invalid/
  fractional values, read/save errors и безопасное отображение error text.
  Это не реальный browser rendering test. Crop/scale/metadata modules не менялись.
- Separate QEMU storage gate: full-CMYK12 отвергнут после ровно204800program bytes,
  следующая операция205056/204800 не вызвана. Gray progressive после него успешно
  подготовлен за115968bytes. Callback counts включают invalidation и finish;
  diagnostic total совпадает с независимой RSP trace настоящих `flash_program`.
  Считаются SDK callback requests, не raw SPI bus commands/endurance.
- После сохранения0 upload start на существующий ready slot отклонён без одного
  program/erase callback; полный paused backing до/после идентичен. Обычные
  settings API выбирают photo theme2/mask16. Cold process получает EXACT warm
  stopped flash, без NVS/settings reseed. Preference0 сохранена, настоящий
  `photo_worker_draw(slot4)` успешен. С reset до draw ни одного JPEG physical
  callback, все generated bytes прежние. Physical source/frame/journal SHA
  совпадают с independent gray RGB565 `a3ec07b0…`. Обе VM stopped/reaped.
- Дополнительный cold legacy gate начал с persisted0 и пустыми candidate/stamp.
  В первой версии F94C00B8 настоящий startup ошибочно записал40bytes stamp
  (32+8). Сохранён failing report и оба физических образа. После исправления
  тот же сценарий на9C1A83BD:0callbacks, весь4MiB unchanged, storage не принят,
  clocks/HTTP стартовали, policy0 прочитана через HTTP. VM stopped/reaped.
- Separate LCD gate текущей app: classic7/simple4/dial4 полных кадра,864000pixels,
  native и corrected literal factory RV32 exact, actual gray decode overlap и
  minute rollover,16negative report controls. Worker stack untouched prefix5012
  из8192bytes, library pool peak14099/context4984. Это observed workload, не worst
  whole-app RAM/stack. Сумма individual heap minima — conservative lower bound,
  не simultaneous aggregate minimum. Все3VM stopped/reaped.

Proof: `Small_TV/qemu/parity/jpeg-write-budget-validation-20261023.json`.
Lossless sector deltas восстанавливают15 физических4MiB images:13текущих и
2старых failing startup. Сохранены15PNG и6RAM snapshots. Offline verifier
повторно считает callbacks, проверяет zero/cold identity, physical journal/frame,
полные RGB и DWARF-derived stack/heaps. Decoder pool diagnostic сохранён как
runtime observation; его адрес отдельно не записан, поэтому независимое
восстановление pool из RAM не заявлено. Все6текущих процессов закрыты.

First cold observer ошибочно выбрал dial3 вместо photo2: decode/zero assertions
прошли, ожидание draw завершилось timeout. Полный исправленный сценарий прошёл.
Первый transport mutant runner потерял скобки при замене if; compile failure
не засчитан. Первый integrated ignore-initial-cap mutant оказался equivalent:
checkpoint снова ограничил job. Genuine bypass отключает оба чтения настройки;
исторические результаты сохранены отдельно. Нельзя считать equivalent/compile
fail варианты пойманными небезопасными реализациями.

## Воспроизведение и остаток плана

```powershell
pwsh -File Small_TV/src/tests/run.ps1 -PythonPath IDF_PYTHON -DependencyRoot IDF_ROOT
pwsh -File Small_TV/src/tests/jpeg_transport/run.ps1 -OutputDirectory NEW_TRANSPORT
python -B Small_TV/src/tests/jpeg_transport/mutation_contract.py --fixtures NEW_TRANSPORT --output NEW_TRANSPORT_MUTANTS
python -B Small_TV/src/tests/photo_write_budget_mutation.py --output NEW_POLICY_MUTANTS
node Small_TV/src/tests/jpeg_write_policy_dom_test.js
pwsh -File Small_TV/src/build.ps1 -DependencyRoot IDF_ROOT
python -B Small_TV/src/tests/photo_write_budget_qemu.py --qemu-root FROZEN --output NEW_QEMU
python -B Small_TV/src/tests/photo_zero_boot_qemu.py --qemu-root FROZEN --seed ZERO_STOPPED_FLASH --output NEW_ZERO_BOOT
python -B Small_TV/src/tests/jpeg_clock_qemu.py --qemu-root FROZEN --output NEW_LCD
python -B Small_TV/src/tests/verify_photo_write_budget_evidence.py --proof Small_TV/qemu/parity/jpeg-write-budget-validation-20261023.json
```

Исходный план остаётся активным: полный current target format/RAM/stack/fault
matrix с новыми refusals, real publication/program/erase interruptions, clients/
reconnect/churn, whole-image audit/full/24h/hardware. Network и LCD acceptance
разделены; HTTP тут запускает storage work. Shared SDK/frozen QEMU неизменны,
физических действий, OTA и push нет. Старые unlimited heavy JPEG acceptance
результаты не являются default-policy acceptance нового образа.
