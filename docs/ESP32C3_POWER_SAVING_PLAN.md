# ESP32-C3 OLED: план режима пониженного энергопотребления

Статус: план реализации, функции ещё не включены в production-профиль.

Целевая платформа: `idf/esp32c3-oled-native`, ESP-IDF v6.0.2,
ESP32-C3 SuperMini OLED 72×40.

## Цель

После остановки радио прошивка должна снижать потребление, сохраняя выбранное
пользователем поведение OLED:

- `clock` — полноэкранные часы и доступный WebUI;
- `blank` — выключенный OLED и доступный WebUI;
- BOOT, энкодер или команда WebUI немедленно возвращают обычный экран;
- запуск радио восстанавливает максимальную производительность без щелчков,
  потери стереоканалов и деградации памяти.

Основным режимом сна должен быть **Automatic Light-sleep ESP-IDF**. Deep-sleep
не входит в основной сценарий, потому что он разрывает Wi-Fi, останавливает
WebUI и перезапускает приложение после пробуждения.

## Официальная документация Espressif

Реализация должна сверяться с документацией для ESP-IDF v6.0.2 и ESP32-C3:

- [Introduction to Low Power Mode for Systemic Power Management](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/low-power-mode/low-power-mode-soc.html)
- [Introduction to Low Power Mode in Wi-Fi Scenarios](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/low-power-mode/low-power-mode-wifi.html)
- [Power Management API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/power_management.html)
- [Sleep Modes and Wakeup Sources](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/system/sleep_modes.html)
- [Wi-Fi Performance and Power Save](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/wifi-driver/wifi-performance-and-power-save.html)
- [I2S driver and power-management locks](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-reference/peripherals/i2s.html)
- [ESP32-C3 Series Datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.html)

Ключевые выводы из документации:

1. Automatic Light-sleep работает через ESP-IDF Power Management и FreeRTOS
   Tickless Idle. Вручную вызывать `esp_light_sleep_start()` в обычном
   Wi-Fi-сценарии не требуется.
2. Для сохранения соединения с роутером Automatic Light-sleep должен работать
   совместно с Wi-Fi Modem-sleep. Драйвер сам просыпается по DTIM.
3. I2S-драйвер получает PM-lock при `i2s_channel_enable()` и освобождает его при
   `i2s_channel_disable()`. Активный PDM-канал поэтому мешает полноценному
   light sleep.
4. Любой цифровой GPIO может будить ESP32-C3 из light sleep, если GPIO-домен
   остаётся включённым.
5. GPIO9 питается от `VDD3P3_CPU`, а не `VDD3P3_RTC`, поэтому его нельзя считать
   источником пробуждения из deep sleep.

## Текущее состояние прошивки

После `Stop` уже выполняется следующее:

- поколение аудиопотока меняется, поэтому устаревшие сетевые и PCM-пакеты
  отбрасываются;
- HTTP/HTTPS-клиент закрывается после выхода из чтения с тайм-аутом до 250 мс;
- декодер освобождается;
- ICY, bitrate и stream info очищаются;
- Wi-Fi переключается с `WIFI_PS_NONE` на `WIFI_PS_MIN_MODEM`;
- level LED гаснет;
- OLED переходит в `clock` или `blank` после сохранённого тайм-аута.

Оставшиеся источники потребления:

- `CONFIG_PM_ENABLE` выключен, CPU работает с фиксированным максимумом
  160 МГц;
- stereo I2S PDM остаётся включённым на 48 кГц;
- output task опрашивает PCM-очередь каждые 5 мс;
- decoder task опрашивает encoded-очередь каждые 20 мс;
- display task проверяет состояние каждые 50 мс;
- в режиме часов OLED перерисовывается каждую секунду из-за мигающего
  двоеточия.

## Целевая модель состояний

Добавить единый `power_manager` со следующими состояниями:

| Состояние | CPU/PM | Wi-Fi | PDM | OLED |
|---|---|---|---|---|
| `PLAYING` | 160 МГц, light sleep запрещён активными ресурсами | `WIFI_PS_NONE` | включён | экран станции |
| `STOPPED_AWAKE` | DFS разрешён | `WIFI_PS_MIN_MODEM` | выключается | экран станции |
| `IDLE_CLOCK` | Automatic Light-sleep | `WIFI_PS_MIN_MODEM` | выключен | часы |
| `IDLE_BLANK` | Automatic Light-sleep | `WIFI_PS_MIN_MODEM` | выключен | display-off |
| `WAKING` | 160 МГц | зависит от последующей команды | запускается при Play | экран станции |

Переходами должен управлять один модуль. Дисплей, сеть, кнопка и аудиосервис
не должны независимо менять режим питания.

## Этап 1. Измерения и диагностика

