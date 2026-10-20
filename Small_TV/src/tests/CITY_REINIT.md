# Город как команда переинициализации темы

Исправление `CITY-REINIT`, 2026-10-20. В factory `/updateCity` (`0x4200f2c0`)
после копирования города/страны устанавливаются persistence/weather flags,
очищается weather-valid, затем `0x4200f3cc` очищает `0x3fcc39e9`. Main loop
видит этот latch и вызывает `0x42008e08`, независимо от изменения строк.
Также очищаются SNTP config/notification flags `0x3fcc3ab9/0x3fcc3ab8`.
Адреса сверены по `reference/http_settings.c`, `application.c`, `time_setup.c`
и `assembly/http_updateCity_at_4200f2c0.asm`.

Ранее наш renderer получал такую команду только от `/setclocktype`. Сравнение
байтов настроек не обнаруживало повторный город, а обычное изменение города
не требовало повторной инициализации. Новый тест падает на исходном `51cd114f9`.

## Реализация и допустимые отличия

`settings_update_city` меняет только город/страну и увеличивает transient
theme revision под одним settings mutex. Snapshot renderer содержит согласованные
строки, тему и revision. Обновление не возвращает старую тему/яркость/photo sizes
из snapshot, снятого до чтения HTTP body. Повтор той же команды перерисовывает
тему, но не помечает неизменные байты dirty. Общий private helper сохраняет
прежние правила generation/dirty/deadline для остальных настроек.

Сохраняются прежние намеренные исправления: bounded JSON/region validation,
debounced writes, asynchronous weather с защитой от устаревшего ответа и
сохранение хорошего cache при повторе того же города. Местное время вычисляется
по актуальному country; time task наблюдает city/country. Успешный UTC sync не
теряется при смене города и не требует остановки исправного SNTP клиента.
Этот gate не заявляет полную эквивалентность SDK/SNTP или реального weather API.

При переинициализации фото сохраняется round-robin slot и сбрасывается активный
fade. Заводская версия очищает картинку, сохраняя старую фазу, и может закончить
переход с пустым экраном; этот подтверждённый баг не воспроизводится.

## Проверки

- 5806 native checks и 10 correspondence controls прошли. City tests охватывают
  четыре темы, три одинаковые команды, новый город, четыре неправильных запроса,
  ошибки публичного API и interleaving изменения темы/яркости во время body read.
  Отказы не меняют revision/настройки/weather requests; одинаковый город не
  вызывает повторный NVS commit. 6 artifact tests проверили новый архив и ресурсы.
- `city_theme_qemu.py`: четыре собственные native VM, восемь настоящих POST.
  Первый renderer event после команды обязан быть init; затем выполняется
  настоящая итерация, а для фото — весь шестишаговый fade. Полный вывод сохранён.
  Это проверка переходов, не pixel equivalence всех сцен.
- `photo_reinit_qemu.py --command city`: original воспроизводит blank bug;
  native выводит следующую фотографию. Сравнены все 57600 пикселей с literal
  factory replay, различий 0. Прежний `--command theme` также прошёл отдельно.
- Независимый network-only gate: factory AP/native AP/native STA, 15 HTTP cases,
  без LCD device. Отдельный cold LCD gate: 2 original + 2 native process cycles,
  точный полный factory setup frame, без HTTP/SDK network readiness criterion.

Все входы во время окончательных прогонов неизменны; каждый owner завершил свои
VM. Применялись только hardware breakpoints и read-only memory observations;
guest PC/RAM/instructions не подменялись. Идущий H10 B50D не использовался для
отладки и не перезапускался. Ранние ошибки нового harness (boot flash mapping,
ожидание только первой fade-фазы и потерянный dependency-root при replay)
сохранены failed; исправленные попытки имеют отдельные каталоги и результаты.

## Сборка и воспроизведение

App `3e030c1cc5f7b456fefc9985c397daf8340c33d1bb2805965b076147a07cd7e1`,
1170432 bytes, свободно 365568 bytes в app partition. ELF
`54293e9741134adca6bcb71e814498d692c048dfeba648d63b0e0ad5529667c4`.
DEBUG off. App/bootloader/resources/source manifest сохранены в
`firmware/development/small-tv-esp32c2-reconstructed/`. Decoder остаётся TJpgd;
эта правка не включает libjpeg. Полный suite/24h и физическая плата не проверялись.

```text
python Small_TV/src/tests/city_theme_qemu.py --dependency-root DEPENDENCIES --qemu-root FROZEN_QEMU --output NEW_OUTPUT
python Small_TV/src/tests/photo_reinit_qemu.py --command city --dependency-root DEPENDENCIES --qemu-root FROZEN_QEMU --output OTHER_NEW_OUTPUT
```

Нужны pinned Unicorn/pyelftools и read-only ROM/factory ELF в DEPENDENCIES.
Python bytecode generation выключать при использовании frozen helper trees.
Proof, exact inputs, failed/success logs и matching ELF:
[`city-reinit-validation-20261020.json`](../../qemu/parity/city-reinit-validation-20261020.json).
