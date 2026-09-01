const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "main");
const read = (name) => fs.readFileSync(path.join(root, name), "utf8");
const output = read("native_audio_output.c");
const kconfig = read("Kconfig.projbuild");
const component = read("CMakeLists.txt");
const board = read("board_config.h");
const pdm = read("spi_pdm_config.h");
const app = read("app_main.c");

const i2sPdmStart = output.lastIndexOf("#elif YORADIO_ESP8266_I2S_PDM");
const i2sPdm = output.slice(
  i2sPdmStart,
  output.indexOf("\n#else", i2sPdmStart),
);

test("ESP8266 production audio defaults to I2S DMA PDM", () => {
  assert.match(
    kconfig,
    /choice YORADIO_AUDIO_OUTPUT[\s\S]*default YORADIO_AUDIO_OUTPUT_I2S_PDM/,
  );
  assert.match(kconfig, /config YORADIO_AUDIO_OUTPUT_SPI_PDM/);
  assert.match(kconfig, /config YORADIO_AUDIO_OUTPUT_I2S_PCM/);
  assert.match(
    component,
    /elseif\(CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM\)[\s\S]*YORADIO_ESP8266_SPI_PDM=1/,
  );
  assert.match(
    component,
    /else\(\)[\s\S]*YORADIO_ESP8266_I2S_PDM=1/,
  );
});

test("I2S PDM uses circular SLC DMA with a continuous neutral bitstream", () => {
  assert.match(i2sPdm, /#define I2S_PDM_DMA_BUFFER_COUNT 4U/);
  assert.match(i2sPdm, /#define I2S_PDM_DMA_BUFFER_WORDS 128U/);
  assert.match(i2sPdm, /I2S_PDM_SILENCE_WORD 0xaaaaaaaaU/);
  assert.match(i2sPdm, /\.tx_desc_auto_clear = false/);
  assert.match(i2sPdm, /\.sample_rate = BOARD_I2S_PDM_FRAME_RATE/);
  assert.match(i2sPdm, /i2s_pdm_fill_dma_silence\(\)[\s\S]*i2s_set_pin/);
  assert.doesNotMatch(i2sPdm, /i2s_zero_dma_buffer/);
});

test("I2S PDM packs across decoder calls instead of padding every block", () => {
  assert.match(output, /static uint32_t s_i2s_pdm_partial_word/);
  assert.match(i2sPdm, /s_i2s_pdm_partial_bits != 32U/);
  assert.match(i2sPdm, /return i2s_pdm_flush\(&writer\);/);
  assert.match(pdm, /BOARD_I2S_PDM_FRAME_RATE \(BOARD_PDM_BIT_RATE_HZ \/ 32U\)/);
  assert.match(pdm, /BOARD_PDM_BIT_RATE_HZ 384615U/);
});

test("I2S PDM routes only DATA and ignores UART RX input", () => {
  assert.doesNotMatch(board, /UART_RX_ISOLATE_GPIO/);
  assert.match(
    i2sPdm,
    /\.bck_o_en = 0,[\s\S]*\.ws_o_en = 0,[\s\S]*\.data_out_en = 1/,
  );
  assert.doesNotMatch(i2sPdm, /gpio_set_level|gpio_set_direction/);
  assert.match(app, /I2S-PDM DMA GPIO[\s\S]*UART RX ignored/);

  const sources = fs
    .readdirSync(root)
    .filter((name) => name.endsWith(".c"))
    .map(read)
    .join("\n");
  assert.doesNotMatch(sources, /uart_read_bytes|uart_driver_install/);
});
