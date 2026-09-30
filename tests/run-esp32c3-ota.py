"""Execute the production C3 OTA parser with fault-injected ESP-IDF flash APIs.

Use Python 3 and a C compiler on Linux/WSL. SDK checksum validation itself is
covered by real-device tests; the host model tests ownership and stream logic.
"""
import os
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory(prefix="yoradio-c3-ota-") as temporary:
    tmp = Path(temporary)
    for name in ("esp_ota_ops.h", "esp_app_format.h", "esp_image_format.h"):
        (tmp / name).write_text('#include "esp32c3_ota_mock.h"\n')
    for name in ("esp_http_server.h", "esp_err.h", "esp_system.h", "esp_timer.h",
                 "freertos/FreeRTOS.h", "freertos/semphr.h", "freertos/task.h"):
        header = tmp / name
        header.parent.mkdir(parents=True, exist_ok=True)
        header.write_text('#include "esp32c3_ota_http_mock.h"\n')
    for test in ("esp32c3_ota_test", "esp32c3_ota_http_test"):
        binary = tmp / test
        subprocess.run([
            os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall", "-Wextra",
            "-Werror", "-I" + str(tmp), "-I" + str(root / "tests/native"),
            "-I" + str(root / "idf/esp32c3-oled-native/main"),
            str(root / ("tests/native/" + test + ".c")), "-o", str(binary),
        ], check=True)
        subprocess.run([str(binary)], check=True)
