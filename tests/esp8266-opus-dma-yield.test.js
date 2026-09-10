const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {execute, hostPath} = require('../tools/esp8266_opus_profile/build_host.cjs');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');

test('actual DMA acquire distinguishes real tick waits, stale notifications and timeout', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'opus-dma-yield-'));
  try {
    const source = fs.readFileSync(path.join(main, 'esp8266_nodac_i2s.c'), 'utf8');
    const start = source.indexOf('static bool acquire_free_buffer(');
    const end = source.indexOf('\nesp_err_t esp8266_nodac_i2s_reserve(', start);
    assert.ok(start >= 0 && end > start);
    fs.writeFileSync(path.join(dir, 'acquire.inc'), source.slice(start, end));
    const program = `
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
#include "opus_dma_yield.h"
#include "nodac_buffer_state.h"
typedef uint32_t TickType_t;
typedef void *TaskHandle_t;
#define taskENTER_CRITICAL() ((void)0)
#define taskEXIT_CRITICAL() ((void)0)
#define pdTRUE 1
static uint32_t s_buffers[2][512];
static nodac_buffer_state_t s_state;
static uint32_t *s_current_buffer;
static unsigned s_current_position;
static bool s_waiting;
static TaskHandle_t s_waiter;
static uint32_t s_dma_wait_ticks, tick, calls, advance, notification;
static bool release_buffer;
static TickType_t xTaskGetTickCount(void) { return tick; }
static TaskHandle_t xTaskGetCurrentTaskHandle(void) { return (void *)1; }
static uint32_t ulTaskNotifyTake(int clear, TickType_t wait) {
  assert(clear == pdTRUE && wait > 0); ++calls; tick += advance;
  if (release_buffer) s_state.state[s_state.active ^ 1U] = NODAC_FREE;
  return notification;
}
#include "acquire.inc"
static void reset(void) {
  nodac_state_init(&s_state);
  s_state.state[s_state.active ^ 1U] = NODAC_READY;
  s_current_buffer = NULL; s_current_position = 0;
  calls = advance = tick = s_dma_wait_ticks = 0;
  notification = 1; release_buffer = true;
}
int main(void) {
  reset(); s_state.state[s_state.active ^ 1U] = NODAC_FREE;
  assert(acquire_free_buffer(10)); assert(calls == 0 && s_dma_wait_ticks == 0);
  assert(opus_dma_needs_frame_delay(true, 0, s_dma_wait_ticks));
  reset(); advance = 3;
  assert(acquire_free_buffer(10)); assert(calls == 1 && s_dma_wait_ticks == 3);
  assert(!opus_dma_needs_frame_delay(true, 0, s_dma_wait_ticks));
  assert(opus_dma_needs_frame_delay(false, 0, s_dma_wait_ticks));
  // A later no-wait packet cannot reuse a previous packet's credit.
  assert(opus_dma_needs_frame_delay(true, s_dma_wait_ticks, s_dma_wait_ticks));
  reset(); // Stale/immediate notification: preserve the ordinary delay.
  assert(acquire_free_buffer(10)); assert(calls == 1 && s_dma_wait_ticks == 0);
  assert(opus_dma_needs_frame_delay(true, 0, s_dma_wait_ticks));
  reset(); release_buffer = false; notification = 0; advance = 10;
  assert(!acquire_free_buffer(10)); assert(!s_waiting && s_dma_wait_ticks == 0);
  reset(); assert(!acquire_free_buffer(0)); assert(calls == 0);
  reset(); tick = UINT32_MAX - 1; advance = 3;
  s_dma_wait_ticks = UINT32_MAX - 1;
  uint32_t before = s_dma_wait_ticks;
  assert(acquire_free_buffer(10)); assert(tick == 1 && s_dma_wait_ticks == 1);
  assert(!opus_dma_needs_frame_delay(true, before, s_dma_wait_ticks));
  puts("DMA yield wait and rollover tests passed");
}
`;
    const file = path.join(dir, 'test.c'), exe = path.join(dir, 'test');
    fs.writeFileSync(file, program);
    execute('cc', ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
      '-fsanitize=address,undefined', '-fno-pie', '-no-pie',
      '-DYORADIO_ESP8266_OPUS_DMA_YIELD=1', '-I' + hostPath(main),
      hostPath(file), '-o', hostPath(exe)]);
    assert.match(execute(hostPath(exe), []), /DMA yield wait and rollover tests passed/);
  } finally { fs.rmSync(dir, {recursive: true, force: true}); }
});

test('experiment is opt-in, measured per packet, and preserves legacy delay', () => {
  const audio = fs.readFileSync(path.join(main, 'audio_service.c'), 'utf8');
  assert.match(audio, /dma_wait_before = esp8266_nodac_i2s_wait_ticks\(\);\s*#endif\s*int decoded = helix_codec_process_one/);
  assert.match(audio, /opus_dma_needs_frame_delay\(codec_kind == HELIX_CODEC_OPUS,/);
  assert.match(audio, /\+\+s_frame_yield_skips;[\s\S]*?#else\s*vTaskDelay\(pdMS_TO_TICKS\(1\)\);/);
  const cmake = fs.readFileSync(path.join(main, 'CMakeLists.txt'), 'utf8');
  assert.match(cmake, /option\(YORADIO_ESP8266_OPUS_DMA_YIELD\s+"[^"]+" OFF\)/);
  assert.match(cmake, /YORADIO_ESP8266_OPUS_DMA_YIELD=\$<BOOL:/);
  const builder = fs.readFileSync(path.join(root, 'tools/esp8266_audio_profile/build_i2s_pdm_production.ps1'), 'utf8');
  assert.match(builder, /\$taskOpusDmaYield = if \(\$OpusDmaYield\) \{ 'ON' \} else \{ 'OFF' \}/);
  assert.match(builder, /"-DYORADIO_ESP8266_OPUS_DMA_YIELD=\$taskOpusDmaYield"/);
  assert.match(builder, /opus_dma_yield=\[bool\]\$OpusDmaYield/);
});
