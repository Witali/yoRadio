# NTH-ALLOC-FAIL: исправление отказа выделения памяти

26 октября 2026. Продолжение [runtime audit](RUNTIME_CALL_GAPS.md), в рамках
приоритетного factory/whole-image пункта. Исправлен подтверждённый SDK path,
где `new[](std::nothrow)` при mallocNULL/no-handler вызывал abort.

## Изменение

Новый `app/platform/nothrow_new.cpp` содержит общий allocation helper и две
GNU linker wrappers для обычных scalar/array nothrow overloads. Ошибка теперь
возвращает `nullptr`; исходная throwing allocation function не вызывается.
Нулевой размер преобразуется в1, provider остаётся malloc, освобождение — через
существующие delete/free. Сохраняются повторная попытка после new-handler,
замена/удаление handler и его намеренное nonreturning поведение. Задержек,
логирования, дополнительных Flash-записей или новых HTTP endpoints нет.

Nothrow формы должны возвращать указатель или null; описание поведения см.
в [проекте стандарта C++, single-object forms](https://eel.is/c++draft/new.delete.single)
и [array forms](https://eel.is/c++draft/new.delete.array). Реализация рассчитана
на проверенный ESP32-C2/RV32/ESP-IDF6.1 profile без C++ exceptions и без heap-abort
при malloc failure. Изменение этих условий останавливает сборку до review.
Over-aligned allocation и полная поддержка C++ exceptions не добавлялись.

Это исправление отмечено `FIXED_FACTORY`. Shared SDK, GCC runtime и frozen
старые builds не менялись. `--wrap` и `--undefined` удерживают обе wrappers
в app archive. Проверка после линковки сопоставляет полные helper/wrapper bodies,
включая file-local call targets, и весь NVS `Page::load` с его source object.
Его array allocation должен разрешаться именно в wrapper. Оставшийся unwrapped
или aligned nothrow symbol отклоняет build. Обычный throwing new не заменяется.

CPP source и checker входят в production source manifest. Двусторонняя карта
учитывает три новые функции, simple C-linkage/noexcept definitions и прежний
Wi-Fi timer guard, чья support row раньше отсутствовала. Это инвентаризация,
не доказательство всего C++ runtime или всего заводского образа.

## До и после

Frozen native ELF9E4E / appC912: реальные `NVS Page::load` инструкции получают
erased-page header, запрашивают512B и при mallocNULL/no-handler доходят до abort.
Этот failing-before сохранён без изменения старого кода.

Новая app4F2C / ELFEB20: тот же NVS path исполняет исправленную wrapper и
возвращает `ESP_ERR_NO_MEM (0x101)`. Проверены также успешное чтение восьми512B
блоков с единственным free, ошибка partition read и null partition.
Partition I/O, malloc, handler и ROM memset — явные private-CPU boundaries;
NVS и wrapper instructions настоящие. Это не fault injection всей работающей ВМ.

У `get_new_handler` также проверен cold-runtime контекст: linked constructor
`_GLOBAL__sub_I__ZSt7nothrow` есть в `.flash.init_array` и вызывает
`pthread_mutex_init` для его mutex до app_main. SDK lock при уже инициализированном
mutex не проходит lazy allocation. Внутренности pthread/FreeRTOS в CPU fixture
не исполняются; восстановление после повреждения или неуспешной глобальной
инициализации mutex не заявлено.

Верхний `app_main` по-прежнему использует `ESP_ERROR_CHECK(nvs_flash_init())`.
Исправление даёт корректную ошибку NVS, но не обещает загрузку устройства при
неустранимой нехватке памяти на этапе инициализации. Другие startup/error paths
и поведение при массовом исчерпании ресурсов остаются отдельными проверками.

## Проверено

- 26 host cases компилируют production CPP с заменой только двух boundary calls.
  Проверены размеры0/1/512/UINT32_MAX/hostSIZE_MAX, успех, OOM и handler changes.
  Они включены в штатный `tests/run.ps1`, а не только в отдельный optional запуск.
- 26 cases исполняют настоящий compiled RV32 helper/wrappers и NVS: null return,
  retry, removing/nonreturning handler и четыре NVS outcomes. ABI registers/stack
  и ownership проверяются отдельно. Исторический before заново исполняется.
- 13 altered-input controls отвергают обход wrapper в NVS, неверный local helper,
  malloc target, старую сборку, app mismatch и ложную network readiness.
- 6300 native checks и3727 независимых JPEG privacy assertions;16 correspondence
  tests;6 artifact/ESP checksum/partition/source/HTTP inventory checks прошли.
- Отдельный QEMU network gate без LCD: настройка через HTTP/scan, NVS/raw settings
  persistence, software reboot, persistent cold boot, reset, HTTP и SNTP. Три
  фазы проверяют реальное SDK время и station state. Weather выдаёт loopback503;
  успешная работа Internet weather этим тестом не подтверждается.
- Отдельный LCD gate: один cold start factory и native, точные57600pixels
  setup frame в каждом. Network readiness не используется для LCD.

Первый network prototype ожидал старую подсеть10.0.2.15 через frozen helper.
Фактически QEMU/SDK выдали192.168.43.15. Новый scoped predicate берёт address из
конфигурации текущей VM; frozen47helperfiles и QEMU не патчились. Неуспешный
prototype сохранён в ignored build; он не считается успешной приёмкой.

Final networkexec93791 и displayexec3351 завершились0. Network owners34392/21584
имеют kernel creation identities и exit0; display owners21168/35764 также
отсутствуют по CIM12:24:26UTC. Все тестовые ВМ закрыты. Board/serial/reset не было.

## Сборка и evidence

Production DEBUGoff сохранён в `firmware/development/small-tv-esp32c2-reconstructed/`:

| Artifact | Значение |
|---|---|
| app SHA | `4f2cfd9837fff0143098eb32f3a2ec6f59170d23902f17f2b2e9fff857165195` |
| ELF SHA | `eb20fb1309d1a5f28229d2ca846924cd18b311da229d34a1319a324d621ee2e6` |
| Source aggregate | `5b6252cec1006fc3b4e5a6fc2dc2f72ca4a396a2a8c6bac521f45be0bf07d161` |
| Размер app | 1475840B; на640B меньше старойC912,60160B свободно в app partition |
| Code wrappers+helper | 58 linked bytes |

Новый JPEG library report/cache identity подготовлен штатным offline build;
его CODEC-REPRO item остаётся отложенным. Здесь не объявлена новая полная JPEG,
RAM/stack, RF, 24h или аппаратная приёмка.

[Proof](../../qemu/parity/nothrow-fix-validation-20261026.json) содержит14gzip /
124100B и30 source pins. Consumer заново сопоставляет current ELF/object/NVS,
исполняет before/after, recomputes SDK-clock arithmetic и все сохранённые LCD
pixels. Пять дополнительных runtime mutations отвергаются. В evidence нет
полного SDK archive, VM flash, пользовательских RAM или UART dumps.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
$taskBuild='C:/Work/yoRadio/.worktree/small-tv-factory-audit/.build/small-tv-nothrow-20261026'
$taskOld='C:/Work/yoRadio/.worktree/small-tv-timer-bounds/.build/small-tv-esp32c2'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_nothrow_fix_evidence.py `
  --proof Small_TV/qemu/parity/nothrow-fix-validation-20261026.json `
  --elf "$taskBuild/small_tv_reconstructed.elf" `
  --app firmware/development/small-tv-esp32c2-reconstructed/app.bin `
  --object "$taskBuild/esp-idf/app/CMakeFiles/__idf_app.dir/platform/nothrow_new.cpp.obj" `
  --nvs "$taskBuild/esp-idf/nvs_flash/libnvs_flash.a" `
  --old-elf "$taskOld/small_tv_reconstructed.elf" --old-app "$taskOld/small_tv_reconstructed.bin"
```

Дальше по factory пункту: Ghidra metadata ranges, точная идентификация factory
NVS caller, оставшиеся TIM/null-completion/station lifetime/BSS ranges/aliases.
Пункты1–3 прошлого списка и все финальные gates сохраняются в плане.

Следующий [factory NVS checkpoint](FACTORY_NVS.md) установил полное312-byte
source identity заводского caller и подтвердил integrated factoryabort/nativeNO_MEM
через реальные allocator instructions. Он не меняет production build этого fix.
