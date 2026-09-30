"""Execute production C3 callbacks, state and WebUI formatting on a host/WSL.

Only platform I/O is mocked. Extract complete production functions so the
callback-to-PCM tests exercise the firmware implementation, not a copied model.
"""
import os
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "idf/esp32c3-oled-native/main"


def function(source, name):
    match = re.search(r"^static [^\n]*\b" + name + r"\(", source, re.M)
    assert match, name
    start = source.index("{", match.start())
    depth = 1
    end = start + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[match.start():end] + "\n"


with tempfile.TemporaryDirectory(prefix="c3-stream-format-") as directory:
    tmp = Path(directory)
    (tmp / "freertos").mkdir()
    (tmp / "freertos/FreeRTOS.h").write_text("""#pragma once
#include <stddef.h>
typedef void *SemaphoreHandle_t;
#define pdTRUE 1
#define pdMS_TO_TICKS(x) (x)
#define portMAX_DELAY 0xffffffffU
static inline void *xSemaphoreCreateMutex(void) { return (void *)1; }
static inline int xSemaphoreTake(void *p, unsigned t) { (void)t; return !!p; }
static inline void xSemaphoreGive(void *p) { (void)p; }
size_t strlcpy(char *, const char *, size_t);
""")
    (tmp / "freertos/semphr.h").write_text('#include "FreeRTOS.h"\n')
    audio = (MAIN / "audio_service.c").read_text()
    web = (MAIN / "websocket_service.c").read_text()
    app = (MAIN / "app_main.c").read_text()
    types = audio[audio.index("typedef struct {\n    uint32_t generation;\n    uint32_t sample_rate;"):
                  audio.index("typedef struct {\n    int64_t started_us;")]
    callbacks = audio[audio.index("static bool update_stream_info("):
                      audio.index("static void decoder_task(")]
    ws_key = web[web.index("typedef struct {"):web.index("} webui_status_key_t;") + len("} webui_status_key_t;")]
    generated = types + ws_key + "\n" + "\n".join(
        function(audio, name) for name in ("codec_name", "decode_stats_add_audio", "send_pcm")
    ) + callbacks
    generated += "\n".join(function(web, name) for name in (
        "json_escape", "format_status", "capture_status_key"))
    generated += function(app, "format_stream_details")
    generated += function(app, "display_state_changed")
    # Execute the actual Espressif decoded-frame branch, including get_info,
    # stats and send_pcm; a single-iteration loop preserves its error break.
    start = audio.index("            if (frame.decoded_size) {")
    end = audio.index("            decode_stats_report(&stats", start)
    generated += """
static void run_espressif_frame(uint32_t generation, native_codec_t codec,
                               esp_audio_simple_dec_info_t *saved) {
    esp_audio_simple_dec_info_t stream_info = *saved;
    bool stream_info_ready = true;
    bool first_frame_memory_logged = true;
    void *decoder = NULL;
    void *aac_decoder = NULL;
    struct { size_t decoded_size; } frame = {4096};
    uint8_t output[4096] = {0};
    decode_stats_t stats = {0};
    do {
""" + audio[start:end] + """
    } while (false);
    *saved = stream_info;
}
"""
    (tmp / "production.inc").write_text(generated)
    executable = tmp / "stream-format"
    subprocess.run([
        os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall", "-Wextra",
        "-Werror", "-I" + str(tmp), "-I" + str(MAIN),
        "-I" + str(ROOT / "idf/components/custom_legacy_codecs"),
        "-I" + str(ROOT / "idf/esp32c3-oled-native/components/custom_flac"),
        str(ROOT / "tests/native/esp32c3_stream_format_test.c"),
        str(MAIN / "native_state.c"), "-o", str(executable),
    ], check=True)
    subprocess.run([str(executable)], check=True)
    executable = tmp / "pcm-workspace"
    subprocess.run([
        os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-I" + str(MAIN), str(ROOT / "tests/native/esp32c3_pcm_workspace_test.c"),
        "-o", str(executable),
    ], check=True)
    subprocess.run([str(executable)], check=True)
    # Run the shared adapter with the actual Helix AAC decoder as well.
    (tmp / "sdkconfig.h").write_text("")
    (tmp / "esp_log.h").write_text(
        "#define ESP_LOGI(...) ((void)0)\n#define ESP_LOGW(...) ((void)0)\n")
    (tmp / "esp_timer.h").write_text("""#pragma once
#include <stdint.h>
static inline int64_t esp_timer_get_time(void) { static int64_t t; return ++t; }
""")
    audio_dir = ROOT / "yoRadio/src/audioI2S"
    golden = ROOT / "tests/native/helix_golden"
    adapter = ROOT / "idf/components/custom_legacy_codecs"
    executable = tmp / "aac-adapter"
    subprocess.run([
        os.environ.get("CXX", "c++"), "-std=c++17", "-O2",
        "-DYORADIO_ESP8266_NATIVE=1", "-DCONFIG_YORADIO_AAC_DECODER_HELIX=1",
        *["-I" + str(path) for path in
          (tmp, golden, audio_dir, audio_dir / "aac_decoder", adapter)],
        str(ROOT / "tests/native/custom_legacy_stream_format_test.cpp"),
        str(adapter / "custom_legacy_adapter.cpp"),
        str(golden / "codec_arena_host.cpp"), "-o", str(executable),
    ], check=True)
    fixtures = ROOT / "tests/fixtures/helix_aac_blocks"
    he = ROOT / "tests/fixtures/aac_stream_format"
    subprocess.run([str(executable), str(fixtures / "stereo-44100.aac"),
                    str(fixtures / "mono-22050.aac"),
                    str(he / "he-44100-stereo.aac"),
                    str(he / "he-48000-stereo.aac"),
                    str(he / "hev2-44100-stereo.aac")], check=True)
    (tmp / "sdkconfig.h").write_text("#define CONFIG_YORADIO_AAC_PLUS 1\n")
    (tmp / "esp_audio_simple_dec.h").write_text("""#pragma once
#include <stdint.h>
#include <stdbool.h>
typedef int esp_audio_err_t;
typedef void *esp_audio_simple_dec_handle_t;
enum { ESP_AUDIO_ERR_OK=0, ESP_AUDIO_ERR_MEM_LACK=-2,
       ESP_AUDIO_ERR_INVALID_PARAMETER=-5, ESP_AUDIO_ERR_NOT_FOUND=-7,
       ESP_AUDIO_ERR_BUFF_NOT_ENOUGH=-8, ESP_AUDIO_SIMPLE_DEC_TYPE_AAC=1 };
typedef struct { int dec_type; void *dec_cfg; int cfg_size; bool use_frame_dec; } esp_audio_simple_dec_cfg_t;
typedef struct { uint8_t *buffer; uint32_t len; bool eos; uint32_t consumed; } esp_audio_simple_dec_raw_t;
typedef struct { uint8_t *buffer; uint32_t len, needed_size, decoded_size; } esp_audio_simple_dec_out_t;
typedef struct { uint32_t sample_rate; uint8_t bits_per_sample, channel; uint32_t bitrate, frame_size; } esp_audio_simple_dec_info_t;
esp_audio_err_t esp_audio_simple_dec_open(esp_audio_simple_dec_cfg_t *, void **);
void esp_audio_simple_dec_close(void *);
esp_audio_err_t esp_audio_simple_dec_process(void *, esp_audio_simple_dec_raw_t *, esp_audio_simple_dec_out_t *);
esp_audio_err_t esp_audio_simple_dec_get_info(void *, esp_audio_simple_dec_info_t *);
""")
    (tmp / "esp_aac_dec.h").write_text("""#pragma once
#include <stdbool.h>
typedef struct { bool aac_plus_enable; } esp_aac_dec_cfg_t;
#define ESP_AAC_DEC_CONFIG_DEFAULT() {false}
""")
    executable = tmp / "aac-framing"
    subprocess.run([
        os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-I" + str(tmp), "-I" + str(MAIN),
        str(ROOT / "tests/native/esp32c3_aac_framing_test.c"),
        str(MAIN / "native_aac_decoder.c"), "-o", str(executable),
    ], check=True)
    subprocess.run([str(executable)], check=True)
    executable = tmp / "aac-memory"
    subprocess.run([
        os.environ.get("CC", "cc"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-I" + str(tmp), "-I" + str(MAIN),
        str(ROOT / "tests/native/esp32c3_aac_memory_test.c"), "-o", str(executable),
    ], check=True)
    subprocess.run([str(executable)], check=True)
