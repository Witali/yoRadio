"""Compile the real board profile with conflicting and valid RTC pin mappings.

Run with Python 3 and a host C compiler (CC, or cc); no ESP-IDF is required.
"""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
board = root / "idf/esp32c3-oled-native/main"
base = {"RTC_CLK_SRC_EXT_CRYS": 1}
encoder = {"YORADIO_ROTARY_ENCODER": 1,
           "YORADIO_ROTARY_ENCODER_GPIO_A": 2,
           "YORADIO_ROTARY_ENCODER_GPIO_B": 4}
cases = [("crystal alone", base, True),
         ("remapped encoder", base | encoder, True),
         ("default LED", base | {"YORADIO_AUDIO_LEVEL_LED": 1,
                                 "YORADIO_AUDIO_LEVEL_LED_GPIO": 8}, True),
         ("RC with default encoder", {"RTC_CLK_SRC_INT_RC": 1} | encoder |
          {"YORADIO_ROTARY_ENCODER_GPIO_A": 0,
           "YORADIO_ROTARY_ENCODER_GPIO_B": 1}, True)]
for pin in (0, 1):
    for phase in ("A", "B"):
        cases.append((f"phase {phase} on GPIO{pin}", base | encoder |
                      {f"YORADIO_ROTARY_ENCODER_GPIO_{phase}": pin}, False))
    button = {"YORADIO_ROTARY_ENCODER_BUTTON": 1,
              "YORADIO_ROTARY_ENCODER_BUTTON_GPIO": pin}
    cases.append((f"button on GPIO{pin}", base | encoder | button, False))
    cases.append((f"disabled button on GPIO{pin}", base | encoder |
                  {"YORADIO_ROTARY_ENCODER_BUTTON_GPIO": pin}, True))
    cases.append((f"LED on GPIO{pin}", base |
                  {"YORADIO_AUDIO_LEVEL_LED": 1,
                   "YORADIO_AUDIO_LEVEL_LED_GPIO": pin}, False))
    cases.append((f"disabled LED on GPIO{pin}", base |
                  {"YORADIO_AUDIO_LEVEL_LED_GPIO": pin}, True))

with tempfile.TemporaryDirectory(prefix="yoradio-crystal-pins-") as temporary:
    tmp = Path(temporary)
    (tmp / "driver").mkdir()
    (tmp / "driver/gpio.h").write_text("")
    (tmp / "sdkconfig.h").write_text("")
    source = tmp / "board.c"
    source.write_text('#include "board_config.h"\nint main(void) { return 0; }\n')
    for name, config, expected_ok in cases:
        result = subprocess.run([
            os.environ.get("CC", "cc"), "-std=c11", "-fsyntax-only",
            "-I" + str(tmp), "-I" + str(board),
            *[f"-DCONFIG_{key}={value}" for key, value in config.items()],
            str(source),
        ], capture_output=True, text=True)
        assert (result.returncode == 0) == expected_ok, (name, result.stderr)
        if not expected_ok:
            assert "RTC 32k crystal reserves GPIO0 and GPIO1" in result.stderr
        print("PASS:", name)
print(f"PASS: {len(cases)} RTC crystal pin configurations")
