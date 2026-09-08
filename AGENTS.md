# Firmware artifacts

- Save every successful production firmware build intended for testing or
  hand-off under the repository''s `firmware/` directory. Do not leave the only
  copy in an ignored build directory.
- Save replaceable, unreleased builds under
  `firmware/development/<variant>/app.bin`.
- Save releases under `firmware/<version>/<variant>/` and never overwrite or
  remove an existing versioned release.

# ESP8266 deployment

- For the connected Wemos D1 mini with I2S audio on UART RX/GPIO3, use the
  native WebUI OTA endpoint for application updates by default.
- Do not automatically fall back to serial flashing or reset when OTA is
  unavailable. Ask the user before serial recovery while the audio circuit
  remains connected to RX. Never send UART application commands on GPIO3.
- Passive UART TX log capture is allowed without transmitting or asserting
  reset/boot control lines. See `esp8266/rtos-sdk-native/README.md` for OTA.

