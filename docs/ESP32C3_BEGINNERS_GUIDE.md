# Build and flash yoRadio on an ESP32-C3 OLED board: beginner's guide

This guide starts with a Windows computer that has no development tools installed.
It explains how to install a ready-made firmware image or compile the firmware
yourself, program a board for the first time, and update it later.

**Choose your route after steps 1 and 2:**

- **Install an existing binary:** follow [Prebuilt firmware: no compilation](#prebuilt-firmware-no-compilation).
  This uses Git, PowerShell, Python and esptool, without downloading a compiler or ESP-IDF.
- **Compile the latest source:** continue with [step 3](#3-install-the-firmware-toolchain).

Both routes include instructions for a new board and for updating an existing radio.

**Target board:** ESP32-C3 SuperMini / 01Space-style board with a 0.42-inch,
72x40 SSD1306 OLED and 4 MB flash. The firmware target is
`idf/esp32c3-oled-native`. Check your board before proceeding: display wiring
and audio hardware must match the [board documentation](ESP32-C3-0.42-OLED.md).

**Computer:** an x64 Windows 10 or Windows 11 PC with an Internet connection.
Allow roughly 10 GB or more of free disk space if you compile from source.
Installing a prebuilt image does not need the compiler/ESP-IDF downloads.
Use a USB **data** cable; a charging-only cable cannot program the board.

## How to use the commands

Copy the commands inside each code block into the indicated terminal and press
Enter. Follow the blocks for your chosen route and wait for each operation to
finish. Do not copy
the triple backticks around a block. If a command fails, resolve that error before
continuing. Lines starting with `#` are comments.

The examples use `C:\yoRadio`. Keep this short path to avoid problems with spaces
and long filenames. Building and flashing normally do not need an administrator
terminal; software installers may request administrator approval.

## 1. Install Git and PowerShell

### Install Git for Windows

1. Open the [official Git for Windows download page](https://git-scm.com/install/windows).
2. Download and run the **x64 installer**.
3. Keep the normal installer defaults. Enable **Git LFS** if offered, and use the
   PATH option that makes Git available from the command line and other software.
4. Complete the installation.

Git downloads the project. Git LFS handles the repository's archived binary files.
If Git LFS is unavailable after installing Git, install the Windows package from
[the official Git LFS site](https://git-lfs.com/).

### Install PowerShell 7

1. Open [Microsoft's PowerShell installation page](https://learn.microsoft.com/en-us/powershell/scripting/install/install-powershell-on-windows).
2. In **Install the MSI package**, download the current stable **win-x64.msi**.
3. Run the installer and keep the default options.
4. Close any terminals that were open before installation.
5. Open the Start menu, search for **PowerShell 7**, and open it.

Use **PowerShell 7.4 or newer**. The Windows PowerShell 5.1 application included
with Windows cannot run these build scripts correctly.

Check the installed tools:

```powershell
$PSVersionTable.PSVersion
git --version
git lfs version
```

The first command must show PowerShell 7.4 or newer. The other commands should
print version numbers. If Git is not recognized, close and reopen PowerShell 7.

For the source-build route, the project's setup script installs its own Python
and ESP-IDF tools. For the prebuilt route, install Python as described in that
section. Neither route needs Arduino IDE, PlatformIO or Visual Studio.

## 2. Download the latest source

Run this in PowerShell 7. The destination `C:\yoRadio` should not already contain
another project or an existing checkout.

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone -c core.longpaths=true --depth 1 --single-branch --branch main https://github.com/Witali/yoRadio.git C:\yoRadio
Remove-Item Env:GIT_LFS_SKIP_SMUDGE
```

If cloning succeeds, continue:

```powershell
Set-Location C:\yoRadio
git lfs install --local --skip-smudge
git log -1 --oneline
```

This downloads the latest `main` branch. The last command shows the source
revision you will build. Skipping Git LFS downloads avoids downloading archived
firmware for other boards; the ESP32-C3 build downloads its own required decoder
libraries during setup. Existing archive `.bin` files may be small LFS pointer
files. The prebuilt route below explicitly downloads the selected binaries with
Git LFS; the source-build route creates a new image locally.

## Prebuilt firmware: no compilation

### What to skip if you only flash firmware

**You do not need to compile anything. Skip steps 3, 4, 5, 8 and 11.**
Do not run `setup.ps1` or `build-production.ps1`: even the build script's flashing
commands compile an application first. You do not need ESP-IDF, the compiler,
CMake, Ninja, Arduino IDE, PlatformIO or Visual Studio.

| Main guide step | What to do when installing a prebuilt image |
| --- | --- |
| 1. Install Git and PowerShell | Do this once. Skip the installers if the version checks already pass. |
| 2. Download the source | Do this once to obtain the firmware manifests and helper scripts. If `C:\yoRadio` is already this repository on `main`, run `git pull --ff-only origin main` there instead of cloning again. Download the actual binaries in P3. |
| 3. Install the firmware toolchain | **Skip.** Install only Python and esptool in P2. |
| 4. Choose build options | **Skip.** Choose an already compiled variant in P1 instead. |
| 5. Compile | **Skip.** Download and check the selected binary in P3 instead. |
| 6 and 7. Programming mode and COM port | **Required.** Follow these when P4 directs you to them. |
| 8. Flash using the build script | **Skip.** Use P5 for a first installation or P6 for an update. |
| 9. Start the radio and configure Wi-Fi | Check startup after every flash. Configure Wi-Fi after a first installation; skip entering it again after P6 if the saved network still works. |
| 10. Enable the sleeping clock | Only needed for a `deep-sleep-clock` variant. Skip changing the settings if the Clock screensaver is already enabled. |
| 11. Rebuild for a later update | **Skip.** For another prebuilt update, repeat P3, P4 and P6. |

**First installation, in order:** steps 1 and 2 once, then P1, P2, P3, P4, **P5**,
and step 9. Also follow step 10 if you chose a sleeping-clock variant.

**Update an existing native radio:** choose the variant in P1, complete P2 only
if the flashing tools are missing, then follow P3, P4 and **P6**. Restart and
check the OLED/WebUI. Skip P5 to keep the existing Wi-Fi settings and playlist.
Do not skip the binary download/hash checks or programming-mode/COM-port checks.

### P1. Choose an available firmware variant

The following five **native ESP-IDF** variants use the board's stereo PDM audio
outputs (left GPIO10, right GPIO3) and the same native 4 MiB partition layout.
The directory name is the value to use for `$variant` in the commands below.

| Directory under `firmware/development/` | Features | Saved source | Files and details |
| --- | --- | --- | --- |
| `esp32c3-oled-native-production` | Ordinary radio; internal RTC oscillator; deep sleep off; logs off. | `eef49d1`, 2026-08-29 | `app.bin`, recovery `full.bin` and boot files. [Manifest](../firmware/development/esp32c3-oled-native-production/manifest.md). |
| `esp32c3-oled-native-development` | Ordinary radio with application diagnostic logs; internal RTC oscillator; deep sleep off. | `eef49d1`, 2026-08-29 | `app.bin`, recovery `full.bin` and boot files. [Manifest](../firmware/development/esp32c3-oled-native-development/manifest.md). |
| `esp32c3-oled-native-deep-sleep-clock` | Production radio with the sleeping clock; internal RTC oscillator; logs off. | `66626be7` | Application only. [Manifest](../firmware/development/esp32c3-oled-native-deep-sleep-clock/manifest.json). |
| `esp32c3-oled-native-production-rtc32k` | Production radio using an external 32.768 kHz crystal; deep sleep off; logs off. | `63572edf` | Application only. [Manifest](../firmware/development/esp32c3-oled-native-production-rtc32k/manifest.md). |
| `esp32c3-oled-native-deep-sleep-clock-rtc32k` | Production radio with both the sleeping clock and external crystal; logs off. | `63572edf` | Application only. [Manifest](../firmware/development/esp32c3-oled-native-deep-sleep-clock-rtc32k/manifest.md). |

These are **saved builds**, not automatically rebuilt copies of today's `main`.
The manifest identifies each image's source and validation. The sleeping-clock
and crystal images have build/host-test validation but are marked as not tested
on physical hardware. Compile from source if you need the newest code with your
own combination of options.

Choose `esp32c3-oled-native-production` for the archived ordinary radio, or choose
one of the other rows for its listed features. A prebuilt binary's features are
fixed: passing build switches to esptool cannot enable or disable them.

The `rtc32k` variants require the external crystal circuit on GPIO0/GPIO1.
See [crystal wiring](ESP32C3_RTC_32K_CRYSTAL.md); those pins cannot also serve the
encoder. The sleeping-clock variants need the WebUI Clock screensaver enabled
and synchronized time, as explained in step 10.

**Historical alternative:** [0.9.724 / esp32c3-oled-042-i2s](../firmware/0.9.724/esp32c3-oled-042-i2s/manifest.md)
is an Arduino firmware with external I2S audio (BCLK GPIO1, WS GPIO3, DIN GPIO10)
and a different SPIFFS partition at `0x370000`. It includes a `factory.bin` with
WebUI. It is not the current native PDM firmware; use its own manifest and wiring
instructions. Do not mix its application, filesystem or boot files with the
native installation commands below.

### P2. Install only the flashing tool

If you already completed this section on this PC, skip the installation below.
Restore the variable in a new terminal and check the tool:

```powershell
$flashPython = (Resolve-Path "C:\yoRadio\.build\flash-tools\Scripts\python.exe").Path
& $flashPython -m esptool version
```

If that reports esptool 5.3.1, continue to P3. Otherwise, install it:

1. Open the [official Python Windows downloads page](https://www.python.org/downloads/windows/).
2. Select a stable **Python 3.13 Windows installer (64-bit)**. Use the regular
   installer, with pip and the Python launcher enabled.
3. Finish installation, close PowerShell, and open PowerShell 7 again.
4. Run:

```powershell
Set-Location C:\yoRadio
py -3.13 --version
py -3.13 -m venv .build\flash-tools
$flashPython = (Resolve-Path ".build\flash-tools\Scripts\python.exe").Path
& $flashPython -m pip install "esptool==5.3.1"
& $flashPython -m esptool version
```

The final command should show esptool 5.3.1. This installs a small, separate
Python environment for flashing; no firmware compilation takes place. If `py`
is not recognized, check that the Python launcher was installed and reopen the
terminal. Keep this terminal open so `$flashPython` remains available.

### P3. Download the actual binary files and check them

Change the first line to one of the five native directory names in the table:

```powershell
$variant = "esp32c3-oled-native-production"
$firmware = Join-Path "C:\yoRadio\firmware\development" $variant
$installFiles = "C:\yoRadio\firmware\development\esp32c3-oled-native-installation"

Set-Location C:\yoRadio
git lfs pull --include="firmware/development/$variant/app.bin,firmware/development/esp32c3-oled-native-installation/*.bin" --exclude=""
if ($LASTEXITCODE -ne 0) { throw "Firmware download failed; do not flash." }
```

This works even though step 2 enabled `--skip-smudge`. It downloads only the
chosen application and the shared installation files. Do not save GitHub's HTML
file page as `.bin`, and do not flash a Git LFS pointer file.

Check the installation-file hashes automatically:

```powershell
$installManifest = Get-Content "$installFiles\manifest.json" -Raw | ConvertFrom-Json
foreach ($file in $installManifest.files) {
    $binaryPath = Join-Path $installFiles $file.file
    $actualHash = (Get-FileHash -LiteralPath $binaryPath -Algorithm SHA256).Hash
    if ($actualHash -ne $file.sha256) {
        throw "Wrong or incomplete download: $binaryPath"
    }
}

& $flashPython -m esptool --chip esp32c3 image-info "$firmware\app.bin"
if ($LASTEXITCODE -ne 0) { throw "Invalid application image; do not flash." }
Get-FileHash -LiteralPath "$firmware\app.bin" -Algorithm SHA256
```

`image-info` must report an ESP32-C3 application. Compare the final SHA-256 with
the selected variant's manifest linked in the table. If it differs, stop and
check the download. These checks do not connect to the board.

The [shared installation package](../firmware/development/esp32c3-oled-native-installation/manifest.md)
contains a production bootloader, the native partition table, an initial OTA
selector, and a ready-made SPIFFS image with WebUI and the repository playlist.
It contains no Wi-Fi credentials. Use your selected variant's `app.bin` with it.
The shared bootloader is quiet; the development application still provides its
own application logs.

Wi-Fi credentials entered during setup are saved on the board in
`/data/wifi.csv`. P6 deliberately preserves that file: a radio remembering your
network after an update does not mean its downloaded application contains your
credentials. A flash dump or a backup of the configured board's filesystem can
contain them.

### P4. Enter programming mode and select the port

Follow steps 6 and 7: hold BOOT, press and release RESET, release BOOT, then
identify the board's COM port. Set the actual port in this terminal:

```powershell
$port = "COM7"
```

COM7 is only an example. Close any serial monitor that is using that port.
**Choose either P5 or P6 below**, depending on whether this is a first installation
or an update. Do not run both procedures as routine steps.

### P5. First installation: application, boot files and WebUI

Use this for a new board or when installing the native partition layout.
It replaces the bootloader, partition table, OTA selector and SPIFFS. Existing
SPIFFS contents, including Wi-Fi credentials and playlists, are overwritten.
NVS is not erased by this command. Save any existing files you want to retain
before using this installation procedure.

```powershell
& $flashPython -m esptool --chip esp32c3 --port $port --baud 460800 --before usb-reset --after no-reset write-flash `
    --flash-mode dio --flash-freq 80m --flash-size 4MB `
    0x0 "$installFiles\bootloader.bin" `
    0x8000 "$installFiles\partitions.bin" `
    0xe000 "$installFiles\boot_app0.bin" `
    0x10000 "$firmware\app.bin" `
    0x3b0000 "$installFiles\spiffs.bin"
```

Wait until all writes and verification finish successfully. Release BOOT, then
press RESET, or unplug and reconnect USB without holding BOOT. The command uses
`--after no-reset` so the final restart is explicit. Continue with step 9 to
configure Wi-Fi. For a sleeping-clock image, also follow step 10.

The older production/development `full.bin` files are recovery images with an
empty SPIFFS region: they do not install the WebUI. The command above uses the
separate SPIFFS image as well. An `app.bin` alone cannot initialize a blank board.
Do not write `app.bin` at `0x0`; that address belongs to the bootloader.

### P6. Update an existing native radio: preserve settings and WebUI

Use this only when the board already has the native layout: application slot 0
at `0x10000`, application slot 1 at `0x1e0000`, and 256 KiB SPIFFS at `0x3b0000`.
If it runs the old Arduino firmware or an unknown layout, use P5 after backing
up its data.

```powershell
& $flashPython -m esptool --chip esp32c3 --port $port --baud 460800 --before usb-reset --after no-reset write-flash `
    --flash-mode dio --flash-freq 80m --flash-size 4MB `
    0xe000 "$installFiles\boot_app0.bin" `
    0x10000 "$firmware\app.bin"
```

This writes the selected application into slot 0 and resets the OTA boot selector
so slot 0 is used, including if an earlier OTA update selected slot 1. It preserves
NVS, Wi-Fi credentials, playlist and SPIFFS WebUI files. It also replaces the old
OTA selection/rollback state. Bootloader, partition table and filesystem are not
written. A WebUI update is a separate operation; P5 replaces the filesystem.

After successful writing and verification, restart with RESET without holding
BOOT. For connection/transfer errors, repeat programming mode and try `115200`
instead of `460800` in the same command.

If a manual restart leaves the board in its downloader, the project's reset
script can use this Python environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.agents\skills\flash-reset-esp32c3-oled\scripts\reset_esp32c3_oled.ps1 -Port $port -PythonPath $flashPython
```

The [reset skill](../.agents/skills/flash-reset-esp32c3-oled/SKILL.md) describes this
recovery method. Confirm startup on the OLED and through the WebUI. No serial
logs are expected from the production application variants.

For another prebuilt update later, run `git pull --ff-only origin main` in
`C:\yoRadio`, select the desired variant, and repeat P3, P4 and P6. If you reopened
PowerShell, set `$flashPython` to `(Resolve-Path "C:\yoRadio\.build\flash-tools\Scripts\python.exe").Path`
again. Pulling a newer Git revision does not imply that every archived binary
was rebuilt; check its manifest.

The command syntax follows [Espressif's esptool reference](https://docs.espressif.com/projects/esptool/en/latest/esp32c3/esptool/basic-commands.html).
The files and offsets were checked offline. These instructions and the shared
installation package have not been validated by flashing a physical board.

**The prebuilt route is complete here.** Use steps 6, 7, 9 and (when applicable)
10 only as directed above. Skip the source-build steps 3, 4, 5, 8 and 11 below.

## 3. Install the firmware toolchain

Allow local PowerShell scripts in this terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Confirm if prompted. This setting lasts only until this PowerShell window closes.
If a managed computer's policy blocks this setting, contact its administrator.

Install the dependencies:

```powershell
Set-Location C:\yoRadio
.\setup.ps1
```

Wait for setup to finish. The first run downloads several components and may take
a while, depending on your connection and computer. It installs:

- Python 3.12.10;
- ESP-IDF v6.0.2;
- the ESP32-C3 compiler, CMake, Ninja and flashing tools;
- the pinned Espressif audio decoder libraries.

Everything is stored in `C:\yoRadio\.idf`. A successful setup ends with a message
similar to `Native ESP32-C3 dependencies are ready in C:\yoRadio\.idf`.
Keep the same PowerShell window open for the following steps.

## 4. Choose the firmware options

Copy this block. These defaults build the ordinary radio, without deep sleep or
an external RTC crystal, which is a simple starting point for a new board:

```powershell
$buildOptions = @{
    DependencyRoot = "C:\yoRadio\.idf"
    FirmwareOutputDirectory = "firmware/development/local-esp32c3"
    DeepSleepClock = $false
    Rtc32kCrystal = $false
}
```

The last two lines are optional features:

| Option | Set to `$true` when... |
| --- | --- |
| `DeepSleepClock` | You want the stopped-radio clock to use deep sleep and update every 500 ms. |
| `Rtc32kCrystal` | You have installed a passive 32.768 kHz RTC crystal on GPIO0 and GPIO1, with the appropriate supporting circuit. |

For example, to enable the sleeping clock without an external crystal, change
`DeepSleepClock = $false` to `DeepSleepClock = $true` before running the block.
To use both features, set both values to `$true`.

For your first build, leave `Rtc32kCrystal` at `$false` unless you have connected
the crystal. GPIO0 and GPIO1 are also the default encoder pins; an encoder must
be disabled or moved to other suitable pins when using the crystal. See
[crystal wiring and build options](ESP32C3_RTC_32K_CRYSTAL.md).

`$buildOptions` stores your selections in the current terminal session. Reuse it
for both compilation and flashing. If you close the window, run this block again
with the same choices.

## 5. Compile the firmware

```powershell
.\idf\esp32c3-oled-native\build-production.ps1 @buildOptions
```

Compiling converts the source code into a program the ESP32-C3 can run. The first
build takes longer than subsequent builds. Wait for `Project build complete` and
a message saying that the production firmware was saved.

With the output setting above, your compiled application is saved here:

```text
C:\yoRadio\firmware\development\local-esp32c3\app.bin
```

The build also creates the bootloader, partition table and filesystem image needed
for a first installation. The flashing command below selects those files for you;
you do not need to enter memory addresses or assemble a combined binary.

This is the **production** profile: normal serial console logs are disabled.
The board can still be programmed through its USB bootloader.

## 6. Connect the board and enter programming mode

1. Connect the board to the PC with a USB data cable.
2. Close serial monitors or other programs that might be using the board.
3. Press and hold **BOOT**.
4. While holding BOOT, press and release **RST / RESET**.
5. Release BOOT and wait a few seconds.

If your board has BOOT but no reset button, disconnect USB, hold BOOT, reconnect
USB, then release BOOT after a few seconds.

The ESP32-C3 native USB Serial/JTAG interface supports direct flashing; a separate
USB-to-serial adapter is unnecessary for this board. See the
[Espressif USB connection guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/get-started/establish-serial-connection.html).

## 7. Find the COM port

In PowerShell:

```powershell
Get-CimInstance Win32_PnPEntity |
    Where-Object { $_.PNPDeviceID -like 'USB\VID_303A&PID_1001*' } |
    Select-Object Name, PNPDeviceID
```

Look for a name containing a port number, for example `USB Serial Device (COM7)`.
You can also open Windows **Device Manager**, expand **Ports (COM & LPT)**, and
look for the port that appears when you connect this board.

Set the variable below to **your actual port**. COM7 is only an example:

```powershell
$port = "COM7"
```

If several matching boards are connected, unplug the others while identifying
this board. If no port appears, try another data cable, another USB port, and
repeat the BOOT/RESET sequence. For driver-related errors shown by Device Manager,
consult the official Espressif connection guide linked above.

## 8. Flash the board for the first time

**Source-build route only.** If you are installing a prebuilt image, skip this
section and use P5 or P6 instead.

**First installation uses `flash`.** It writes the bootloader, partition table,
initial OTA selection, application and SPIFFS filesystem. SPIFFS contains the
WebUI and playlist. On a previously configured radio, this also replaces saved
Wi-Fi credentials and the playlist in SPIFFS; back those files up first if needed.

```powershell
.\idf\esp32c3-oled-native\build-production.ps1 @buildOptions -IdfArguments @("-p", $port, "-b", "460800", "flash")
```

Wait for writing and verification to finish. Keep the USB cable connected until
the command completes. The tool may reset the board automatically afterward.

If uploading fails because of communication errors, repeat the programming-mode
sequence and retry at a lower baud rate:

```powershell
.\idf\esp32c3-oled-native\build-production.ps1 @buildOptions -IdfArguments @("-p", $port, "-b", "115200", "flash")
```

## 9. Start the radio and configure Wi-Fi

1. Release BOOT completely.
2. Press and release RESET. If there is no reset button, unplug and reconnect USB
   without holding BOOT.
3. Check the OLED for the startup screen.
4. On a fresh installation without saved credentials, connect your phone or PC
   to the board's open Wi-Fi network named **yoRadio-XXXXXX**.
5. Stay connected even if the phone or PC says the network has no Internet.
6. Open **http://192.168.4.1/** in a browser. Use `http`, not `https`.
7. Enter the name and password of your **2.4 GHz Wi-Fi network**, then save.
8. The board restarts. Reconnect your phone or PC to your usual network, then
   open the radio's new IP address shown on its OLED or in your router's device list.

The native WebUI and AP behavior are described in the
[target README](../idf/esp32c3-oled-native/README.md#native-http-server-and-webui).
Audio playback also requires the correct external audio circuit described in the
[board hardware guide](ESP32-C3-0.42-OLED.md).

If the board stays in the bootloader after flashing, use the project's recovery
script from `C:\yoRadio`. Prebuilt users should use the command with
`-PythonPath $flashPython` in P6; the following command is for the source-build
route after running setup:

```powershell
.\.agents\skills\flash-reset-esp32c3-oled\scripts\reset_esp32c3_oled.ps1 -Port $port
```

The script resets the ESP32-C3 without rewriting flash. It can find the Python
installed by setup. Follow the OLED and WebUI to confirm the application started;
a returned COM port alone does not prove that the radio is running. The reset
procedure is documented in the project's
[ESP32-C3 reset skill](../.agents/skills/flash-reset-esp32c3-oled/SKILL.md).

## 10. Enable the sleeping clock, if your firmware includes it

This section applies when `DeepSleepClock = $true` was used during compilation,
or when you installed a prebuilt `deep-sleep-clock` variant.

1. In the WebUI, enable the screensaver for the stopped radio and select **Clock**.
2. Wait for the radio to synchronize its time over the network.
3. Stop playback and wait for the configured screensaver timeout.
4. The clock now updates every 500 ms while the CPU spends most of its time asleep.
5. To return to the station screen, hold BOOT for longer than 500 ms, release it,
   then press again to play.

Wi-Fi, WebUI and USB are unavailable during this sleep mode. A brief BOOT click
may be missed. USB disconnecting during deep sleep is expected behavior, as
explained in [Espressif's USB Serial/JTAG documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/usb-serial-jtag-console.html).
See [the project's deep-sleep instructions](ESP32C3_DEEP_SLEEP_CLOCK.md) for details.

## 11. Update the firmware later without replacing your settings

This section rebuilds from source. To install another existing binary without
compiling, use P3, P4 and P6 in the prebuilt section instead.

For later updates of this native firmware with the same partition layout, use
**`app-flash`**. It updates the application without writing NVS or SPIFFS, preserving
settings, Wi-Fi credentials, playlist and WebUI files. It does not update the
WebUI assets. If an update requires a partition or filesystem migration, follow
that release's instructions and back up your data first.

Open PowerShell 7 and run:

```powershell
Set-Location C:\yoRadio
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
git pull --ff-only origin main
```

If Git reports an error or local changes, resolve it before continuing; do not
force the update. Set your build options again, using the same desired values:

```powershell
$buildOptions = @{
    DependencyRoot = "C:\yoRadio\.idf"
    FirmwareOutputDirectory = "firmware/development/local-esp32c3"
    DeepSleepClock = $false
    Rtc32kCrystal = $false
}

.\idf\esp32c3-oled-native\build-production.ps1 @buildOptions
```

Enter programming mode and identify the port again as in steps 6 and 7. Its
number may have changed. Replace COM7 below with the current number:

```powershell
$port = "COM7"
.\idf\esp32c3-oled-native\build-production.ps1 @buildOptions -IdfArguments @("-p", $port, "-b", "460800", "app-flash")
```

Restart with RESET after successful flashing if necessary. Reuse the same
`$buildOptions` for every build/flash call: omitting a feature switch makes the
build script turn that feature off, even in a previously used configuration.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| `git` is not recognized | Complete the Git installation and open a new PowerShell 7 window. |
| `git lfs` is not recognized | Install Git LFS, reopen PowerShell, and check `git lfs version`. |
| `image-info` fails or a firmware hash differs | Repeat the targeted `git lfs pull` in P3; do not flash a pointer file or HTML download. |
| Scripts are disabled | Run the process-scoped execution-policy command from step 3 in the same terminal. |
| `Start-Process` does not accept `-Environment` | Use PowerShell 7.4 or newer. Check `$PSVersionTable.PSVersion`. |
| `$buildOptions` or `$port` is missing after reopening the terminal | Repeat the option block and set the current COM port. |
| No COM port is listed | Check the USB data cable and repeat BOOT/RESET. Examine Device Manager. |
| Port is busy or access is denied | Close the serial monitor/uploader that is using that COM port, then retry. |
| Flashing stays at `Connecting...` | Enter programming mode manually, verify the port, and retry. |
| Transfer fails partway through | Try a shorter data cable, a direct USB port, and `115200` baud. |
| Serial monitor is empty | Production builds disable logs. Check the OLED and WebUI instead. |
| WebUI and USB disappear when the clock is shown | With deep sleep enabled, hold BOOT for longer than 500 ms to wake the radio. |
| Compile error says GPIO0/1 are reserved for the RTC crystal | Disable conflicting encoder/LED options, move their pins, or disable the crystal option when that hardware is absent. |
| Setup or compilation fails | Keep the first error and the preceding lines. Do not flash an old file while assuming the new build succeeded. |

The commands were checked against the repository's native ESP32-C3 scripts and
pinned ESP-IDF v6.0.2 configuration. This guide has not been validated by a complete
installation on a freshly installed Windows PC or by flashing a board during its
preparation.
