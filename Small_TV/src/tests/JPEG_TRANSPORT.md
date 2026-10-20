# ESP-IDF transport и общие бюджеты JPEG

Checkpoint 2026-10-20: `storage/jpeg_transport.c/.h` и `jpeg_espidf.c/.h`
реализованы. Настоящие ESP-IDF flash/partition/PSA API собраны и исполнены в
отдельной ESP32-C2 test probe под QEMU. **Основная Small TV app3E03/TJpgd не
изменена; libjpeg и actual upload/cache workflow ещё не подключены.**

## Разрешение I/O

Generic transport получает readonly guard result до выдачи ports. Каждый новый
authorization attempt сначала отзывает прежний доступ; failed verification не
оставляет старое разрешение. Только полный matching map/resources/stamp даёт
право начать job. Guard отдельно ограничен по read/call/time budget.

Job использует **один** calls/read bytes/program bytes/erase count/time budget
для всех scratch/cache/journal/input ports. Создание другого port не обнуляет
счётчики. Проверка полного запроса выполняется до I/O; rejected request не
считается issued. Callback failure считается с полным requested byte count,
даже если физически выполнилась лишь часть. После I/O error/deadline/quota
останавливаются все ports job; при новом begin epoch меняется. Старую NOR/journal
RAM owner обязан abort/reopen из actual flash, без retry stale cached state.

Writable port — sorted copied full-sector ranges внутри verified capabilities.
Readonly input разрешён в bounded assets payloads или owned scratch ranges,
но не в boot/NVS/settings. Whole-request bounds, gaps/overflow, page/sector
alignment, readonly flag и buffers, пересекающие capability state, проверяются
до вызова driver. Data addresses не должны поступать произвольно из HTTP.

Device context заимствует port object. Все borrowers нужно отбросить до reuse
этой памяти; use-after-reuse C object не является безопасным token API. Epoch
защищает живые ports прежнего job, а не уничтоженные/recycled C objects.
RAM-only cache operations/codec rows требуют `jpeg_transport_check` и owner abort
protocol: callback revocation сама по себе не может остановить CPU или вернуть
управление из уже выполняющегося synchronous flash call. Deadline проверяется
до/после callback; операция, превысившая срок, может быть уже завершена в flash.
Новый I/O не выдаётся, а metadata/data восстанавливаются по реальным bytes.

## Binding закреплённой ESP-IDF

Использован SDK9a97f6c54ec638111ce55cd36581b3c192f15207, mbedTLS submodule
ce3f3485a121c100f58f36d700cb35b060f6e866; SDK tracked tree clean.
Контракты взяты из exact local headers/implementation:

- `esp_flash_get_physical_size` проверяет физическую ёмкость отдельно от
  image-configured `esp_flash_get_size`; обе должны совпасть с4MiB layout.
- Читается raw3KiB partition table, проверяется SDK verifier/MD5 и canonical FF
  tail. Полные32-bit flags сохраняются, включая неизвестные SDK bits.
  ALL SDK partitions cross-check по label/type/subtype/address/size, chip,
  known flags и4KiB erase size; пропущенные/лишние entries не игнорируются.
  Временные3KiB heap освобождаются до создания codec caches.
- Discovery read/call и elapsed time вычитаются из startup budget. Init/platform
  crypto initialization не являются частью последующего per-decode budget.
- Guard SHA-256 использует public `psa_hash_setup/update/finish/abort`; старый
  private `mbedtls_sha256` API не импортируется. Cleanup после каждого ресурса.
- Runtime read/program/erase проходят через `esp_flash_*` только после port
  checks.256-byte logical page — transport unit, SDK сам делит её согласно
  selected chip driver. Callback counts не выдаются за сигналы bus или endurance.
  Microsecond deadline использует monotonic `esp_timer_get_time`, без delays.

Это build/layout mismatch guard, не authenticated firmware. Обычный ESP-IDF
partition iterator теряет unknown flag bits; raw+SDK cross-check здесь необходим.
Primary SDK file hashes, compile commands и executed ELF включены в proof.

## Проверки

Host MSVC C11 `/O2 /W4 /WX`:31cases с real resource SHA через BCrypt,
independent physical counters и детерминированным clock. Shared quota across
stores, создание port после уже выполненного I/O, readonly write **внутри**
его scope, pre/post deadlines, final SHA deadline, rollback/large timestamps,
read/program/erase errors, failed reauthorization, stale epochs, ranges/null/
alias/wrap/page checks.14compiled mutants runtime-rejected; compile/loader
failures не считаются успехом negative control. Assertion count не coverage.

Target probe — `tests/jpeg_transport/idf_probe`, real SDK, без network/LCD
criterion и guest RAM/PC patches. Four variants/five owned processes:

1. Matching stamped image: cross-sector writes и настоящая0→1 sector RMW,
   independent full4MiB before/after comparison. Изменились ровно35ожидаемых bytes;
   все остальные media/photos/settings/application bytes сохранились.
2. Процесс завершён с disk flush, затем свежий QEMU process открыл тот же drive.
   Cold persistence verified:0program bytes/0erases. RAM/flash cache старого
   emulator не принимается за cold evidence.
3. Legacy unmarked image, MD5-valid raw unknown flags и MD5-valid extra partition
   внутри planned scratch — каждый вариант отвергнут. Все4MiB bytes неизменны.

Matching update:157issued callbacks,53314read bytes,1024program bytes,1erase;
cold read:6callbacks/80bytes,0writes. Это конкретный synthetic storage workflow,
**не** wear/time measurement обычного JPEG или проверка всех форматов.
Все5процессов завершены по своим name/QMP/process handles. Frozen QEMU files
не менялись. First failed CMake path и два pre-launch harness mistakes сохранены;
они не объявляются firmware failures. Windows paths нормализованы, launcher
получает правильные offline/reconstructed arguments, baseline снимается paused.

Firmware probe сохранена в `firmware/development/small-tv-storage-probe/`.
Сборка фиксирует19source/generated hashes **до** compilation, проверяет
неизменность перед archive, пишет deterministic ordered source fingerprint.
Это standalone storage test image, не UI firmware с новым JPEG. Её135504bytes
не доказывают размер/heap/stack будущей полной Small TV с libjpeg.

Точные RV32 flags replay в отдельные objects: transport2324code/maxframe240,
ESP-IDF binding1448code/maxframe416; writable static0. Executed probe globals:
platform context536, каждый port152, каждый NOR/cache handle4352bytes.
Это не total heap/task/IRQ/callback stack; measurement ELF отдельно от production.

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_transport/run.ps1 -OutputDirectory NEW_HOST
python -B Small_TV/src/tests/jpeg_transport/mutation_contract.py --fixtures NEW_HOST --output NEW_NEGATIVE
pwsh -NoProfile -File Small_TV/src/tests/jpeg_transport/build-idf.ps1 -BuildDirectory NEW_IDF_BUILD
python -B Small_TV/src/tests/jpeg_transport/qemu_probe.py --qemu-root FROZEN_QEMU --output NEW_VM_OUTPUT
```

Proof: [`jpeg-transport-validation-20261020.json`](../../qemu/parity/jpeg-transport-validation-20261020.json).
Далее byte-bounded subfiles одного shared NOR scratch (без sector rounding
каждого массива), real libjpeg bridge/matrix и выбор production budgets по
actual decode traffic. Значения probe/host fixtures нельзя копировать как
предел для всех обычных JPEG. Upload invalidation/source identity, matching
assets deployment с сохранением photos/settings и final UI/network/full/24h/
hardware acceptance также остаются открытыми.