- [ ] Добавить отдельный compile-time флаг экспериментального power-saving.
- [ ] В debug-профиле включить `CONFIG_PM_PROFILING`.
- [ ] Добавить диагностическую команду с `esp_pm_dump_locks()`.
- [ ] Измерить исходное потребление в `PLAYING`, `STOPPED`, `CLOCK` и `BLANK`.
- [ ] Зафиксировать свободную RAM, largest free block и минимальную RAM.
- [ ] Проверить PDM GPIO10/GPIO3 осциллографом после `Stop`.

Production-профиль не должен постоянно печатать PM-статистику. Диагностика
включается макросом и не должна менять рабочую логику.

## Этап 2. Приостановка аудиовыхода

Добавить в `native_audio_output` явные операции `suspend` и `resume`.

### Stop / suspend

1. Остановить приём новых PCM-пакетов.
2. Выполнить короткий bias ramp к цифровому нулю.
3. Очистить незавершённый локальный PCM-блок.
4. Вызвать `i2s_channel_disable()`.
5. Удерживать GPIO10/GPIO3 в безопасном низком состоянии, если это не создаёт
   постоянного тока через RC-фильтр или вход усилителя.
6. Оставить зарегистрированный I2S-канал и DMA-память выделенными.

Сохранение выделенной памяти уменьшает риск фрагментации и ускоряет Play.
Полное `i2s_del_channel()` допускается позже как отдельный агрессивный профиль,
только после теста многократных циклов Stop/Play.

### Play / resume

1. Удержать CPU на максимальной частоте.
2. Включить I2S-канал.
3. Предзагрузить DMA цифровым нулём.
4. Выполнить bias ramp.
5. Разрешить вывод PCM.

## Этап 3. Событийные задачи вместо опроса

Automatic Light-sleep эффективен только когда задачи заблокированы.

- [ ] `stream_task` оставить заблокированной на command queue через
  `portMAX_DELAY`, когда радио остановлено.
- [ ] Разбудить decoder task при Stop управляющим пакетом или task notification,
  затем ждать encoded-очередь без 20-мс polling.
- [ ] Разбудить output task при Stop отдельным событием, затем ждать PCM-очередь
  без 5-мс polling.
- [ ] Перевести display task на event/notification от состояния, кнопки,
  настроек и таймера часов.
- [ ] Не отправлять WebSocket status без изменения данных; оставить редкий
  heartbeat только при необходимости протокола.

Нельзя просто увеличить polling-интервалы: это ухудшит отзывчивость и всё равно
будет периодически выводить CPU из сна.

## Этап 4. Часы и OLED

OLED сохраняет изображение без повторной передачи framebuffer.

- [ ] По умолчанию обновлять `HH:MM` только при изменении минуты.
- [ ] Сделать мигающее двоеточие отдельной настройкой; оно требует пробуждения
  раз в секунду.
- [ ] При `clock` оставить OLED включённым и при необходимости уменьшить
  contrast через существующую настройку яркости.
- [ ] При `blank` очистить framebuffer, передать его один раз и выполнить
  display-off.
- [ ] По первому фронту BOOT немедленно восстановить экран станции и обычную
  яркость, не ломая распознавание single/double/long press.

## Этап 5. DFS и Automatic Light-sleep

Начальная конфигурация для платы:

```text
CONFIG_PM_ENABLE=y
CONFIG_FREERTOS_USE_TICKLESS_IDLE=y
CONFIG_FREERTOS_IDLE_TIME_BEFORE_SLEEP=3
```

Во время инициализации вызвать `esp_pm_configure()`:

```c
esp_pm_config_t config = {
    .max_freq_mhz = 160,
    .min_freq_mhz = 40,
    .light_sleep_enable = true,
};
ESP_ERROR_CHECK(esp_pm_configure(&config));
```

Ограничения:

- `CONFIG_PM_POWER_DOWN_PERIPHERAL_IN_LIGHT_SLEEP` первоначально оставить
  выключенным, иначе обычный GPIO wakeup для BOOT/GPIO9 недоступен;
- `CONFIG_ESP_SLEEP_POWER_DOWN_FLASH` первоначально не включать;
- `CONFIG_PM_POWER_DOWN_CPU_IN_LIGHT_SLEEP` и дополнительные отключения
  MAC/baseband включать отдельным этапом после проверки базового light sleep;
- воспроизведение должно удерживать собственный `ESP_PM_CPU_FREQ_MAX` lock;
- после полного Stop этот lock должен освобождаться;
- I2S lock освобождается самим официальным драйвером при
  `i2s_channel_disable()`.

## Этап 6. Wi-Fi

| Состояние | Политика |
|---|---|
| Воспроизведение | `WIFI_PS_NONE` для минимальной задержки потока |
| Радио остановлено | `WIFI_PS_MIN_MODEM` |
| Access Point | без Automatic Light-sleep до отдельной проверки AP-сценария |

`WIFI_PS_MAX_MODEM` не использовать по умолчанию: официальный драйвер
предупреждает о большей задержке до listen interval и возможной потере
broadcast-пакетов. Для WebUI и WebSocket безопаснее `WIFI_PS_MIN_MODEM`.

