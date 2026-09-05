const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..", "esp8266", "rtos-sdk-native", "main");
const read = (name) =>
  fs.readFileSync(path.join(root, name), "utf8").replace(/\r\n/g, "\n");
const output = read("native_audio_output.c");
const nodac = read("esp8266_nodac_i2s.c");
const nodacHeader = read("esp8266_nodac_i2s.h");
const kconfig = read("Kconfig.projbuild");
const component = read("CMakeLists.txt");
const board = read("board_config.h");
const pdm = read("spi_pdm_config.h");
const app = read("app_main.c");
const audio = read("audio_service.c");
const defaultProfile = fs.readFileSync(
  path.resolve(root, "..", "sdkconfig.defaults"),
  "utf8",
);

const projectCmake = fs.readFileSync(
  path.resolve(root, "..", "CMakeLists.txt"),
  "utf8",
);

const i2sPdmStart = output.indexOf(
  "#elif YORADIO_ESP8266_I2S_PDM\n\n#define I2S_PDM_BATCH_WORDS",
);
const i2sPdm = output.slice(
  i2sPdmStart,
  output.indexOf(
    "\n#else\n\nesp_err_t native_audio_output_init(void) {",
    i2sPdmStart,
  ),
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
  assert.match(defaultProfile, /CONFIG_ESPTOOLPY_FLASHMODE_QIO=y/);
  assert.match(defaultProfile, /CONFIG_ESPTOOLPY_FLASHFREQ_40M=y/);
  assert.match(defaultProfile, /CONFIG_ESP_MAIN_TASK_STACK_SIZE=3072/);
  assert.doesNotMatch(board, /BOARD_TASK_STACK_INPUT/);
  assert.match(app, /input_service_poll\(\)[\s\S]*ulTaskNotifyTake\(pdTRUE, wait\)/);
  assert.match(defaultProfile, /CONFIG_YORADIO_MP3_DECODER_LIBMAD=n/);
  assert.match(defaultProfile, /CONFIG_YORADIO_HELIX_MP3_SSO=y/);
  assert.match(defaultProfile, /CONFIG_YORADIO_HELIX_AAC=y/);
  assert.match(defaultProfile, /CONFIG_YORADIO_HELIX_AAC_SSO=n/);
  assert.match(defaultProfile, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PDM=y/);
  assert.match(defaultProfile, /CONFIG_YORADIO_AUDIO_OUTPUT_SPI_PDM=n/);
  assert.match(defaultProfile, /CONFIG_YORADIO_AUDIO_OUTPUT_I2S_PCM=n/);
  assert.match(defaultProfile, /CONFIG_YORADIO_SPI_PDM_OVERSAMPLE_8=y/);
  assert.match(defaultProfile, /CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32=y/);
});

