# WebRadio

This is a separate Arduino-core firmware for a Wemos D1 mini. It is intended
as a direct, reproducible comparison with the native ESP8266 RTOS-SDK target;
it does not replace that production firmware.

The audio lifecycle follows the official ESP8266Audio examples:

- `AudioFileSourceICYStream` reads an HTTP/ICY radio stream;
- `AudioFileSourceBuffer` uses one preallocated 5 KiB input buffer;
- `AudioGeneratorMP3` or `AudioGeneratorAAC` uses one preallocated 29,192-byte
  mutually exclusive codec workspace;
- `AudioOutputI2SNoDAC` generates mono delta-sigma/PDM audio on GPIO3 through
  the same RC-filter connection used by the native firmware;
- decoder, buffer and source are released in that order when stopping or
  switching streams.

The target uses the standard `ESP8266WebServer` on port 80. In client mode it
provides a compact page and JSON API for URL selection, MP3/AAC selection,
volume, play and stop. A short BOOT/GPIO0 press toggles play/stop. If Wi-Fi
cannot connect within 15 seconds, the board starts the open
`WebRadio` setup access point; in AP mode only Wi-Fi setup is
available. Credentials, stream URL, codec and volume are stored in emulated
EEPROM. Only unencrypted HTTP/ICY streams are supported by this target.

## Reproducible build

The setup script uses an already installed `arduino-cli` when available.
Otherwise it downloads Arduino CLI 1.5.1 and verifies the official SHA-256.
Dependencies are kept outside the source tree in the common repository cache
`.build/dependencies/arduino-esp8266audio`. The deliberately short path avoids
a Windows path-length bug in the ESP8266 GCC 10 toolchain:

```powershell
.\esp8266\arduino-esp8266audio-webradio\build.ps1 -Setup -Clean
```

The build pins ESP8266 Arduino core 3.1.2 and ESP8266Audio 2.4.1 and selects
Wemos D1 mini, 160 MHz CPU, QIO flash at 40 MHz, 4 MiB flash and lwIP v2
high-bandwidth settings supplied by the board profile. A successful build is
copied to `firmware/development/web-radio/app.bin`.

## Upstream basis

- [ESP8266Audio WebRadio](https://github.com/earlephilhower/ESP8266Audio/tree/2.4.1/examples/WebRadio)
- [WebRadio.ino](https://github.com/earlephilhower/ESP8266Audio/blob/2.4.1/examples/WebRadio/WebRadio.ino)
- [StreamMP3FromHTTP](https://github.com/earlephilhower/ESP8266Audio/blob/2.4.1/examples/StreamMP3FromHTTP/StreamMP3FromHTTP.ino)
- [ESP8266Audio 2.4.1](https://github.com/earlephilhower/ESP8266Audio/tree/2.4.1)

The derived firmware and ESP8266Audio are GPL-3.0-or-later. See the repository
`LICENSE` and the upstream source headers.
