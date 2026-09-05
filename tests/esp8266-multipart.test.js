const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const root = path.resolve(__dirname, '..');
test('streaming multipart handles every split and rejects truncated uploads', () => {
  const directory = fs.mkdtempSync(path.join(root, '.build/multipart-test-'));
  const wslPath = p => '/mnt/'+p[0].toLowerCase()+p.slice(2).replace(/\\/g, '/');
  const output = path.join(directory, 'test');
  const args = ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
    '-I'+wslPath(path.join(root, 'esp8266/rtos-sdk-native/main')),
    wslPath(path.join(__dirname, 'native/esp8266_multipart_test.c')), '-o', wslPath(output)];
  const build = spawnSync('wsl.exe', ['--exec', 'gcc', ...args], {encoding:'utf8'});
  assert.equal(build.status, 0, build.stdout+build.stderr);
  const run = spawnSync('wsl.exe', ['--exec', wslPath(output)], {encoding:'utf8'});
  assert.equal(run.status, 0, run.stdout+run.stderr);
  assert.match(run.stdout, /Streaming multipart tests passed/);
});