test("ESP8266 keeps mutable sdkconfig inside each build directory", () => {
  assert.match(projectCmake, /if\(NOT DEFINED SDKCONFIG\)/);
  assert.match(
    projectCmake,
    /set\(SDKCONFIG "\$\{CMAKE_BINARY_DIR\}\/sdkconfig" CACHE FILEPATH/,
  );
  assert.match(projectCmake, /file\(WRITE "\$\{SDKCONFIG\}" ""\)/);
});

test("I2S PDM submits only complete finite DMA buffers with neutral underrun fallback", () => {
  assert.match(i2sPdm, /I2S_PDM_SILENCE_WORD 0xaaaaaaaaU/);
  assert.match(
    i2sPdm,
    /esp8266_nodac_i2s_init\([\s\S]*I2S_PDM_SILENCE_WORD,[\s\S]*BOARD_I2S_PDM_BCK_DIV,[\s\S]*BOARD_I2S_PDM_CLKM_DIV/,
  );
  assert.match(i2sPdm, /esp8266_nodac_i2s_write/);
  assert.match(i2sPdm, /I2S_PDM_WRITE_TIMEOUT_MS 100U/);
  assert.match(i2sPdm, /TickType_t deadline/);
  assert.match(i2sPdm, /writer->deadline - now/);
  assert.doesNotMatch(i2sPdm, /pdMS_TO_TICKS\(I2S_PDM_WRITE_TIMEOUT_MS\)\);[\s\S]*esp8266_nodac_i2s_write/);
  assert.doesNotMatch(i2sPdm, /i2s_driver_install|\bi2s_write\(/);
  assert.match(nodacHeader, /ESP8266_NODAC_DMA_BUFFER_COUNT 2U/);
  assert.match(nodacHeader, /ESP8266_NODAC_DMA_BUFFER_WORDS 512U/);
  assert.match(nodacHeader, /producer\/DMA ping-pong/);
  assert.match(nodac, /NODAC_DMA_BUFFER_COUNT ESP8266_NODAC_DMA_BUFFER_COUNT/);
  assert.match(nodac, /NODAC_DMA_BUFFER_WORDS ESP8266_NODAC_DMA_BUFFER_WORDS/);
  assert.match(nodac, /SLC0\.rx_link\.start = 1/);
  assert.match(nodac, /SLC0\.tx_link\.start = 1/);
  assert.match(nodac, /SLC0\.int_ena\.rx_eof = 1/);
  assert.match(nodac, /SLC0\.int_ena\.rx_dscr_err = 0/);
  assert.match(nodac, /rom_i2c_writeReg_Mask\(0x67, 4, 4, 7, 7, 1\)/);
  assert.match(nodac, /I2S0\.conf\.bck_div_num = bck_div/);
  assert.match(nodac, /I2S0\.conf\.clkm_div_num = clkm_div/);
  assert.match(nodac, /finished->buf_ptr\[word\] = s_silence_word/);
  assert.match(nodac, /~\(3U << 12\).*\(1U << 12\)/);
  assert.match(nodac, /vTaskNotifyGiveFromISR/);
  assert.match(
    nodac,
    /ulTaskNotifyTake\([\s\S]*pdTRUE, ticks_to_wait - elapsed\)/,
  );
  assert.doesNotMatch(
    nodac,
    /NODAC_QUEUE_RECHECK_TICKS|xQueueCreate|xQueueReceive/,
  );
  assert.match(nodac, /descriptor->next_link_ptr = NULL/);
  assert.match(nodac, /if \(nodac_state_eof\(&s_state\)\)[\s\S]*finished->buf_ptr\[word\] = s_silence_word/);
  assert.match(nodac, /s_current_position == NODAC_DMA_BUFFER_WORDS[\s\S]*nodac_state_publish/);
  assert.doesNotMatch(nodac, /s_free_buffers|pop_free_buffer/);
  const silence = nodac.slice(nodac.indexOf('void esp8266_nodac_i2s_silence('), nodac.indexOf('void esp8266_nodac_i2s_reset_underruns('));
  assert.match(silence, /nodac_state_silence/);
  assert.doesNotMatch(silence, /s_buffers\[|memcpy|memset/);
  assert.match(output, /esp8266_nodac_i2s_reset_underruns/);
  assert.match(output, /stats->queue_empty_events = esp8266_nodac_i2s_underruns\(\)/);
});

test("I2S PDM defaults to a genuine 1.536 MHz PDM32 carrier", () => {
  assert.match(output, /static uint32_t s_i2s_pdm_partial_word/);
  assert.match(i2sPdm, /s_i2s_pdm_partial_bits != 32U/);
  assert.match(i2sPdm, /return i2s_pdm_flush\(&writer\);/);
  assert.match(pdm, /CONFIG_YORADIO_I2S_PDM_OVERSAMPLE_32[\s\S]*BOARD_I2S_PDM_OVERSAMPLE 32U[\s\S]*BOARD_I2S_PDM_CARRIER_BITS_PER_SAMPLE 32U/);
  assert.match(pdm, /BOARD_I2S_PDM_REPEAT/);
  assert.match(pdm, /BOARD_I2S_PDM_BCK_DIV 8U/);
  assert.match(pdm, /BOARD_I2S_PDM_CLKM_DIV 13U/);
  assert.match(pdm, /BOARD_I2S_PDM_NOMINAL_HZ/);
  assert.match(pdm, /160000000U \/ BOARD_I2S_PDM_BCK_DIV \/ BOARD_I2S_PDM_CLKM_DIV/);
  assert.match(i2sPdm, /bit < BOARD_I2S_PDM_OVERSAMPLE/);
  assert.match(i2sPdm, /repeat < BOARD_I2S_PDM_REPEAT/);
  assert.match(i2sPdm, /i2s_pdm_pack32/);
  assert.doesNotMatch(i2sPdm, /IRAM_ATTR[^\n]*[\r\n]+i2s_pdm_pack32/);
  assert.match(i2sPdm, /integrator = sum & 0xffffU/);
  assert.match(i2sPdm, /word = \(word << 1\) \| \(sum >> 16\)/);
  assert.match(i2sPdm, /PDM32_STEP\(\); PDM32_STEP\(\);/);
});

test("optimized branchless PDM32 packer is bit-exact", () => {
  const samples = [-32768, -30000, -1, 0, 1, 1234, 30000, 32767];
  let oldIntegrator = 0;
  let newIntegrator = 0;
  for (let pass = 0; pass < 32; ++pass) {
    for (const sample of samples) {
      const target = sample + 32768;
      let oldWord = 0;
      let newWord = 0;
      for (let bit = 0; bit < 32; ++bit) {
        oldIntegrator += target;
        const high = oldIntegrator >= 65536 ? 1 : 0;
        if (high) oldIntegrator -= 65536;
        oldWord = ((oldWord << 1) | high) >>> 0;

        const sum = newIntegrator + target;
        newIntegrator = sum & 0xffff;
        newWord = ((newWord << 1) | (sum >>> 16)) >>> 0;
      }
      assert.equal(newWord, oldWord);
      assert.equal(newIntegrator, oldIntegrator);
    }
  }
});

test("I2S PDM drives its clocks like ESP8266Audio and ignores UART RX input", () => {
  assert.doesNotMatch(board, /UART_RX_ISOLATE_GPIO/);
  assert.match(
    nodac,
    /FUNC_I2SO_DATA[\s\S]*FUNC_I2SO_BCK[\s\S]*FUNC_I2SO_WS/,
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

test("I2S DMA is installed before Wi-Fi starts and then emits neutral PDM", () => {
  assert.match(
    app,
    /audio_service_init\(\)[\s\S]*native_audio_output_init\(\)[\s\S]*network_service_start\(\)/,
  );
  assert.doesNotMatch(app, /network_service_connected\(\)[\s\S]*native_audio_output_init/);
});

test("ESP8266 audio trace follows decoder PCM into the physical PDM DMA buffer", () => {
  assert.match(component, /option\(YORADIO_ESP8266_AUDIO_TRACE[\s\S]*OFF\)/);
  assert.doesNotMatch(defaultProfile, /YORADIO_ESP8266_AUDIO_TRACE/);
  assert.match(audio, /AUDIO_TRACE PCM cb=%u rate=%u ch=%u samples=%u/);
  assert.match(audio, /min=%d max=%d fnv=%08x first=/);
  assert.match(output, /AUDIO_TRACE OUTPUT-PCM cb=%u frames=%u/);
  assert.match(output, /trace_output_pcm\(samples, frames, channels\)/);
  assert.match(nodac, /memcpy\(s_current_buffer \+ s_current_position, words,[\s\S]*AUDIO_TRACE DMA-PDM/);
  assert.match(nodac, /ones=%u\/%u/);
  assert.match(nodac, /s_dma_trace_count < 4U/);
});
