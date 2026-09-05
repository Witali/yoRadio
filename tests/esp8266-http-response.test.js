const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const test = require('node:test');
const root = path.resolve(__dirname, '..');
test('actual HTTP response encoder coalesces chunks and keeps valid framing', () => {
  const src = fs.readFileSync(path.join(root,
    'esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_txrx.c'), 'utf8');
  const code = src.slice(src.indexOf('static esp_err_t httpd_send_headers('),
    src.indexOf('esp_err_t httpd_resp_send_404('));
  assert.ok(code.length > 1000);
  const fixture = fs.readFileSync(path.join(__dirname, 'native/esp8266_http_response_test.c'), 'utf8');
  const directory = fs.mkdtempSync(path.join(root, '.build/http-response-test-'));
  const source = path.join(directory, 'test.c'), binary = path.join(directory, 'test');
  fs.writeFileSync(source, fixture.replace('/* RESPONSE_IMPLEMENTATION */', code));
  const wsl = process.platform === 'win32';
  const platformPath = p => wsl ? '/mnt/'+p[0].toLowerCase()+p.slice(2).replace(/\\/g, '/') : p;
  const args = ['-std=c11','-Wall','-Wextra','-Werror',platformPath(source),'-o',platformPath(binary)];
  const build = spawnSync(wsl ? 'wsl.exe' : 'cc', wsl ? ['--exec','gcc',...args] : args, {encoding:'utf8'});
  assert.equal(build.status, 0, build.stdout+build.stderr);
  const run = spawnSync(wsl ? 'wsl.exe' : binary, wsl ? ['--exec',platformPath(binary)] : [], {encoding:'utf8'});
  assert.equal(run.status, 0, run.stdout+run.stderr);
  assert.match(run.stdout, /HTTP response framing passed/);
});
