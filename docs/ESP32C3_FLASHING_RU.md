# Прошивка yoRadio на ESP32-C3 с OLED

Инструкция для ESP32-C3 SuperMini / 01Space с OLED 0,42″, SSD1306 72×40 и
4 МиБ flash. Состояние версий проверено 20 ноября 2026 года.

Для обычного использования выбирайте **`idf61-rawq-20261015` от 15 октября**.
Это последняя найденная сборка с полной приёмкой на физической ESP32-C3:
139 проверок и ещё 6 после установки прошли успешно. Более свежая сборка
от 17 ноября приведена отдельно: **на реальной плате она не тестировалась**.

Обе версии относятся к native ESP-IDF прошивке. OLED подключён к GPIO5/SDA
и GPIO6/SCL; стереозвук PDM — левый канал GPIO10, правый GPIO3.
Для звука нужны фильтры и усилитель по [схеме платы](ESP32-C3-0.42-OLED.md).
К GPIO нельзя подключать динамик или наушники напрямую. Это другой вариант
аппаратуры, чем историческая Arduino-прошивка с внешним I2S ЦАП.

## Какую версию скачать

| Версия | Файл приложения | Статус |
| --- | --- | --- |
| **15 октября 2026**, `idf61-rawq-20261015` | [Скачать app.bin](https://media.githubusercontent.com/media/Witali/yoRadio/2fcc3fda5192d32dd8c72878f9ce8633914ac134/firmware/development/esp32c3-idf61-raw-tail-quiet/app.bin), 1 474 288 байт | **Основной выбор.** Аппаратная приёмка, HTTP/HTTPS, AAC-LC/HE-AAC/HE-AAC v2/MP3/FLAC/Vorbis/Opus, восстановление и OTA прошли. [Отчёт](ESP32C3_PRODUCTION_ACCEPTANCE_20261015.md), [манифест](../firmware/development/esp32c3-idf61-raw-tail-quiet/manifest.json). |
| **17 ноября 2026**, `esp32c3-oled-native-transfer-20261117` | [Скачать app.bin](https://media.githubusercontent.com/media/Witali/yoRadio/2245311c51aed9cbc196f825df50ac26e4da95f6/firmware/development/esp32c3-oled-native-transfer-20261117/app.bin), 1 523 776 байт | **Для испытаний. На реальной плате не тестировалась.** Сборка, проверка образа, статический анализ и регрессии PCM прошли. Образ опубликован в ветке `codex/cyd-espressif-vorbis`. [Метаданные](https://github.com/Witali/yoRadio/blob/2245311c51aed9cbc196f825df50ac26e4da95f6/firmware/development/esp32c3-oled-native-transfer-20261117/app-metadata.json), [отчёт](https://github.com/Witali/yoRadio/blob/2245311c51aed9cbc196f825df50ac26e4da95f6/tests/results/cyd-production-refresh-20261117/README.md). |

Октябрьский образ использует ESP-IDF 6.1, QIO 80 МГц и выход с номинальной
частотой 48 кГц. Проверены в том числе десятиминутные воспроизведения.
Deep sleep выключен, логи отключены. Аппаратная приёмка относится к указанному
бинарному файлу: самостоятельная пересборка того же профиля не становится
автоматически проверенной версией.

Контрольные суммы SHA-256:

```text
15 октября:
90334aabe2d62cbec10b0686433eba43d8c79bd62c5c191db337dace5e571aeb

17 ноября:
73fe4110899f45cc5154960304ad10e4a6572b6f2c9f6e5b912de6524607ebe1
```

После скачивания проверьте файл в PowerShell, указав его настоящий путь:

```powershell
Get-Item -LiteralPath "C:\путь\к\app.bin" | Select-Object Length
Get-FileHash -LiteralPath "C:\путь\к\app.bin" -Algorithm SHA256
```

Размер и SHA-256 должны совпасть с выбранной версией. Маленький текстовый
Git LFS pointer или сохранённая HTML-страница GitHub не являются прошивкой.
Не продолжайте при несовпадении контрольной суммы.

## Обновление через WebUI

Если native yoRadio уже работает и в WebUI есть страница **Update**, достаточно
скачанного `app.bin` и браузера. Python, esptool и USB для этого не нужны.
Используется штатная native-разметка с двумя OTA-слотами по 1 900 544 байта;
перейти с Arduino или другой разметки этим способом нельзя.

1. Подключите компьютер или телефон к той же сети, что и радио. Откройте IP
   радио с OLED или из списка устройств роутера.
2. Откройте **Update**, либо адрес `http://IP_РАДИО/update.html`.
3. Выберите **firmware**, укажите проверенный `app.bin`, нажмите **Update**.
4. Дождитесь подтверждения проверки и автоматической перезагрузки.
   Во время обновления не отключайте питание. Достижение 100% в браузере
   означает окончание отправки, но сервер ещё должен принять образ.
5. Снова откройте WebUI. Для октябрьского образа версия должна быть
   **`idf61-rawq-20261015`**. Проверьте OLED, Play/Stop и звук.

OTA сохраняет Wi-Fi, настройки, плейлист и файлы WebUI. Оно обновляет приложение,
но не загрузчик, таблицу разделов или SPIFFS. Загружайте только `app.bin`
для native ESP32-C3 OLED, а не `full.bin`, `factory.bin` или образ CYD/ESP8266.

Состояние приложения можно проверить по `http://IP_РАДИО/api/native/ota`.
ELF SHA-256 принятой октябрьской версии:

```text
8d63aee7c134d8c994d254bb8bdea3a66ad33d552ad3ef4ba2426d99b4cbc2e5
```

Для испытания ноябрьской версии используйте её отдельный файл и SHA-256 из
таблицы. На чистую плату сначала установите октябрьский комплект по USB, затем
загрузите ноябрьское приложение через WebUI. Это не добавляет ему аппаратной
приёмки. Для возврата к принятой версии повторите OTA с октябрьским `app.bin`.
Если приложение не запускается, остаётся восстановление по USB.

## Подготовка к прошивке по USB

Ниже используются Windows 10/11, PowerShell 7, Git с Git LFS и Python 3.13
с pip и Python Launcher. Если инструментов нет, установите их с официальных
сайтов: [Git](https://git-scm.com/install/windows), [Git LFS](https://git-lfs.com/),
[PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows),
[Python](https://www.python.org/downloads/windows/).
Компилятор, ESP-IDF и Arduino IDE для готовых файлов не нужны.

В новом терминале PowerShell скачайте проект в свободный каталог `C:\yoRadio`:

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone -c core.longpaths=true --depth 1 --single-branch --branch main https://github.com/Witali/yoRadio.git C:\yoRadio
Remove-Item Env:GIT_LFS_SKIP_SMUDGE
if ($LASTEXITCODE -ne 0) { throw "Не удалось скачать проект." }
Set-Location C:\yoRadio
```

Если проект уже скачан, откройте его каталог вместо повторного клонирования.
Не заменяйте каталог с собственной работой. Установите esptool в отдельное
окружение и скачайте только нужные бинарные файлы:

```powershell
py -3.13 -m venv .build\flash-tools
if ($LASTEXITCODE -ne 0) { throw "Не удалось создать окружение Python." }
$flashPython = (Resolve-Path ".build\flash-tools\Scripts\python.exe").Path
& $flashPython -m pip install "esptool==5.3.1"
if ($LASTEXITCODE -ne 0) { throw "Не удалось установить esptool." }

$firmware = Join-Path (Get-Location) "firmware\development\esp32c3-idf61-raw-tail-quiet"
$installFiles = Join-Path (Get-Location) "firmware\development\esp32c3-oled-native-installation"
git lfs pull --include="firmware/development/esp32c3-idf61-raw-tail-quiet/*.bin,firmware/development/esp32c3-oled-native-installation/*.bin" --exclude=""
if ($LASTEXITCODE -ne 0) { throw "Не удалось скачать бинарные файлы." }
```

Проверьте контрольные суммы приложения, его загрузчика, таблицы разделов
и общего установочного комплекта:

```powershell
$variantManifest = Get-Content "$firmware\manifest.json" -Raw | ConvertFrom-Json
foreach ($name in @("app.bin", "bootloader.bin", "partition-table.bin")) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $firmware $name) -Algorithm SHA256).Hash
    if ($actualHash -ne $variantManifest.files.$name) {
        throw "Контрольная сумма не совпала: $name"
    }
}
if ($variantManifest.image.sha256 -ne "90334aabe2d62cbec10b0686433eba43d8c79bd62c5c191db337dace5e571aeb") {
    throw "Выбран другой образ, а не принятая октябрьская версия."
}
$installManifest = Get-Content "$installFiles\manifest.json" -Raw | ConvertFrom-Json
foreach ($file in $installManifest.files) {
    $actualHash = (Get-FileHash -LiteralPath (Join-Path $installFiles $file.file) -Algorithm SHA256).Hash
    if ($actualHash -ne $file.sha256) {
        throw "Контрольная сумма установочного файла не совпала: $($file.file)"
    }
}
& $flashPython -m esptool --chip esp32c3 image-info "$firmware\app.bin"
if ($LASTEXITCODE -ne 0) { throw "Образ приложения не прошёл проверку." }
```

Если появился текст ошибки, устраните её до прошивки.
Все дальнейшие блоки выполняются в этом же терминале, чтобы сохранить переменные.

Подключите плату USB-кабелем с передачей данных. Зажмите **BOOT**, нажмите
и отпустите **RESET**, затем отпустите **BOOT**. Если RESET отсутствует,
подключите USB с зажатой BOOT и затем отпустите её.
В диспетчере устройств найдите появившийся COM-порт Espressif USB Serial/JTAG;
для native USB его VID/PID — **303A:1001**. Укажите настоящий порт:

```powershell
$port = "COM7"
```

`COM7` — пример. Если подключено несколько одинаковых плат, оставьте только
нужную. Закройте её serial monitor и другие программы прошивки.

## Первая установка по USB

Выберите этот раздел для чистой платы или перехода с Arduino. Он заменяет
загрузчик, разметку, выбор OTA-слота и SPIFFS. **Сохранённые в SPIFFS Wi-Fi
и плейлист будут заменены** установочными файлами. Сначала сохраните нужные
данные. Область NVS этой командой не стирается.

```powershell
& $flashPython -m esptool --chip esp32c3 --port $port --baud 460800 --before usb-reset --after no-reset write-flash `
    --flash-mode dio --flash-freq 80m --flash-size 4MB `
    0x0 "$firmware\bootloader.bin" `
    0x8000 "$firmware\partition-table.bin" `
    0xe000 "$installFiles\boot_app0.bin" `
    0x10000 "$firmware\app.bin" `
    0x3b0000 "$installFiles\spiffs.bin"
if ($LASTEXITCODE -ne 0) { throw "Запись не завершена; проверьте ошибку esptool." }
```

Здесь `dio` соответствует команде записи ESP-IDF: ROM загружает bootloader
в DIO, а соответствующий ему загрузчик включает QIO. Для ESP32-C3 загрузчик
записывается в **`0x0`**, приложение — в **`0x10000`**. Не меняйте эти адреса.

Приёмка октябрьского приложения выполнена на работающей плате через OTA;
первая USB-установка именно этого комплекта отдельно проверена по файлам
и адресам, без нового аппаратного прогона на чистой плате.

## Обновление по USB с сохранением настроек

Используйте вместо предыдущего раздела, если на плате уже штатная native-разметка:
`app0` — `0x10000`, `app1` — `0x1e0000`, SPIFFS — `0x3b0000`, размер SPIFFS —
256 КиБ. Подготовка и проверки файлов остаются теми же.

```powershell
& $flashPython -m esptool --chip esp32c3 --port $port --baud 460800 --before usb-reset --after no-reset write-flash `
    --flash-mode dio --flash-freq 80m --flash-size 4MB `
    0xe000 "$installFiles\boot_app0.bin" `
    0x10000 "$firmware\app.bin"
if ($LASTEXITCODE -ne 0) { throw "Запись не завершена; проверьте ошибку esptool." }
```

Эта команда сохраняет NVS, Wi-Fi, плейлист и WebUI. Она записывает приложение
в `app0` и сбрасывает OTA-выбор на него. Это нужно, чтобы после предыдущих OTA
загрузчик не продолжил запускать старый `app1`. Таблица разделов и загрузчик
не заменяются. Не применяйте этот способ к Arduino или неизвестной разметке.

## Первый запуск и проверка

1. После успешной записи и проверки esptool отпустите BOOT. Нажмите RESET
   или переподключите USB, не удерживая BOOT.
2. При первой установке подключитесь к открытой сети **yoRadio-XXXXXX**.
   Сообщение телефона об отсутствии интернета ожидаемо.
3. Откройте **http://192.168.4.1/** и задайте вашу Wi-Fi сеть **2,4 ГГц**.
4. После перезагрузки вернитесь в обычную сеть и откройте адрес радио с OLED.
5. Проверьте версию, запуск станции, Play/Stop и сохранение плейлиста.

При обновлении с сохранением настроек повторно вводить Wi-Fi обычно не нужно.
Пустой serial monitor для production-сборки нормален: логи отключены.
Если COM-порт отсутствует, проверьте кабель и повторите BOOT/RESET. При ошибке
передачи попробуйте `--baud 115200` вместо `460800`. Если плата остаётся
в загрузчике, см. [восстановление ESP32-C3](ESP32C3_BEGINNERS_GUIDE.md#p6-update-an-existing-native-radio-preserve-settings-and-webui).

Подробные варианты сборки и старые образы описаны в
[полном руководстве](ESP32C3_BEGINNERS_GUIDE.md). Команды записи и режимы reset:
[официальная документация esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32c3/esptool/advanced-options.html).
