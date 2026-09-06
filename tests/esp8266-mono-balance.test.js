const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const output = fs.readFileSync(path.join(__dirname, '../esp8266/rtos-sdk-native/main/native_audio_output.c'), 'utf8');

test('all ESP8266 native output backends ignore balance for mono PCM', () => {
  assert.equal((output.match(/left_balance = channels == 2 && s_balance < 0/g) || []).length, 3);
  assert.equal((output.match(/right_balance = channels == 2 && s_balance > 0/g) || []).length, 3);
});

test('runtime and restored balance use a signed lower bound', () => {
  assert.match(output, /^#define BALANCE_DENOMINATOR 16\s*$/m);
  for(const name of ['native_audio_output_reload_settings', 'native_audio_output_set_balance_runtime']) {
    const fn = output.slice(output.indexOf(`void ${name}(`));
    assert.match(fn, /< -BALANCE_DENOMINATOR/);
  }
});
