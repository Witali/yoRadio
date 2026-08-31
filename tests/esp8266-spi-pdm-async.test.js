const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "main");
const output = fs.readFileSync(path.join(root, "native_audio_output.c"), "utf8");
const component = fs.readFileSync(path.join(root, "CMakeLists.txt"), "utf8");
const board = fs.readFileSync(path.join(root, "board_config.h"), "utf8");
const input = fs.readFileSync(path.join(root, "input_service.c"), "utf8");
const radio = fs.readFileSync(path.join(root, "radio_control.c"), "utf8");
const network = fs.readFileSync(path.join(root, "network_service.c"), "utf8");

test("ESP8266 SPI-PDM drains a bounded queue from the transfer-done interrupt", () => {
  assert.match(output, /#define SPI_PDM_QUEUE_CHUNKS 12U/);
  assert.match(output, /\.intr_enable = \{\.trans_done = 1\}/);
  assert.match(output, /\.event_cb = spi_pdm_event/);
  assert.match(
    output,
    /IRAM_ATTR spi_pdm_event[\s\S]*SPI_TRANS_DONE_EVENT[\s\S]*spi_pdm_start_next_locked\(\)[\s\S]*vTaskNotifyGiveFromISR/,
  );
});

test("ESP8266 SPI-PDM producer sleeps only when its bounded queue is full", () => {
  assert.match(
    output,
    /s_spi_queue_count < SPI_PDM_QUEUE_CHUNKS[\s\S]*spi_pdm_start_next_locked\(\)/,
  );
  assert.match(output, /ulTaskNotifyTake\(pdTRUE,/);
  assert.doesNotMatch(output, /while \(SPI1\.cmd\.usr\)/);
  assert.doesNotMatch(output, /spi_trans\(HSPI_HOST/);
  assert.doesNotMatch(component, /--wrap=spi_trans/);
});

test("ESP8266 SPI-PDM drains queued sound before forcing silence", () => {
  assert.match(
    output,
    /void native_audio_output_silence\(void\)[\s\S]*spi_pdm_wait_idle\(\)[\s\S]*spi_pdm_send\(silence, SPI_PDM_CHUNK_BITS\)[\s\S]*spi_pdm_wait_idle\(\)/,
  );
});

test("ESP8266 input task has enough board-specific stack to open SPIFFS playlist", () => {
  assert.match(board, /#define BOARD_TASK_STACK_INPUT 3072/);
  assert.match(input, /xTaskCreate\(input_task, "input", BOARD_TASK_STACK_INPUT,/);
});
test("ESP8266 audio profile can auto-start a reproducible HTTP stream", () => {
  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE=1/);
  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE_URL/);
  assert.match(
    radio,
    /#ifdef YORADIO_ESP8266_AUDIO_PROFILE_URL[\s\S]*audio_service_play\([\s\S]*YORADIO_ESP8266_AUDIO_PROFILE_URL/,
  );
});
test("ESP8266 audio profile can use an explicit static IPv4 test network", () => {
  assert.match(component, /YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP/);
  assert.match(network, /#ifdef YORADIO_ESP8266_AUDIO_PROFILE_STATIC_IP/);
  assert.match(network, /tcpip_adapter_dhcpc_stop\(TCPIP_ADAPTER_IF_STA\)/);
  assert.match(network, /tcpip_adapter_set_ip_info/);
});