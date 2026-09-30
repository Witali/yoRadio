# Build and flash yoRadio on an ESP32-C3 OLED board: beginner's guide

This guide starts with a Windows computer that has no development tools installed.
It explains how to download the source, compile the firmware, install it on a
board for the first time, and update it later.

**Target board:** ESP32-C3 SuperMini / 01Space-style board with a 0.42-inch,
72x40 SSD1306 OLED and 4 MB flash. The firmware target is
`idf/esp32c3-oled-native`. Check your board before proceeding: display wiring
and audio hardware must match the [board documentation](ESP32-C3-0.42-OLED.md).

**Computer:** an x64 Windows 10 or Windows 11 PC with an Internet connection.
Allow roughly 10 GB or more of free disk space for sources, tools and builds.
Use a USB **data** cable; a charging-only cable cannot program the board.

## How to use the commands

Copy the commands inside each code block into the indicated terminal and press
Enter. Run the blocks in order and wait for each operation to finish. Do not copy
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

You do not need to install Python, Arduino IDE, PlatformIO, Visual Studio or
ESP-IDF separately. The project's setup script installs its own pinned tools.

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
files; the commands below compile and flash a new, real image.

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
script from `C:\yoRadio`:

```powershell
.\.agents\skills\flash-reset-esp32c3-oled\scripts\reset_esp32c3_oled.ps1 -Port $port
```

The script resets the ESP32-C3 without rewriting flash. It can find the Python
installed by setup. Follow the OLED and WebUI to confirm the application started;
a returned COM port alone does not prove that the radio is running. The reset
procedure is documented in the project's
[ESP32-C3 reset skill](../.agents/skills/flash-reset-esp32c3-oled/SKILL.md).

## 10. Enable the sleeping clock, if you built it

This section applies only when `DeepSleepClock = $true` was used during compilation.

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
