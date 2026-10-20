# Защита областей JPEG flash

Checkpoint 2026-10-20: `storage/jpeg_guard.c/.h` и
`tools/jpeg_guard_layout.py` подготовлены и проверены отдельно. Они **ещё не
подключены к production CMake, ESP-IDF transport или работающему decoder**.
App3E03/TJpgd и её исходный assets archive не изменены. Это новый
`REQUESTED_CHANGE` для расширения JPEG, без заявления factory equivalence.

## Что разрешает guard

Перед выдачей writable capabilities transport должен получить `JPEG_GUARD_OK`:

- Размер устройства точно совпадает с compiled layout. Все boot partitions
  совпадают по label/type/subtype/offset/size/flags, включая количество и порядок.
  ESP-IDF adapter обязан перечислить **всю** таблицу, затем сортировать её.
- Sorted sector-aligned allowed/protected ranges покрывают всю flash без дыр
  и пересечений. Boot/application, остальные partitions, все photo slots,
  immutable payloads и settings остаются защищены. Согласованная переклассификация
  первого boot/photo/settings сектора тоже отвергается.
- SHA-256 каждого из 27 animation/icon payloads и ownership stamp совпадает.
  Чтение — chunks≤256bytes. User photos, scratch/cache, настройки и неиспользуемое
  padding не входят в payload hashes. Повторная проверка после их изменения
  остаётся успешной; whole-assets hash не используется как runtime criterion.
- Частичное чтение, ошибка hash begin/update/finish или несовпадение ресурса
  не дают разрешения. Hash state освобождается после каждого begin attempt,
  включая частичную ошибку. Проверка ничего не программирует и не стирает.

Core использует streaming SHA provider, а не новую реализацию криптографии.
Host тестирует через Windows BCrypt с известным SHA-256 `abc` и независимыми
hashes asset manifest; для ESP-IDF ещё требуется adapter существующего mbedTLS.
Owner сериализует проверку/изменение ресурсов, хранит authorization только для
успешно проверенной boot session и закрывает handles перед заменой образа.
Readonly guard сам не ограничивает прямые вызовы `jpeg_nor_open`: эту границу
должен обеспечить ещё не реализованный production transport.

## Зачем нужен stamp

Известные payload hashes сами по себе не описывают владение бывшими свободными
хвостами. Поэтому сборочный инструмент формирует SHA-256 canonical authority:
вся partition map, immutable offsets/sizes/hashes, candidate/protected extents,
scratch/metadata/пять cache mappings и spare extents, место stamp. User photo
hashes и self-referential whole-image/layout hashes в authority не входят.

64-byte stamp: `STVOWN1\0`, 32bytes ownership ID, 24bytes FF. Сейчас он находится
по `0x28f720` в уже защищённом последнем erase sector первой анимации, после её
payload. Это не расходует 2 spare sectors: остаётся262available/260allocated.
Stamp сам включён отдельным resource hash в generated descriptors; после его
добавления пересчитываются assets manifest и cache `layout_id`.

Инструмент принимает только validated sanitized build assets с FF candidate
tails. Он пишет **новую копию** assets/manifest/header/plan в новую директорию;
исходные файлы не меняет. Занятое или чужое stamp padding не перезаписывает.
Прежний корректный stamp допускается идемпотентно. Только64bytes protected
padding отличаются; все исходные resource/photo payloads побайтно сохранены.
Согласованное изменение allocation с прежними27payloads меняет ownership ID.

Все будущие builds с новым backend должны формировать stamp и descriptors
вместе. Legacy/unmarked assets и app-only update с чужим stamp не разрешают
запись. Нельзя автоматически «исправить» stamp на неизвестной flash: это
означало бы присвоить владение без доказательства. Future deployment должен
сохранить user photos/settings; подготовленный полный assets.bin не является
разрешением стереть их при обновлении. Build integration ещё впереди.

Это защита от несовместимой native разметки/ресурсов, не authenticated firmware
или проверка произвольного враждебного image. Stamp требует доверенного build
pipeline. Данные runtime cache ожидаемо отличаются от исходных FF bytes.

## Проверки и измерения

MSVC C11 `/W4 /WX`, реальный sanitized image и строгий readonly transport:

- 84 first/middle/last corruptions всех28hashed ranges отвергаются; после
  восстановления данных повторная проверка успешна. Unmarked image проверен
  отдельно. Все не-immutable bytes разрешено изменить без ложного запрета.
- 49 invalid layout cases до любого I/O; 3050read faults (каждый2954callback
  ordinal с partial error и96silent corrupt reads);3010hash faults (каждый
  begin/update/finish ordinal). Cleanup проверяется на каждом результате.
- 12invalid generator inputs и12controls: полная карта, каждый immutable hash,
  photo exclusion, stamp-only padding, idempotence, new-layout/same-payload ID,
  сохранность inputs и отказ перезаписать существующий output.
- 10 отдельно скомпилированных mutants отвергнуты runtime assertions: обход
  partition/digest/stamp verification, игнорирование read/hash errors, утечка
  hash state и разрешение boot/photo/settings sectors. Compile/loader errors
  не засчитываются как rejection.

Первый generator test неверно требовал уникальности всех icon hashes. Некоторые
разные slots содержат одинаковые payloads; `FIXED_TEST` теперь сравнивает
кратность. Старый test source и failed log сохранены. Ошибки guard этим не было.
Число внутренних assertions не является числом независимых сценариев или
процентом покрытия.

RV32IMC/ilp32 GCC15.2 `-Os`: core1150code bytes, writable static0;
generated const descriptors1448bytes (layout72, partitions128, ranges128,
resources1120). Frames: verify_resource320 и jpeg_guard_verify96bytes.
Provider/transport/call-chain/IRQ/task stack сюда не входят. Проверяется
ET_REL object, **не RV32 execution и не полный firmware link**.
Один успешный guard читает752121bytes за2954calls; boot time ещё не измерен.

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_guard/run.ps1 -OutputDirectory NEW_HOST
python -B Small_TV/src/tests/jpeg_guard/generator_contract.py --assets-dir firmware/development/small-tv-esp32c2-reconstructed --output NEW_GENERATOR
python -B Small_TV/src/tests/jpeg_guard/mutation_contract.py --fixtures NEW_HOST --assets NEW_HOST/assets.bin --output NEW_NEGATIVE
```

Proof с точными sources/compiler pins и85compressed raw outputs:
[`jpeg-ownership-guard-validation-20261020.json`](../../qemu/parity/jpeg-ownership-guard-validation-20261020.json).
6artifact checks подтверждают неизменность app3E03 и archive. Six original
H10 owner identities подтверждены readonly CIM; его QMP/RSP, SDK и snapshots
не менялись. Portable [atomic cache journal](JPEG_CACHE_JOURNAL.md) теперь также
подготовлен отдельно; actual upload/source workflow, hardware faults, transport
authorization/budgets, build/codec integration и final acceptance остаются
обязательными следующими этапами.
