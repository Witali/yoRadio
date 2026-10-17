# Отключаемая отладка Small TV и QEMU

Оба проекта теперь собираются без подробной диагностики по умолчанию.
`build.ps1 -DebugLogging` включает CMake `DEBUG=ON`; приложение, ESP-IDF и
bootloader используют уровень 4 вместо обычного уровня 2. Посторонние SDK
настройки, оптимизация, assertions и GDB symbols сохраняются. Debug BIN имеет
отдельный архив `small-tv-esp32c2-reconstructed-debug`; manifest содержит режим.
QEMU shared C2/C3 installers имеют тот же ключ, прямой Meson option — `esp_debug`.
В OFF исключены packet formatter, RX/MMIO traces и DNS/NTP printf с аргументами.
QOM `debug-logging` read-only; raw frame dumps остаются выключены в обоих режимах.
QEMU commit — `04443f07dc`. PowerShell common `-Debug` относится к PowerShell.

Проверены полные OFF → ON → OFF сборки в одном каталоге и четыре реальных
logging runs по 20 условий: ROM/SDK, Wi-Fi, UDP SNTP, четыре темы через HTTP,
captive 302 и LCD после переинициализации. Обычный UART: 0 I/D/V, 3 W; debug:
79 I, 3883 D, 3 W. Startup string исключена из обычного BIN. Итоговый appEF66D557
/ ELF8FCE7524, debug11DDCE49 / ELFDBE574C9, source81CF614C / 59 inputs.
Ранний обычный 5CA/B2 сохранён отдельно, его результаты не переименованы.

Каждый из трёх QEMU режимов прошёл 11 packet regressions, оба режима — modular
SPI/I²C/SD/GPIO и boot/source/no-panic CYD/C3 OLED. Обычные pixel hashes прежние.
Debug C3 modular host-timed capture отличается фазой бегущей строки/AP startup
text и не объявляется pixel-equivalence. Xtensa не менялся; CYD LCD проверен
QTest. OFF EXE76A8221C отличается от раннего E2103F7F export timestamp; остальные
PE sections, включая `.text/.data/.rdata`, совпадают. Debug EXE — 99940EA2.

Quiet observer читает настоящий atomic connection flag вместо debug UART:
4 cycles/16.475576 guest s, 5 snapshots/32 HTTP/2 reconnect. Minimum sampled heap
87 576, SDK sum of minima 55 868, lowest stack fill 480 у settings. Итоговый EF66
прошёл H09: 34 условия/16 пар/68 запросов с upload/scan/weather/retry/restart/
новым cold boot. Restart считается по ROM marker. Четыре body cases прошли:
второй GET за 4.494401/4.539967/0.133139 s при прежнем пределе 6.

Первые неверные ожидания probes (404 вместо 302; промежуточный очищенный кадр),
Windows cleanup lock и bare Meson define сохранены как harness/installer ошибки.
Числа, scope и хеши — [validation JSON](debug-logging-validation-20261017.json).
Это не новый full parity/24h H10. Старый console boot gate на этом этапе ещё
ожидает INFO; его нужно адаптировать перед full обычного BIN. Transport suite
требует diagnostic QEMU messages. DD41/96A/B4/30F checkpoint сохраняет прежнюю
область. Физические платы не прошивались/сбрасывались; ВМ участка закрыты.
