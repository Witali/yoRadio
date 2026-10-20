# Атомарные метаданные JPEG-кеша

Checkpoint 2026-10-20: `storage/jpeg_journal.c/.h` подготовлен и проверен с
настоящим portable NOR core на host. **Не подключён к production CMake,
ESP-IDF transport, HTTP upload или libjpeg.** App3E03/TJpgd и её assets archive
остаются неизменными. Это новый `REQUESTED_CHANGE`, не перенос factory function.

## Порядок записи и восстановления

Журнал занимает два уже выделенных metadata sectors `0x1f8000` и `0x1f9000`.
Каждая запись — полный snapshot пяти cache entries, привязанный к `layout_id`,
`codec_id`, размеру RGB565 кадра и пределу JPEG source. Запас8KiB не расходуется.

1. `begin(slot)` записывает invalid snapshot в другой сектор, проверяет его и
   commit page. Последний подтверждённый сектор не изменяется. Только успешный
   return разрешает владельцу перезаписать source/frame данного slot.
2. Owner пишет кадр через NOR layer. `publish` вызывает обязательный adapter:
   flush dirty writes, затем SHA-256 **всего физического кадра**, сравнение с
   ожидаемым результатом decoder. Ошибка оставляет durable invalid state.
3. Только после успешной проверки публикуется ready snapshot в другом bank.
   Erase проверяется целиком;512-byte body программируется и проверяется до
   commit page. После commit выполняется read-back, затем меняется RAM state.
4. Cold open читает оба actual banks без старой RAM. Выбирается самая новая
   структурно valid generation. Более новый foreign layout/codec не разрешает
   вернуться к старому matching snapshot: все entries становятся invalid,
   generation сохраняется. Equal generations блокируют использование журнала;
   `UINT64_MAX` не переполняется в ноль и запрещает новый begin без I/O.

Важное второе условие: **каждый cache hit проверяет текущий физический frame hash**.
Повреждение свежего invalid snapshot может заставить boot выбрать старый ready
record, тогда как frame уже частично перезаписан. Старые метаданные сами по себе
не дают разрешения показать этот кадр. Lookup с ошибкой verification не очищает
только RAM ready flag: перед перезаписью begin всё равно обязан durably invalidate.

Source identity перед lookup должна описывать текущие persistent JPEG bytes;
её нельзя брать из устаревшего HTTP/settings snapshot. Verification callback —
доверенный non-reentrant adapter, который ещё требуется подключить. Параллельные
uploads/renderer/codec owner сериализует. Guard должен разрешить transport до
open; произвольные HTTP offsets/config не являются capabilities.

Metadata I/O или read-back failure poisons handle. Дальнейшие lookup/begin/publish
не вызывают flash до abort/reopen. Ошибка внешней frame verification оставляет
pending invalid transaction для cancel/repair; owner отдельно abort/reopen failed
NOR frame handle. Cancel/abort ничего не записывают. Повторный begin для уже
durably invalid matching entry не стирает metadata повторно. Обычный ready hit
тоже не пишет flash. Обновление ready entry требует2metadata erases; это protocol
model count, не аппаратное измерение ресурса памяти.

## Формат и границы атомарности

Wire encoding — explicit little endian, без serialization C structs/padding:

| Offset | Содержимое |
|---:|---|
| 0 | `STVJC01\0` (8bytes) |
| 8 / 12 / 16 | version1 / body size512 / generation64 |
| 24 / 56 | layout SHA-256 / codec SHA-256 |
| 88 / 92 / 96 | frame bytes / source limit / slot count5 |
| 100…111 | canonical zeros |
| 112…471 | 5entries×72: ready32, source size32, source SHA32, frame SHA32 |
| 472…507 / 508 | zeros / CRC-32 prefix0…507 |
| Последняя128/256-byte page сектора | `STVCMT1\0`, generation64, CRC32, inverted CRC32, FF padding |

