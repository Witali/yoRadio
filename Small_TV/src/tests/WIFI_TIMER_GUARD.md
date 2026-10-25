# Защита Wi-Fi timer ID перед входом в SDK

Продолжение [WIFI_TIMER_DISPATCH.md](WIFI_TIMER_DISPATCH.md). Найденный pre-bound
read исправлен в `app/network/wifi_timer.c`: ID 14..255 отклоняются до вызова
vendor dispatcher. Сообщение освобождается один раз через тот же
`g_osi_funcs_p->_free`, который использует SDK. Валидные ID 0..13 и null-message
передаются оригинальной функции. Метка `FIXED_FACTORY` сохраняет адреса дефекта.

Это исправление частного ABI pinned ESP-IDF 6.1 / ESP32-C2. При сборке проверяются
32-битный pointer, версия OS adapter 9 и `_free` offset 176. Post-link проверка
требует dense table 0..13 и прежний sentinel; смена SDK/target требует review.
Защита не зависит от DEBUG и не добавляет задержки, Flash I/O или allocations.

## Реальный вход из ROM

Одного `--wrap=pp_timer_do_process` оказалось недостаточно для доказательства.
Новый object необходимо удержать `--undefined=__wrap_pp_timer_do_process`, иначе
линкер не извлекал его из app archive. Это выявила первая неуспешная линковка.

Далее post-link check выявил, что `ppTask` имеет `SHN_ABS`: native symbol
`0x40001c44` — trampoline в ROM `0x40046eec`. Размер 522 из archive symbol не
является размером ROM body (554). Нельзя считать SDK archive call доказанным
вызовом из linked flash-кода.

В точном ROM rev200 `289ce00e…` событие 8 выбирает блок `0x40046fb8` через
таблицу `0x3ff4553c`. Блок читает `pp_wdev_funcs` из `0x3fcdfddc`, затем callback
из `+356`, берёт message из task frame `sp+12` и выполняет `jalr`.
Полное тело native `wdev_funcs_init` сопоставлено с текущим SDK object: его
function-pointer relocation разрешается в guard, а не в original dispatcher.

В отдельном host CPU исполнена фактическая инициализация от успешного calloc
до настоящего возврата функции для flags 0/4/8/12. Во всех четырёх случаях
финальный `+356` содержит guard и больше не переписывается. Используются реальные
initialized ELF data; beacon callbacks, подготовленные предшествующим
`wdev_data_init`, заданы как явные opaque data stubs и не исполняются.

Затем настоящий 12-байтный ROM caller использует **эту инициализированную таблицу**
для каждого ID 0..255. Так проверен путь ROM→table→guard→SDK,
а не только наличие wrap-флага или искусственно вставленного guard pointer.

## Результаты

- 258 прямых cases: все byte IDs, null message и callback return 0.
- 256 cases через реальный ROM event-8 block.
- Четыре полных successful-allocation initialization tails до возврата SDK.
- Всего 518 cases; invalid IDs не входят в vendor и не читают timer table.
- По одному free для каждого non-null сообщения; valid/null semantics сохранены.
- Контроль без guard снова воспроизводит исходный OOB read при ID 255.

Callbacks/log/free — объявленные внешние host stubs. Это не симуляция всей
очереди/scheduler или transitive callback effects. Полные network/display,
длительные и аппаратные gates для нового build остаются отдельными.

Production DEBUGoff build успешно собран и сохранён в
`firmware/development/small-tv-esp32c2-reconstructed/`:

| Identity | Значение |
| --- | --- |
| app | `c91294fca6acb16283605eef8aedcf98102d7a8ad42076c09b058594a5c97e93` |
| ELF | `9e4ec88d6e85ae58fa3e164362f1b10491f9edef0feaa4af8c52c9fa88446e24` |
| source aggregate | `04b19378061ef5cdad4fd56f27477cafb4d454f58b0767df30eba66384333bcd` |
| Размер app | 1476480 байт, +48 к прежнему build |
| Guard body | 46 байт |

`build.ps1` выполняет static link/ROM/table qualification перед архивированием,
сохраняет `wifi-timer-guard.json` и включает checker sources в source manifest.
Нужен pinned ROM ELF package `esp-rom-elfs/20260528`; build ничего не прошивает.
Для обычного ручного `idf.py` post-link checker нужно выполнить отдельно.

[Архив](../../qemu/parity/wifi-timer-guard-validation-20261025.json) привязан к
этим app/ELF/source, 12 checker sources и реальным SDK archives/ROM.
Дополнительный host transcript — один gzip, 1902 байта. SDK/ELF/полный RAM dump
не дублируются; полный link trace уже находится в development artifact.

```powershell
$env:PYTHONPATH='C:/Work/yoRadio/.build/small-tv-parity/oracle-deps'
& 'C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe' -B -X utf8 `
  Small_TV/src/tests/verify_wifi_timer_guard_evidence.py `
  --proof Small_TV/qemu/parity/wifi-timer-guard-validation-20261025.json `
  --sdk-libraries C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6/components/esp_wifi/lib/esp32c2 `
  --rom C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf
```

## Сопутствующий build follow-up

При свежей сборке libjpeg `jconfigint.h` изменил `BUILD` с 20261020 на 20261025.
Codec sources/patches прежние, но raw library SHA и cache codec ID изменились.
Нужна отдельная оптимизация reproducible build date/inputs, чтобы одинаковый
декодер не заставлял заново создавать Flash RGB565 cache только из-за даты.
Сохранять library/codec ownership guard: исключать важные identity checks ради
совпадения кэша нельзя. Проверить стабильность между датами/путями и сохранение
инвалидации при настоящем изменении codec. Это ещё не исправлено данным guard.
