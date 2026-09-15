"""Compile and execute the real RTC wake stub with a bounded I2C/GPIO model.

Run with Python 3 and a host C compiler (CC, or cc) on Linux/WSL.
No board, ESP-IDF, or network is required.
"""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
headers = [
    "sdkconfig.h", "driver/gpio.h", "esp_rom_gpio.h", "esp_rom_sys.h",
    "esp_sleep.h", "esp_wake_stub.h", "hal/gpio_ll.h",
    "hal/rtc_timer_ll.h", "soc/gpio_sig_map.h", "soc/io_mux_reg.h",
]
with tempfile.TemporaryDirectory(prefix="yoradio-rtc-test-") as temporary:
    tmp = Path(temporary)
    for name in headers:
        header = tmp / name
        header.parent.mkdir(parents=True, exist_ok=True)
        header.write_text('#include "esp32c3_sleep_mock.h"\n')
    executable = tmp / "clock-test"
    subprocess.run([
        os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall", "-Wextra",
        "-Werror", "-I" + str(tmp), "-I" + str(root / "tests/native"),
        "-I" + str(root / "idf/esp32c3-oled-native/main"),
        str(root / "tests/native/esp32c3_deep_sleep_clock_test.c"),
        "-o", str(executable),
    ], check=True)
    subprocess.run([str(executable)], check=True)