Invalid entry целиком нулевой. CRC обнаруживает повреждения, это не authentication.
Commit marker программируется последним. Если прерванная program успела записать
все non-FF marker bytes, snapshot уже может быть valid, хотя callback вернул
ошибку; cold recovery допускает старое или новое **целое** состояние. В этом
случае body и кадр уже проверены, поэтому частичная frame publication невозможна.

Журнал гарантирует атомарность cache metadata при соблюдении owner protocol.
Он не восстанавливает сам JPEG source после прерванного upload и не заменяет
server privacy/format validation, transport authorization, actual source hash,
operation/time budgets или hardware power-loss acceptance. Их integration и
полный HTTP/reset workflow остаются открытыми пунктами плана.

## Проверки

MSVC C11 `/O2 /W4 /WX`, строгая4MiB NOR RAM model, реальный sparse allocation,
пять независимых nonconstant115200-byte frame fixtures, Windows BCrypt SHA:

- 4270callbacks/update при128-byte pages и2410при256-byte pages. Каждый ordinal
  проверен пятью способами: partial error, silent partial write/corrupt read,
  hard power cut после полной операции, в середине и до операции. Всего33400.
  Cold RAM discard после каждой инъекции. Ready metadata обязана давать целый
  old/new frame; все остальные четыре кадра и protected flash bytes сохранны.
- 768one-bit corruptions: каждый byte512body и256footer последнего ready bank.
  Дополнительно явный dangerous fallback: newest invalid record повреждён после
  частичной перезаписи кадра, old ready record отвергается physical SHA. Итого769.
- Все6boot reads могут частично отказать без fallback к неизвестной generation.
  State/argument/foreign-layout/codec/dimensions/source-limit cases, cancel,
  повторная invalidation без erase, verifier failures, ties и counter limit.
- 12 separately compiled mutants runtime-rejected: erase current head, skip
  invalidation, trust unverified publication/hit, ignore CRC/footer, choose oldest,
  ignore layout/codec, generation wrap, ignore read error, skip erase verification.
  Mutants используют `--quick`: state/corruption tests без полной33400матрицы.
  Compile/loader failures не считаются rejection.
- Независимый `wire_contract.py` использует Python struct/zlib/hashlib, не C
  encoder/CRC:4настоящих snapshots,128/256pages, generations7/8, все5entries,
  source/frame hashes против буквальных полных pixel fixtures.

Внутренние3.17billion assertions в stress model не являются числом независимых
сценариев или процентом покрытия. Fault model проверяет указанные сбои, не все
электрические варианты прерванного erase/program физического чипа.

GCC15.2 RV32IMC/ilp32 `-Os`: code2976bytes, const24, writable static0;
caller-owned journal handle1032 включая512-byte body. Frame NOR handle/cache
считается отдельно. Самый большой отдельный frame — open448bytes; убрана лишняя
256-byte expected footer copy (ранее704). Snapshot/verify_bytes —304 каждый;
это **не** суммарный task/IRQ/callback stack или RV32 execution. Проверен ET_REL,
не firmware link. Предыдущий source/output и новое измерение сохранены в proof.

```powershell
pwsh -NoProfile -File Small_TV/src/tests/jpeg_journal/run.ps1 -OutputDirectory NEW_FULL
python -B Small_TV/src/tests/jpeg_journal/wire_contract.py --run NEW_FULL
python -B Small_TV/src/tests/jpeg_journal/mutation_contract.py --fixtures NEW_FULL --output NEW_NEGATIVE
```

Proof с source/compiler pins и118compressed raw outputs:
[`jpeg-cache-journal-validation-20261020.json`](../../qemu/parity/jpeg-cache-journal-validation-20261020.json).
6artifact checks подтвердили unchanged production archive;6original H10 owner
identities readonly-confirmed. QEMU/SDK/snapshot/physical flash не менялись.
Далее ESP-IDF authorized transport/SHA/budgets, bounded shared scratch subfiles,
build/HTTP/source/cache workflow и libjpeg integration, затем final gates.
