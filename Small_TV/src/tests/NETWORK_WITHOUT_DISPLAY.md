# Сеть без LCD-устройства

`network_without_display_qemu.py` проверяет HTTP и SNTP factory/native в
собственных ВМ с `default-peripherals=off` и пустым списком external devices.
Исходный профиль не редактируется: копируется только его сетевая конфигурация.
QOM подтверждает отсутствие `lcd`, а hardware arguments не содержат модулей.
Гость исполняет обычную неизменённую прошивку и выполняет SPI writes в пустую
шину; готовность экрана, framebuffer и GPIO подсветки тесту не нужны.

Для каждого firmware выполняются cold boot и `system_reset`. После каждого
требуется свежий NTP response count, фактическое время SDK с расхождением менее
1секунды от точной метки UDP ответа и успешный настоящий GET `/getclocktype`.
Сравнение учитывает reset-relative HRT offset/correction; bootstrap UART не
является подтверждением SNTP. Для native дополнительно требуются реальные
connected/time_synced flags, отсутствие AP role и DHCP address10.0.2.15 из RAM
matching ELF. Для factory используются подтверждённые SDK offsets, привязанные
к immutable dump; полного чтения его Wi-Fi/DHCP role этим тестом не заявляется.

QMP wrapper отклоняет display commands, сохраняя список использованных команд.
Screendump не вызывается, PNG/PPM не создаются, display явно помечен not_run.
Boot имеет отдельный результат: ровно два ROM boot и отсутствие panic/watchdog.
Проверяются hashes всех59входов и неизменность исходного flash snapshot.
Используется `-snapshot`; это не проверка сохранения гостевых записей во flash.
Старые full/H10 и обычный LCD-профиль не меняются, дополнительных QMP/RSP
к H10 тест не открывает.

Запуск в рабочей копии с actual matching app/ELF и существующим frozen QEMU:

```powershell
python -X utf8 -B Small_TV/src/tests/network_without_display_qemu.py `
  --qemu-root C:/Work/yoRadio/.worktree/small-tv-jpeg-headers/.build/jpeg-header-qemu-complete-20261018 `
  --dependency-root C:/Work/yoRadio `
  --output C:/Work/yoRadio/.build/network-only-new
```

F1/ELF91E2/D64 прошёл оба firmware и обе фазы. Счётчики NTP1→2, четыре
контрольных ответа HTTP200 после readiness probes; максимальное абсолютное
расхождение SDK/wire timestamp0.191694s.
Native после reset: STA connected, AP false,10.0.2.15,time_synced true.
Для обоих процессов по2ROM boot, panic нет; все59inputs совпали.
Свидетельства: `../../qemu/parity/network-without-display-validation-20261018.json`.

Эта проверка доказывает независимость программной сетевой проверки от LCD.
Реальные RF/WPA/captive portal, доступность Internet/weather, LCD pixels/PWM,
длительная работа и физическая плата требуют своих сценариев.
