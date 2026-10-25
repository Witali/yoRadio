# Таймеры Wi-Fi в ранее неразобранных участках

Продолжение [SDK gap recovery](SDK_GAP_RECOVERY.md), 25 октября 2026.
Вызов `0x4207b120` принадлежит `pp_timer_coex_slice`, диапазон
`0x4207b11a..0x4207b12c` с исключённым концом. Четыре тела между
`0x4207581e` и `0x42075896` также сопоставлены с полными функциями SDK.

| Функция | Factory start | Factory bytes | Native start | Native bytes |
| --- | --- | ---: | --- | ---: |
| `pm_dream_timeout_process` | `0x4207581e` | 16 | `0x4207ab86` | 16 |
| `pm_sleep_delay_timeout_process` | `0x4207582e` | 32 | `0x4207ab96` | 28 |
| `pm_disconnected_sleep_delay_timeout_process` | `0x4207584e` | 28 | `0x4207abb2` | 28 |
| `pm_coex_restart_timeout_process` | `0x4207586a` | 44 | `0x4207abce` | 44 |
| `pp_timer_coex_restart` | `0x4207b07a` | 18 | `0x42080920` | 18 |
| `pp_timer_disconnected_sleep_delay` | `0x4207b0f6` | 18 | `0x42080994` | 18 |
| `pp_timer_sleep_delay` | `0x4207b108` | 18 | `0x420809a6` | 18 |
| `pp_timer_coex_slice` | `0x4207b11a` | 18 | `0x420809b8` | 18 |
| `pp_timer_dream` | `0x4207b13e` | 18 | `0x420809dc` | 18 |

Это обработчики энергосбережения SDK и его таймерные обёртки. Например,
dream-обработчик очищает байт состояния и передаёт управление
`pm_enable_sleep_delay_timer`; sleep-delay обработчики очищают свой флаг и
условно переходят в соответствующий sleep-handler. По этим функциям не
добавлялась задержка в пользовательский интерфейс и не удалялись таймеры SDK.

## Как подтверждены имена

`tools/match_factory_timers.py` заново проверяет прежние три SDK-функции и
их shared symbol bindings из неизменных библиотек `esp32-wifi-lib`
`b87cce81803b85c3639fb14bac6c24cff6d0fbad`. Для новых девяти тел проверяются
все fixed instruction bits, разрешённые ELF relocations/RELAX, локальные
переходы и точные границы. Суммарно это 238 исходных SDK bytes, 210 factory
bytes и четыре локальных перехода.

Пять обёрток почти одинаковы: загрузить аргумент, вызвать обработчик, вернуть
единицу. Один только instruction pattern принимает соседнюю реальную обёртку
за `pp_timer_coex_slice`, связывая её call с другим адресом. Поэтому новый слой
обязательно сверяет callee с подтверждённым `pm_coex_slice_timeout_process`
`0x420756f0` и другими известными targets. Локальный `.LANCHOR0` сопоставляется
в контексте того же object/section, а не глобально по одинаковому имени.

`tools/reverse/native_timer_match.py` проверяет те же полные SDK-модели против
нашего точного ELF `76b5ce37…`. Все девять тел совпали после допустимых
relocations/relaxation; глобальные calls/data bindings разрешились в реальные
символы native ELF, локальные state anchors согласованы. Разница 32/28 байт
у sleep-delay объясняется разрешённым сокращением вызова, а не потерянной веткой.

Это соответствие **выбранных тел**. Реализации вызываемых функций могут
различаться между SDK, как уже описанная coexistence-обёртка. Полная семантическая
эквивалентность, RF, тайминги и достижимость из диспетчера этим не доказаны.
Функции в persistent Ghidra DB не создавались: следующий шаг — уточнить
метаданные/регистрацию dispatch callbacks в отдельной transient-копии.

## Проверки и воспроизведение

На настоящих SDK/factory bytes прошли восемь rejection controls: соседняя
обёртка, return literal, изменённый relocated callee, усечённое тело, неверный
конец, неверный/отсутствующий callee anchor и чужой local state anchor. Ещё две
подмены отвергнуты на native: соседняя обёртка и return literal.

В `qemu/parity/factory-timers-20261025/` сохранены match traces и результат
повторной проверки: два gzip-файла, 6438 байт. Полные ELF/SDK/assembly и
изменяющиеся runtime journals не дублируются.

```powershell
$py='C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe'
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& $py -B -X utf8 Small_TV/src/tests/factory_timers_test.py `
  --elf C:/Work/yoRadio/.build/small-tv-reverse/factory-analysis.elf `
  --sdk-libraries C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8 `
  --match-report Small_TV/qemu/parity/factory-timers-20261025/matches.json.gz `
  --native-elf .build/small-tv-esp32c2/small_tv_reconstructed.elf `
  --output .build/factory-timers-replay/report.json
```

Output должен быть новым файлом. Factory ELF, SDK archives и native ELF
привязаны к точным identities. Команда повторно строит все match traces и
проверяет source hashes, а не доверяет архивному `passed`.

Следующий checkpoint: [WIFI_TIMER_DISPATCH.md](../tests/WIFI_TIMER_DISPATCH.md)
связывает все 14 событий с register/post/dispatch, уточняет 21 Ghidra body и
выполняет точные dispatcher instructions. Найдены явное различие имён/callee
для события 11 и недочёт pre-bound table read при некорректном ID; production
исправление и transitive review остаются в плане.
