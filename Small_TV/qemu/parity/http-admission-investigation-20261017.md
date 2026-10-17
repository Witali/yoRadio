# Задержка до входа в HTTP-обработчик

Общий `upload-integrated-full-20261017` завершился ошибкой границы HTTP latency,
а не ошибкой сравнения календарных пикселей. Граница остаётся 6 guest seconds.
Ниже — отдельные диагностические наблюдения; новый общий pass не установлен.
Сводка измерений: [http-admission-observation-20261017.json](http-admission-observation-20261017.json).

## Прежнее исправление QEMU

Коммит `9d4da15732c44581aadced96fb71b9310bbee8b9` сохраняет C2 frame в bounded
очереди при отсутствии RX DMA descriptor. Запись RX_BASE_DESC пробуждает очередь.
Раньше потеря SYN вызывала повтор TCP примерно через шесть секунд. Коммит входит
в текущий QEMU `962cda7a6f58a3a7a71934239c3204c1483be8d4`; установленный executable
имеет SHA-256 `fde38d5311cf05b7c22e9ed114b2b57f22ce25f0f06d3f31b02bf519cc8d42eb`.
Повторены все восемь packet regressions, включая C2 starvation/FIFO/queue-limit:
они прошли. Отдельное firmware-ожидание погоды описано в
[software-weather-wait-checks.md](software-weather-wait-checks.md).

## Наблюдаемый путь и другие пользователи

| Участок | Функции и назначение | Что проверено |
| --- | --- | --- |
| Вход из SLIRP | `Esp32_WLAN_receive`, `.receive` в `NetClientInfo` | Обычный Ethernet, инкапсулированные ESP-NOW data и management replies направляются в общую очередь. Encapsulated ACK намеренно не передаётся в RX DMA; TCP по этой ветке не идёт. |
| Очередь | `Esp32_WLAN_insert_frame`, `Esp32_WLAN_inject_timer` | Другие источники — beacon/scan/auth/association и локальные DNS/NTP replies. Их кадры используют ту же bounded очередь. |
| RX DMA | `Esp32_sendFrame` | Единственный вызывающий участок находится в `Esp32_WLAN_inject_timer`; прямого обхода прежнего guard не найдено. |
| Пробуждение | `Esp32_WLAN_rx_ready` из записи RX_BASE_DESC | Отдельно изучен SDK `wDev_AppendRxBlocks`, включая RX_CTRL reload и NEXT/LAST; наличие этого второго механизма само по себе не доказывает сбой модели. |
| Обратная передача | `esp32c3_wifi_complete_tx`, `Esp32_WLAN_handle_frame`, `Esp32_WLAN_send_ethernet`, TX timer | Проверить SYN-ACK и завершение TCP отдельно от приёма SYN. |
| HTTP dispatch | `web_settings_post` | Зарегистрирован на 16 маршрутах. До входа в него уже должны пройти TCP handshake и разбор HTTP headers. |

Общие POST-маршруты: `/set_checkbox_state`, `/set_display_time`, `/wifireset`,
`/advancedset`, `/restart`, `/SetNightStopTime`, `/SetNightStartTime`,
`/set_night_brightness`, `/set_clock_color`, `/set_led_brightness`, `/updateCity`,
`/SetTimeModeValue`, `/settings`, `/setclocktype`, `/setgifvalue`, `/configure`.
Отдельный `web_settings_get` обслуживает 11 GET-маршрутов. Общая задержка до
dispatch способна затронуть все маршруты; это не доказательство дефекта каждой
из 16 ветвей обработчика.

## Новые измерения на неизменной сборке

Три отдельных диагностических прогона завершили по 180 синтетических POST.
В wire-прогоне `/settings` занял 5.813201 guest s; обработчик был вызван через
5.738763 s и выполнился за 0.000616 s. PCAP показывает первый SYN без SYN-ACK
и повтор SYN через 5.661505 s; затем HTTP прошёл быстро. В том же прогоне
максимальная длительность самого обработчика составила 0.010984 s.

Отдельный RX-trace прогон снова воспроизвёл задержку 5.697895 s. Dedicated
`esp32c3_wifi_rx_drop` был включён и не выдал событий. Это не позволяет приписать
нынешний случай прежней ветви `no-descriptor`. Неинструментированные причины
потерь, дальнейший гостевой путь и обратная передача ещё требуют локализации.
Корректные IPv4/TCP checksums и идентичные TCP bytes исходного и повторного SYN
проверены в wire PCAP. Сырые PCAP и debugger logs остаются в ignored `.build/`;
в Git сохранены только синтетические сводки и хеши.

Следующий замер наблюдает `esp_netif_receive`, `tcp_input`, `tcp_alloc` и HTTP
entry/return аппаратными breakpoints и bounded чтением compiled structures.
RAM, регистры, PC и инструкции гостя не подменяются. Первый вариант TCP observer
повторно останавливался на том же breakpoint и был остановлен; он помечен
`valid_diagnostic=false`, его данные не являются доказательством firmware-сбоя.
Исправленный observer естественно исполняет entry instruction до восстановления
точки останова. Не ослаблять HTTP gate и не менять firmware по неподтверждённой
гипотезе.
