const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execute, hostPath, root} = require('../tools/esp8266_opus_profile/build_host.cjs');

test('bounded ICY title parser matches the previous whole-block parser under ASan/UBSan', t => {
  const main = path.join(root, 'idf/esp32c3-oled-native/main');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'esp32c3-icy-title-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  const executable = path.join(dir, 'test');
  execute('gcc', ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
    '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-pie', '-no-pie',
    '-I' + hostPath(main), hostPath(path.join(main, 'icy_title.c')),
    hostPath(path.join(__dirname, 'native/esp32c3_icy_title_test.c')), '-o', hostPath(executable)]);
  const output = execute(hostPath(executable), []);
  assert.match(output, /ICY title differential PASS/);
  t.diagnostic(output.trim());
});
