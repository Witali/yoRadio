# Диспетчер таймеров Wi-Fi

Продолжение [SDK_TIMER_GAPS.md](../reference/SDK_TIMER_GAPS.md), 25 октября 2026.
Проверены начальные таблицы из 14 событий и полные тела 17 функций в каждом
образе: 14 обёрток, регистрация post callback, передача события и диспетчер.
Это расширяет проверку за пределы прежних девяти выбранных функций.

| Объект | Factory | Native ELF `76b5ce37…` |
| --- | --- | --- |
| `g_pp_timer_info`, 120 байт | `0x3fcb52f8` | `0x3fcac978` |
| post callback slot | `0x3fcc3100` | `0x3fcb5d98` |
| `pp_timer_register_post_cb` | `0x4207b162` | `0x42080a00` |
| `pp_timer_process` | `0x4207b16e` | `0x42080a0c` |
| `pp_timer_do_process` | `0x420acc28` | `0x420d1486` |

SDK-таблица состоит из 14 восьмибайтных записей `{uint32 id, callback}` и
нулевой завершающей записи. Сверены все неизменяемые байты и ELF relocations
из прежнего pinned `libpp.a/pp_timer.o`. Пять ранее подтверждённых callback
адресов привязывают таблицу к известным именам; все 14 тел повторно проверены.
Среди похожих setter-функций нашлось четыре кандидата регистрации. Единственная
пара register/process использует один и тот же post callback slot.

| ID | Factory callback | Native callback при другом имени |
| ---: | --- | --- |
| 0 | `pp_timer_noise_check` | |
| 1 | `pp_timer_tbtt` | |
| 2 | `pp_timer_dream` | |
| 3 | `pp_timer_active` | |
| 4 | `pp_timer_coex_slice` | |
| 5 | `pp_timer_sleep_delay` | |
| 6 | `pp_timer_disconnected_sleep_delay` | |
| 7 | `pp_timer_connectionless_wake_interval` | |
| 8 | `pp_timer_connectionless_wake_window` | |
| 9 | `pp_timer_beacon_monitor` | |
| 10 | `pp_timer_beacon_monitor_tbtt` | |
| 11 | `pp_timer_max_idle` | `pp_timer_keep_alive` |
| 12 | `pp_timer_resample` | |
| 13 | `pp_timer_coex_restart` | |

Событие 11 требует отдельного semantic review. Его native-обёртка вызывает
`pm_keep_alive_timeout_process`, factory — `pm_max_idle_timeout_process`.
Имена версий заданы явно; одинаковый instruction pattern обёрток не доказывает
равенство вызываемых реализаций. В отчёте это остаётся открытым различием SDK.

## Проверка точных инструкций

Приватный Unicorn RV32 CPU выполняет исходные 178 байт `pp_timer_do_process`
для factory и native. Таблица, сообщение и стек — синтетические host fixtures;
callback/log/free заменены **явными внешними stubs**. Тело самого диспетчера
не патчится. Ни QMP/RSP, ни физическое устройство не используются.

Для каждого образа выполнен 501 случай: все ID 0..255, ещё 241 вариант с
подставленным байтом после таблицы, null message, переставленные допустимые
записи для linear fallback, null callback и callback с возвратом 0. Итого 1002
выполнения. Проверяются выбор callback, освобождение сообщения ровно один раз,
возвращаемое значение, log branch и фактические адреса чтений. Успех диспетчера
не означает возврат child callback: его return value здесь игнорируется.

Найден **недочёт SDK, пока не исправленный в production app**: до проверки
границ выполняется чтение `table[id].id`. Для ID 15..255 один байт читается за
пределами 120-байтной таблицы. Это воспроизведено и в factory, и в нашей сборке:
PC `0x420acc62` / `0x420d14c0`. Затем событие корректно отвергается, callback
не вызывается, сообщение освобождается, возвращается 0. ID 14 читает нулевую
завершающую запись внутри таблицы. ID 0..13 этого дефекта не проявляют.

Это характеристика существующего дефекта, не разрешение воспроизводить ошибку
в нашей прошивке. Следующий шаг — защита ID **перед** входом в vendor dispatcher
с сохранением ABI и освобождения сообщения. Проверить все ссылки, включая
прямой вызов из `ppTask` и pointer registration в `wdev_funcs_init`; один флаг
линкера сам по себе не доказывает, что каждый вход защищён. Работу с прошивкой
вести в другой task worktree: текущие app/ELF и producers используются soak.

## Метаданные Ghidra и архив

В отдельной копии проекта, `-readOnly -noanalysis`, восстановлены 18 функций и
уточнены три существующие. Всего 21 qualified body с прежними PM handlers;
14 callback table edges проверены по реальным байтам. Enumerated functions
5143→5161, FunctionManager count 5148→5166. Добавлено ровно 143 инструкции,
все внутри подтверждённых диапазонов. Полный повторный xref audit сохраняет
396 согласованных GP instructions без прежних GP gaps.

Initialized program bytes до/после совпали. Все десять файлов исходного
проекта и десять файлов копии побайтно прежние после обоих headless executions.
Изменения метаданных не сохранялись в persistent DB. Хранится delta графа,
полный многомегабайтный граф повторно не архивируется.

[Архив](../../qemu/parity/timer-dispatch-validation-20261025.json): 28 ссылок,
15 новых gzip / 47112 байт, 13 reused payloads. Consumer заново проверяет
прежние 20 controls, оба dispatcher body, 1002 исполнения и 15 новых rejection
controls таблицы/metadata/instruction scope/project integrity.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_timer_dispatch_evidence.py `
  --proof Small_TV/qemu/parity/timer-dispatch-validation-20261025.json `
  --sdk-libraries C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-gaps-20261024/sdk-wifi-b87cce8 `
  --assembly C:/Work/yoRadio/.worktree/small-tv-improvement-plan/.build/factory-all-executable-20261024.asm
```

Структура и выбранные инструкции проверены; весь runtime event lifecycle,
transitive callback effects, исправление prefetch, RF, whole-image equivalence,
24h и аппаратная приёмка остаются открытыми.
