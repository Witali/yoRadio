# Пять коротких вызовов: panic, new[] и очистка исключений

Checkpoint 2026-10-26 продолжает [RV32 disassembly](RV32_DISASSEMBLY.md).
Назначение пяти выбранных вызовов установлено по полным телам, relocations и
связанным targets. Найден общий factory/native отказ при нехватке памяти.
**Исправление этого отказа открыто.**

Позднее26Oct исправлен native nothrow path и проверена новая production app:
[NOTHROW_ALLOCATION.md](NOTHROW_ALLOCATION.md). Исторические failing-before
результаты ниже сохранены, а полнота всего образа остаётся открытой.

Следующий scoped checkpoint восстановил границы десяти тел и все пять
пропущенных ссылок в transient read-only Ghidra:
[RUNTIME_METADATA.md](RUNTIME_METADATA.md). Все453C.JAL теперь имеют точные
ссылки и target functions; это не доказательство достижимости всего образа.

| Заводской PC | Владелец / вызываемая функция |
|---|---|
| `0x40380180` | `_panic_handler` → `xt_unhandled_exception` |
| `0x4038018e` | `_panic_handler` → `panicHandler` |
| `0x420a3a12` | `operator new[](size_t, const std::nothrow_t&)` → `__cxa_begin_catch` |
| `0x420a3a14` | Тот же landing pad → `__cxa_end_catch` |
| `0x420a3e32` | `eh_globals_dtor(void*)` → `_Unwind_DeleteException` |

## Полные тела и границы

Factory ELF `8c9fd166…` и native ELF `9e4ec88d…` сохранены без изменений.
Проверены 10 factory тел / 508 linked bytes и 9 native / 496 bytes: panic
vector, scalar new, array-new veneer, nothrow array new, TLS cleanup, end-catch
и abort-only exception stubs. В native не связан `_Unwind_Resume`; отсутствие
проверено по таблице символов, это не пропавшая функция приложения.

Использованы семь точных ELF objects текущих SDK/build и GCC 15.2.0 runtime.
Сопоставление разрешает только заявленные relocations/RELAX, проверяет локальные
переходы и callee bindings. Оно не устанавливает версию factory compiler и
не приравнивает весь старый SDK к новому. Целый compiler archive не сохранён.

Scalar и array nothrow bodies похожи. Здесь `_ZnajRKSt9nothrow_t` вызывает
`_Znaj`, а его 2-byte veneer переходит в `_Znwj`. Цепочка проверена по native
symbols и полным телам. Маленькое совпавшее тело без bindings не определяет имя.

Ghidra учитывала 14 из 20 bytes nothrow body без landing pad; destructor 48 B
не имел entry, target `0x420a3fd4` попал внутрь чужого body. Ranges теперь
квалифицированы, но persistent project не менялся. Transient metadata recovery
и остальной whole-image scope остаются открытыми.

## Подтверждённый дефект NTH-ALLOC-FAIL

При `malloc == NULL` и отсутствии `new_handler` обе версии проходят:

`new[](nothrow)` → `new[]` → `new` → `__cxa_allocate_exception` stub → `abort`.

Landing pad при этом не достигается. Его отдельный искусственный запуск
возвращает ноль после begin/end-catch, но не доказывает настоящую EH delivery.
Factory caller `0x42040efc` запрашивает 512 B и проверяет NULL в `0x42040f02`
с переходом в `0x42040f80`. Bytes аргумента, call и null branch проверены.
Однако OOM runtime вызывает abort до возврата. Имя/полный body caller ещё
требуют SDK matching; похожий NVS source не идентифицирует его сам по себе.

Native nothrow array new находится в `0x420a413e`; исполнение показывает тот же
abort. Следующий шаг: безопасный возврат `nullptr` для nothrow allocation,
zero-size/new-handler/ownership, fail-before/pass-after tests, новая production
app и реальная NVS/network проверка. Shared SDK и frozen builds не патчить.
Throwing new, panic и полную поддержку исключений это автоматически не исправит.

## Проверки

176 literal RV32 cases проверяют **наблюдаемое поведение**:

- 132 panic cases: сохранённые GPR/CSR, 32 причины, interrupt bit, маскирование,
  выбор callback, восстановление stack/registers и реальный `mret`. Callback
  возвращается искусственно; восстановление SDK после panic не заявлено.
- New: успех/OOM для 0, 1, 512 и `UINT32_MAX`, retry после new-handler.
  Настоящие exception stubs исполняются до abort.
- TLS cleanup: null, пустое состояние, один/два узла. Первый непустой узел
  достигает настоящего DeleteException→abort; второй узел/free не выдумываются.
- Nothrow array new: успех, OOM и явный вход landing pad в обоих ELF.

`desired_nothrow_oom_contract_passed=false` сохраняет failing before. Pass
отчёта означает воспроизведённый алгоритм, а не исправленный дефект.
Begin-catch — внешняя граница; end-catch сопоставлен целиком, но все его ветки
ещё не исполнены. Не доказаны natural exception reachability и hardware acceptance.

13 реальных input mutations отвергаются: frame, branch, call targets,
array/scalar identity, source object и RELAX. Consumer отвергает ещё семь
изменений отчёта, включая выдуманный OOM fix, compiler identity и physical pass.

## Воспроизведение

[Proof](../../qemu/parity/runtime-call-gaps-validation-20261026.json):
10 gzip payloads / 62 267 B / 12 source pins. Семь objects позволяют заново
разобрать ELF symbols/relocations без установленного compiler runtime.
Factory/native ELF, DROM, user data, RAM ВМ и UART не добавлены.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_runtime_call_evidence.py `
  --proof Small_TV/qemu/parity/runtime-call-gaps-validation-20261026.json `
  --factory C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --native C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2/small_tv_reconstructed.elf
```

SDK qualification, literal CPU fixtures и rejection controls разделены по модулям.
Не запускались QEMU, serial/reset или физическая прошивка. Полнота образа,
произвольные aliases/EH metadata и финальные acceptance gates остаются открытыми.
