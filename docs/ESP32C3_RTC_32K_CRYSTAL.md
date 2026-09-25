# ESP32-C3: внешний часовой кварц 32 768 Гц

Ключ `-Rtc32kCrystal` выбирает **пассивный кварцевый резонатор 32.768 kHz**
как источник RTC для `idf/esp32c3-oled-native` (ESP-IDF v6.0.2).
Он работает независимо от `-DeepSleepClock`; для часов во сне нужны оба ключа.

## Подключение

- Один вывод кварца — **GPIO0 / XTAL_32K_P**.
- Второй вывод — **GPIO1 / XTAL_32K_N**.
- Нагрузочные конденсаторы от каждого вывода к GND подбираются по спецификации
  кварца с учётом паразитной ёмкости монтажа; универсального номинала нет.
- Espressif рекомендует ESR не выше 70 кОм. Соединения должны быть короткими;
  проверьте, что на GPIO0/GPIO1 конкретной платы нет другой нагрузки.

Это не внешний RTC-модуль по I2C и не активный генератор с тактовым выходом.
Используется режим ESP-IDF `EXT_CRYS`, а не `EXT_OSC`.
Выводы и требования взяты из
[даташита ESP32-C3](https://documentation.espressif.com/esp32-c3_datasheet_en.html)
и [рекомендаций Espressif по схеме](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html).

Энкодер по умолчанию тоже занимает GPIO0/GPIO1. При включённом кварце сборка
отклоняет эти выводы для фаз энкодера, его кнопки и настраиваемого level LED.
Отключите соответствующее устройство или назначьте другие свободные выводы
в `menuconfig`/собственном sdkconfig. При следующем запуске скрипта повторите
ключ `-Rtc32kCrystal`. Штатные OLED (GPIO5/6), PDM (GPIO10/3), BOOT (GPIO9)
и LED (GPIO8) с кварцем не конфликтуют.

## Сборка

Из корня репозитория/worktree, PowerShell 7:

```powershell
# Обычная прошивка с часами от кварца
.\build.ps1 -Rtc32kCrystal

# Часы от кварца с обновлением во сне каждые 500 мс
.\build.ps1 -DeepSleepClock -Rtc32kCrystal

# Production, с toolchain основного checkout
.\idf\esp32c3-oled-native\build-production.ps1 -Rtc32kCrystal -DependencyRoot C:\Work\yoRadio\.idf
.\idf\esp32c3-oled-native\build-production.ps1 -DeepSleepClock -Rtc32kCrystal -DependencyRoot C:\Work\yoRadio\.idf
```

| Ключи | Каталог сборки внутри native target | Production-образ внутри `firmware/development/` |
| --- | --- | --- |
| `-Rtc32kCrystal` | `build-rtc32k` / `build-production-rtc32k` | `esp32c3-oled-native-production-rtc32k/app.bin` |
| `-DeepSleepClock -Rtc32kCrystal` | `build-deep-sleep-clock-rtc32k` / `build-production-deep-sleep-clock-rtc32k` | `esp32c3-oled-native-deep-sleep-clock-rtc32k/app.bin` |

Параметры `BuildDirectory`, `Sdkconfig` и `FirmwareOutputDirectory` native-скриптов
сохраняют приоритет над автоматически выбранными путями. Ключ поддерживается
корневым, native и production скриптами. Прошивка платы автоматически не запускается.

## Настройки и поведение

С ключом скрипт задаёт `CONFIG_RTC_CLK_SRC_EXT_CRYS=y` и
`CONFIG_RTC_CLK_CAL_CYCLES=3000`. Без ключа он выбирает
`CONFIG_RTC_CLK_SRC_INT_RC=y` и калибровку 1024 такта. При каждом запуске
заменяются все элементы выбора источника RTC, калибровка и старые алиасы
`CONFIG_ESP32C3_RTC_CLK_*`, поэтому настройки не остаются от предыдущей сборки.

ESP-IDF запускает и калибрует кварц до приложения. Если он не запустился,
SDK после повторных попыток переходит на внутренний RC-генератор. В production
логи выключены, поэтому отсутствие сообщения не подтверждает работу кварца.
Для аппаратной проверки используйте сборку с логами и проверьте отсутствие
`32 kHz XTAL not found`, затем измерьте дрейф времени при длительном сне.

RTC wake stub получает фактическую калибровку выбранного источника через
`esp_clk_slowclk_cal_get()`. Алгоритм обновления каждые 500 мс остаётся общим
для кварца и RC, включая fallback. Кварц улучшает стабильность относительно
внутреннего RC, но итоговая точность зависит от резонатора, монтажа и температуры.
SNTP по-прежнему нужен для установки текущего времени; во сне Wi-Fi выключен.
Подробнее: [часы в deep sleep](ESP32C3_DEEP_SLEEP_CLOCK.md).

## Проверки без платы

```sh
python3 tests/run-esp32c3-rtc-crystal-pins.py
python3 tests/run-esp32c3-deep-sleep-clock.py
```

Нужны Python 3 и host C-компилятор `cc` (либо `CC`); на Windows можно использовать
WSL. Проверяются конфликты выводов и разрешённые переназначения, полусекундные
границы на 32 768 Гц, переход суток и существующие сценарии I2C/GPIO wake stub.
Аппаратный запуск кварца и его точность проверяются отдельно на плате.
