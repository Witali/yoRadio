const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {execute, hostPath} = require('../tools/esp8266_opus_profile/build_host.cjs');

test('actual decoder fairness bounds expensive calls and rebases after a complete idle tick', () => {
  const root = path.resolve(__dirname, '..');
  const source = fs.readFileSync(path.join(root, 'idf/esp32-cyd2usb-native/main/audio_service.c'), 'utf8').replace(/\r\n/g, '\n');
  const start = source.indexOf('static void decoder_yield_if_due(');
  const end = source.indexOf('\n}\n', start);
  assert.ok(start >= 0 && end > start, 'Missing actual production helper');
  const helper = source.slice(start, end + 3);
  const build = path.join(root, '.build');
  fs.mkdirSync(build, {recursive: true});
  const dir = fs.mkdtempSync(path.join(build, 'decoder-fairness-'));
  assert.ok(fs.realpathSync(dir).startsWith(fs.realpathSync(build) + path.sep));
  try {
    const harness = path.join(dir, 'test.c');
    fs.writeFileSync(harness, `#include <assert.h>
#include <stdio.h>
#include "stream_fairness.h"
#ifdef NDEBUG
#error Assertions are required
#endif
static uint64_t now_us;
static unsigned waits;
static int64_t esp_timer_get_time(void) { return (int64_t)now_us; }
static void vTaskDelay(unsigned ticks) {
    assert(ticks == 2); /* A one-tick wait may end at the next tick edge. */
    ++waits;
    now_us += 1001; /* Deliberately not an integral slice or tick interval. */
}
${helper}
int main(void) {
    stream_fairness_t budget;
    stream_fairness_begin(&budget, now_us);
    for (unsigned i = 0; i < 99; ++i) {
        now_us += 200;
        decoder_yield_if_due(&budget);
        assert(waits == 0);
    }
    now_us = 20000;
    decoder_yield_if_due(&budget);
    assert(waits == 1 && budget.started_us == 21001);
    now_us = 41000;
    decoder_yield_if_due(&budget);
    assert(waits == 1);
    now_us = 41001;
    decoder_yield_if_due(&budget);
    assert(waits == 2 && budget.started_us == 42002);
    /* A single expensive frame must yield; waiting for 32 calls is unsafe. */
    now_us += 300000;
    decoder_yield_if_due(&budget);
    assert(waits == 3 && budget.started_us == now_us);
    decoder_yield_if_due(&budget);
    assert(waits == 3);
    /* An elapsed budget after a blocking read yields once and then rebases. */
    now_us += 1000000;
    decoder_yield_if_due(&budget);
    assert(waits == 4 && budget.started_us == now_us);
    puts("actual decoder fairness: 99 short calls, threshold/rebase/slow-call/blocking controls PASS");
    return 0;
}
`);
    const executable = path.join(dir, 'test');
    execute('gcc', ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
      '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-pie', '-no-pie',
      '-I' + hostPath(path.join(root, 'idf/components/native_stream/include')),
      hostPath(harness), '-o', hostPath(executable)]);
    const output = execute(hostPath(executable), []);
    assert.match(output, /controls PASS/);
  } finally {
    fs.rmSync(dir, {recursive: true, force: true});
  }
});
