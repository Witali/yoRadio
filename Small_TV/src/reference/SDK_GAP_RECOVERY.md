# Три пропущенные функции Wi-Fi SDK

Продолжение [полного поиска ссылок](FULL_IMAGE_XREFS.md), 24 октября 2026.
Три GNU-only GP sites оказались внутри функций Wi-Fi-библиотек ESP-IDF 5.5.4.
Их имена и границы подтверждены сопоставлением полных тел, включая локальные
переходы. Исходная прошивка и наша production-сборка не изменялись.

| Функция | Заводской диапазон, конец исключён | SDK / linked bytes | Локальные переходы |
|---|---|---|---|
| `ieee80211_tx_mgt_cb` | `0x420581b6..0x4205838a` | 516 / 468 | 27 |
| `wifi_connect_process` | `0x420662da..0x4206632e` | 100 / 84 | 1 |
| `pm_coex_slice_timeout_process` | `0x420756f0..0x4207581e` | 318 / 302 | 15 |

Всего 934 исходных SDK bytes сопоставлены с 854 заводскими. Разница объясняется
17 разрешёнными сокращениями AUIPC/JALR→JAL и тремя удалёнными LUI при GP relaxation.
Все биты инструкций вне полей релокаций должны совпадать. Изменяемые поля ограничены ELF
relocations; нужен соответствующий `R_RISCV_RELAX`. Проверяются все 43 локальных
перехода, повторные ссылки на один symbol и общие `g_wifi_nvs`, `g_ic`,
`g_osi_funcs_p`/`wifi_log` между функциями. Это идентификация SDK-кода; полная
семантическая эквивалентность прошивок этим не доказывается.

Использован tag ESP-IDF `v5.5.4`, commit
`735507283d5b2f9fb363a1901172dbd9e847945d`; его gitlink указывает на
[`esp32-wifi-lib` `b87cce81803b85c3639fb14bac6c24cff6d0fbad`](https://github.com/espressif/esp32-wifi-lib/tree/b87cce81803b85c3639fb14bac6c24cff6d0fbad).
Локальный SDK имел исходники, но не этот подмодуль. Три библиотеки C2 загружены
в отдельную ignored папку анализа, с проверкой Git blob и SHA-256. Установленные
SDK не модифицировались. В новый архив целые SDK libraries не включены.

## Исправление представления Ghidra

В исходной базе три адреса были undefined `DataDB`, без содержащих функций.
Новая `RecoverFactoryGaps.java` работает с копией проекта в headless `-readOnly
-noanalysis`; временно создаёт только подтверждённые инструкции и function bodies.
Все initialized memory hashes до и после совпали. После завершения процесса
все десять файлов как исходного проекта, так и его копии остались побайтно прежними.

Уточнённый экспорт содержит 5143 перечисленные функции вместо 5140 и 286671
инструкцию вместо 286384. Все 396 GP memory instructions теперь согласуются
с GNU. `gp_coverage_agrees=true`, список прежних трёх gaps пуст. Полнота всего
образа остаётся недоказанной: отсутствие других GP gaps не исключает непросмотренные
функции без GP или другие вычисляемые ссылки. В частности, caller `0x4207b120`
ещё не имеет containing function в базе; его дальнейший разбор остаётся в плане.

Самостоятельный счётчик FunctionManager здесь равен 5145→5148, а перечисление
в экспортёре — 5140→5143. Обе величины выросли ровно на три; смешивать их нельзя.
Для хранения изменений достаточно delta из 14 function rows, трёх GP rows и
instruction count. Полный 7-МБ адресный граф повторно не архивируется.

## Соответствующие символы нашей сборки

В точном native ELF `76b5ce37…` уже связаны:

| Символ | Адрес | Bytes |
|---|---|---|
| `ieee80211_tx_mgt_cb` | `0x4205b482` | 452 |
| `wifi_connect_process` | `0x4206a534` | 836 |
| `pm_coex_slice_timeout_process` | `0x4207ab2c` | 6 |

Последний символ устанавливает `a0=1` и делает tail jump в
`pm_coex_go_to_sleep`, `0x4207a9f0`, 316 bytes. Это обёртка; размер 6 bytes сам по
себе не означает отсутствия реализации. Наличие символов и перехода проверено
по байтам и таблице символов ELF. Эти данные не приравнивают поведение двух
версий SDK и не закрывают весь RF/coexistence/power-management gate.

## Проверки и воспроизведение

[`factory-sdk-gaps-validation-20261024.json`](../../qemu/parity/factory-sdk-gaps-validation-20261024.json)
сохраняет источники, SDK provenance/hashes, полные match traces, typed Ghidra
observations, delta графа, native symbol links и состояние неизменности проектов.
24 payload references, 50296 новых gzip bytes; прежние payloads переиспользуются.
Нет полного factory dump/ELF, целых SDK libraries, VM flash/RAM/UART.

15 SDK controls отвергают изменённые registers/immediates, неверные local branches,
усечённое тело, отсутствие RELAX permission, разные targets повторного `wifi_log`,
несогласованный `g_wifi_nvs` и обрезанный настоящий ar archive. Ещё пять controls
проверяют восстановленный GP gap, имя владельца, bytes/bounds и изменение проекта.
Локальный branch-test проходит через relocation mask и отвергается именно
семантической проверкой target, а не только сравнением opcode.

```powershell
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_factory_sdk_evidence.py `
  --proof Small_TV/qemu/parity/factory-sdk-gaps-validation-20261024.json `
  --assembly .build/factory-all-executable-20261024.asm `
  --sdk-libraries .build/factory-gaps-20261024/sdk-wifi-b87cce8
```

GNU-файл воспроизводится из того же immutable ELF, как описано в предыдущем
checkpoint. SDK inputs должны иметь SHA-256:

| Файл | SHA-256 |
|---|---|
| `libnet80211.a` | `8f989ecd7104520083727442247aed08ad93ef2bc304ae727022f8573f4bc558` |
| `libpp.a` | `b460bb305a8d3c5e93489a03710108a06435d58bf12410e080c0c6805a74bade` |
| `libcore.a` | `85394ad591b3964c19d57fa8403b61a9ac5906c3f89a5d3a09d3493abf1e8353` |

Исторические source identities поддерживает `--source-revision`. Старый
full-image proof отдельно проходит с `--source-revision 36adbd6f7`, его девять
negative controls сохранены. H10 остаётся отдельным живым тестом и не прерывался.

Продолжение 25 октября: [SDK_TIMER_GAPS.md](SDK_TIMER_GAPS.md) идентифицирует
caller `0x4207b120` и четыре следующих PM-обработчика, проверяет девять тел с
пятью timer wrappers также против native ELF. Это уточнение имён/границ и
selected instruction correspondence; persistent Ghidra recovery и регистрация
диспетчерских callbacks остаются следующим шагом.