## Этап 7. Пробуждение BOOT

Для light sleep настроить GPIO9 как активный низким уровнем источник:

```c
ESP_ERROR_CHECK(gpio_wakeup_enable(GPIO_NUM_9, GPIO_INTR_LOW_LEVEL));
ESP_ERROR_CHECK(esp_sleep_enable_gpio_wakeup());
```

После wakeup существующий ISR должен положить событие в очередь кнопки. Первое
событие возвращает экран станции; дальнейший debounce и распознавание жеста
работают без отдельной ветки.

Не использовать GPIO9 как источник deep-sleep wake: по официальному datasheet
он находится в домене `VDD3P3_CPU`.

## Этап 8. WebUI и сохранение настроек

Добавить настройку `Power saving while stopped`:

- `off` — без новой политики, режим совместимости;
- `modem sleep` — текущее поведение Wi-Fi без Automatic Light-sleep;
- `light sleep` — рекомендуемый режим.

Существующие `clock/blank` и тайм-аут остаются отдельными параметрами.
Дополнительные настройки:

- мигание двоеточия;
- яркость часов, если решено не использовать общую яркость дисплея.

Все значения должны сохраняться в NVS и отправляться в WebUI при первоначальной
загрузке страницы, а не непрерывно перезаписывать поля.

## Deep-sleep

Deep-sleep можно рассматривать только как отдельный будущий режим `blank`:

- Wi-Fi и WebUI будут недоступны;
- пробуждение перезапускает приложение;
- GPIO9 не подходит как штатный deep-sleep wakeup;
- потребуется другой вывод домена `VDD3P3_RTC`, таймер или полное включение
  питания;
- пользователь должен получить явное предупреждение в WebUI.

Для режима часов с доступным WebUI deep-sleep не применять.

## Последовательность перехода Stop → idle

1. Зафиксировать новое поколение потока.
2. Прекратить публикацию ICY и PCM старого поколения.
3. Закрыть HTTP/TLS в stream task.
4. Освободить декодер и несовместимый codec arena.
5. Очистить encoded/PCM-очереди.
6. Погасить level LED.
7. Выполнить PDM ramp и `i2s_channel_disable()`.
8. Переключить Wi-Fi в `WIFI_PS_MIN_MODEM`.
9. Освободить `ESP_PM_CPU_FREQ_MAX` lock.
10. После тайм-аута показать часы или выключить OLED.
11. Когда все задачи заблокированы, ESP-IDF самостоятельно входит в
    Automatic Light-sleep.

## Последовательность пробуждения и Play

1. GPIO, Wi-Fi или таймер будит CPU средствами ESP-IDF.
2. Зафиксировать `ESP_PM_CPU_FREQ_MAX` lock.
3. Немедленно показать экран станции при пользовательском событии.
4. При Play переключить Wi-Fi в `WIFI_PS_NONE`.
5. Включить I2S, предзагрузить нули и выполнить bias ramp.
6. Подготовить новое поколение потока.
7. Открыть HTTP/HTTPS.
8. Определить FOURCC/signature потока и создать нужный декодер.
9. Начать PCM-вывод.

## Проверки на реальной плате

- [ ] Debug-сборка показывает отсутствие неожиданных PM-lock в idle.
- [ ] Production и debug используют одинаковую рабочую логику.
- [ ] GPIO10/GPIO3 не несут PDM-частоту после Stop.
- [ ] BOOT будит экран и сохраняет single/double/long press.
- [ ] WebUI остаётся доступным после длительного light sleep.
- [ ] Физическая кнопка и WebUI синхронно обновляют состояние.
- [ ] Часы корректны после SNTP и длительного сна.
- [ ] HTTP и HTTPS корректно закрываются и запускаются заново.
- [ ] MP3, AAC, FLAC, Vorbis и Opus проходят Stop/Play.
- [ ] Не менее 100 циклов Stop/Play не уменьшают largest free block.
- [ ] Переключение станций не смешивает декодеры разных поколений.
- [ ] Не возникает щелчков при suspend/resume PDM.
- [ ] Измерен ток для `PLAYING`, `STOPPED_AWAKE`, `IDLE_CLOCK` и `IDLE_BLANK`.
- [ ] Измерена задержка первого ответа WebUI после DTIM/light sleep.

## Критерии готовности

Функцию можно включать по умолчанию для ESP32-C3 OLED, когда:

1. все тесты управления и кодеков проходят без регрессий;
2. WebUI остаётся доступным в client mode;
3. BOOT надёжно будит устройство;
4. измерения подтверждают снижение среднего потребления;
5. после 100 циклов Stop/Play отсутствует накопительная потеря RAM;
6. production-профиль не отличается от debug рабочей логикой;
7. отключение экспериментального compile-time флага полностью возвращает
   прежнее поведение.

